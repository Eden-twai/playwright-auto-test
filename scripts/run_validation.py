#!/usr/bin/env python3
"""AI Hub 分層驗證入口；預設僅執行一般回歸，不操作服務狀態。

放在專案根目錄的 scripts/ 下執行：
    python scripts/run_validation.py
    python scripts/run_validation.py --target tests/test_user_home.py::test_example
    python scripts/run_validation.py --manual-activation
    python scripts/run_validation.py --auto-login

--manual-activation 需要額外四個環境變數授權，並執行前、後各一輪一般回歸。
不會改動既有測試檔，亦不會自動設定寫入授權或重試旗標。
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
REGRESSION_FILES = (
    "tests/test_site_access.py",
    "tests/test_platform_manager.py",
    "tests/test_user_home.py",
)
GHERKIN_REGRESSION_FILES = (
    "tests/bdd/site_access_regression_steps.py",
    "tests/bdd/platform_manager_regression_steps.py",
    "tests/bdd/user_home_regression_steps.py",
)
GHERKIN_REGRESSION_FEATURES = tuple(
    path.removesuffix("_steps.py") + ".feature" for path in GHERKIN_REGRESSION_FILES
)
MANUAL_TARGETS = (
    "tests/manual_model_activation.py::test_model_activation_and_chat",
    "tests/manual_ai_application_activation.py::test_ai_app_activation",
)
GHERKIN_TARGETS = (
    "tests/bdd/model_chat_steps.py",
    "tests/bdd/ai_app_steps.py",
)
REQUIRED_MANUAL_ENV = {
    "MODEL_TEST_WRITE": "I_UNDERSTAND",
    "MODEL_TEST_ALLOW_DISABLE": "YES",
    "AI_APP_TEST_WRITE": "I_UNDERSTAND",
    "AI_APP_TEST_ALLOW_DISABLE": "YES",
}
AI_APP_ENTRY_TEST = "tests.test_user_home::test_ai_apps_can_be_opened_and_returned"
AI_APP_ENTRY_MISSING_REASON = "使用者介面沒有 AI 應用入口"

STAGES = (
    ("static", "Python 靜態語法檢查"),
    ("collection", "一般回歸測試收集與數量核對"),
    ("login", "本輪自動登入與登入狀態驗證"),
    ("targeted", "本次修改的指定測試"),
    ("regression_before", "46 項一般回歸"),
    ("manual_activation", "模型與 AI 應用完整啟停"),
    ("regression_after", "啟停後最終一般回歸"),
    ("logout", "本輪登出與登入狀態清理"),
)


def now_taipei() -> str:
    return datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")


def git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, text=True, capture_output=True, timeout=5,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def source_hashes() -> dict[str, str]:
    """版本證據，不讀取 .env、.auth、報表或登入憑證。"""
    result: dict[str, str] = {}
    for folder in ("pages", "tests", "scripts"):
        base = ROOT / folder
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix not in {".py", ".feature"}:
                continue
            if any(p in {".venv", "__pycache__", ".git"} for p in path.parts):
                continue
            result[path.relative_to(ROOT).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    for name in ("conftest.py", "pytest.ini", "requirements.txt"):
        path = ROOT / name
        if path.is_file():
            result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def parse_collection_count(output: str) -> int | None:
    matches = re.findall(r"\b(\d+)\s+tests?\s+collected\b", output)
    if matches:
        return int(matches[-1])
    matches = re.findall(r"\bcollected\s+(\d+)\s+items?\b", output)
    if matches:
        return int(matches[-1])
    return None


def parse_junit(path: Path) -> dict:
    """以 JUnit XML 為準，不由 stdout 字串推測 PASS。"""
    root = ET.parse(path).getroot()
    cases = list(root.iter("testcase"))
    counts = {"total": len(cases), "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    skip_reasons = []
    failed_cases = []
    passed_tests = []
    for case in cases:
        name = f"{case.get('classname', '')}::{case.get('name', '')}"
        if (issue := case.find("failure")) is not None:
            counts["failed"] += 1
            failed_cases.append({"test": name, "message": issue.get("message", "")})
        elif (issue := case.find("error")) is not None:
            counts["errors"] += 1
            failed_cases.append({"test": name, "message": issue.get("message", "")})
        elif (issue := case.find("skipped")) is not None:
            counts["skipped"] += 1
            skip_reasons.append({
                "test": name, "reason": issue.get("message") or (issue.text or "").strip()
            })
        else:
            counts["passed"] += 1
            passed_tests.append(name)
    return {**counts, "skip_reasons": skip_reasons, "failed_cases": failed_cases,
            "passed_tests": passed_tests}


def is_ai_app_entry_test(name: str) -> bool:
    return name.split("[", 1)[0] in {
        AI_APP_ENTRY_TEST,
        "tests.bdd.user_home_regression_steps::test_ai_apps_can_be_opened_and_returned",
    }


def regression_skip_policy(stage_id: str, counts: dict, max_skips: int) -> tuple[str, str]:
    """啟用前只豁免一項已知入口缺少的 Skip；啟用後入口必須實際通過。"""
    skips = counts["skip_reasons"]
    if any(not item["reason"].strip() for item in skips):
        return "有測試 Skip 缺少原因，需補充說明", ""
    if stage_id == "regression_after":
        if (any(is_ai_app_entry_test(item["test"]) for item in skips)
                or any(is_ai_app_entry_test(item["test"]) for item in counts["failed_cases"])
                or not any(is_ai_app_entry_test(name) for name in counts["passed_tests"])):
            return "啟停後 AI 應用入口測試必須通過，不能略過、失敗或缺少", ""
    expected_entry_skips = [
        item for item in skips
        if stage_id == "regression_before"
        and is_ai_app_entry_test(item["test"])
        and item["reason"].strip().startswith(AI_APP_ENTRY_MISSING_REASON)
    ]
    exempt = min(len(expected_entry_skips), 1)
    counted_skips = counts["skipped"] - exempt
    if counted_skips > max_skips:
        return (f"Skip {counts['skipped']} 項，其中啟用前入口缺少豁免 {exempt} 項；"
                f"其餘 {counted_skips} 項超過允許上限 {max_skips}，需確認新略過原因"), ""
    note = ("啟用前 AI 應用入口缺少：保留 1 項 Skip 紀錄，另行允許；"
            f"其餘 {counted_skips} 項 Skip 未超過上限 {max_skips}。"
            if exempt else "")
    return "", note


def missing_manual_permissions(env: dict[str, str]) -> list[str]:
    return [name for name, value in REQUIRED_MANUAL_ENV.items() if env.get(name) != value]


def validate_targets(targets: list[str]) -> list[str]:
    """只准指定既有一般回歸節點；不能繞過服務操作授權。"""
    errors = []
    for target in targets:
        source = target.split("::", 1)[0]
        if source not in REGRESSION_FILES or target.startswith("-"):
            errors.append(target)
    return errors


def run_command(command: list[str], log: Path, *, env=None) -> tuple[int, float, str]:
    log.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    with log.open("w", encoding="utf-8") as fp:
        try:
            process = subprocess.Popen(
                command, cwd=ROOT, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, bufsize=1, errors="replace",
                env=env,
            )
        except OSError as exc:
            message = str(exc)
            fp.write(message + "\n")
            return 127, time.monotonic() - start, message
        try:
            assert process.stdout is not None
            for line in process.stdout:
                fp.write(line)
                fp.flush()
                print(line, end="", flush=True)
            code = process.wait()
        except KeyboardInterrupt:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise
    return code, time.monotonic() - start, log.read_text(encoding="utf-8")


def markdown_summary(data: dict) -> str:
    lines = [
        "# AI Hub 驗證摘要",
        "",
        f"- 執行批次：`{data['run_id']}`",
        f"- 時間（Asia/Taipei）：{data['started_at']} 至 {data['finished_at'] or '執行中'}",
        f"- Git Commit：`{data['git_commit'] or '無法取得（不可視為已綁定版本）'}`",
        f"- Git 工作區：{data['git_status']}",
        f"- 整體狀態：**{data['overall']}**",
        f"- 預期一般回歸數量：{data['expected_regression_count']}",
        "- 模型對話送出：" + ("本輪要求，納入模型操作案例驗證" if data.get("chat_send_requested")
                             else "本輪未要求；僅驗證原有 Chat UI"),
        "",
        "| 階段 | 狀態 | 測試統計 / 原因 |",
        "|---|---|---|",
    ]
    for stage in data["stages"]:
        counts = stage.get("counts")
        detail = (
            f"{counts['passed']} passed, {counts['failed']} failed, "
            f"{counts['errors']} errors, {counts['skipped']} skipped"
            if counts else stage.get("reason", "—")
        )
        if stage.get("reason") and counts:
            detail += f"；{stage['reason']}"
        if stage.get("skip_policy_note"):
            detail += f"；{stage['skip_policy_note']}"
        lines.append(f"| {stage['label']} | {stage['status']} | {detail.replace('|', '/')} |")
    lines += ["", "## 略過原因（當次實測）", ""]
    has_skips = False
    for stage in data["stages"]:
        items = (stage.get("counts") or {}).get("skip_reasons", [])
        if not items:
            continue
        has_skips = True
        lines += [f"### {stage['label']}（{len(items)} 項）", ""]
        lines += [f"- `{item['test']}`：{item['reason']}" for item in items]
        lines.append("")
    if not has_skips:
        lines.append("無，或尚未產生實測結果。")
    lines += [
        "",
        "## 證據與判讀",
        "",
        f"- 本輪日誌：`reports/validation_runs/{data['run_id']}/`",
        "- `source_sha256`、Git 資訊與各階段命令／JUnit 數據見同批次 JSON。",
        "- 未執行、被阻擋與 pytest Skip 三者分開記錄；歷史測試成績不會自動帶入本輪。",
        "- HTML、Trace、Screenshot 可能含敏感頁面或登入資訊；分享前請檢查，勿提交公開儲存庫。",
        "",
    ]
    if data["warnings"]:
        lines += ["## 提醒", ""] + [f"- {w}" for w in data["warnings"]] + [""]
    return "\n".join(lines)


def write_summary(data: dict, run_dir: Path) -> None:
    """保留每輪歷史；根目錄兩份摘要永遠代表最近一次執行。"""
    data["finished_at"] = now_taipei() if data["overall"] != "RUNNING" else None
    base = ROOT / "reports"
    base.mkdir(exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    for path, content in (
        (base / "validation_summary.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n"),
        (base / "validation_summary.md", markdown_summary(data)),
        (run_dir / "validation_summary.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n"),
        (run_dir / "validation_summary.md", markdown_summary(data)),
    ):
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Hub 固定分層驗證；預設無服務寫入操作")
    parser.add_argument("--target", action="append", default=[], metavar="NODEID",
                        help="指定一般回歸中的單項測試，可重複給定")
    parser.add_argument("--manual-activation", action="store_true",
                        help="實際停用並重新啟用模型與 AI 應用（需額外四項授權）")
    parser.add_argument("--gherkin", action="store_true",
                        help="以 Gherkin 執行前後回歸及模型與 AI 應用操作，沿用整輪登入狀態")
    parser.add_argument("--auto-login", action="store_true",
                        help="自動登入後跑測試，整輪結束或失敗時嘗試登出")
    parser.add_argument("--chat-send", action="store_true",
                        help="模型啟用後送出一則訊息並驗證回覆與歷史；需 --manual-activation")
    parser.add_argument("--auth-browser", choices=("chromium", "firefox", "webkit"),
                        default="chromium", help="登入與登出視窗使用的瀏覽器，預設 chromium")
    parser.add_argument("--auth-browser-channel", choices=("chrome", "msedge"),
                        help="登入與登出改用已安裝 Chrome/Edge，需搭配 chromium")
    parser.add_argument("--expected-regression-count", type=int, default=46,
                        help="一般回歸收集數量閘門，預設 46")
    parser.add_argument("--max-regression-skips", type=int, default=5,
                        help="一般回歸 Skip 上限，預設 5；啟用前另允許 1 項已知 AI 應用入口缺少，啟用後入口必須通過")
    args = parser.parse_args(argv)
    regression_files = GHERKIN_REGRESSION_FILES if args.gherkin else REGRESSION_FILES
    if args.gherkin and not (args.auto_login and args.manual_activation and args.chat_send):
        parser.error("--gherkin 必須搭配 --auto-login --manual-activation --chat-send")
    if args.chat_send and not args.manual_activation:
        parser.error("--chat-send 必須搭配 --manual-activation")
    if args.auth_browser_channel and args.auth_browser != "chromium":
        parser.error("auth-browser-channel 必須搭配 chromium")
    if args.expected_regression_count < 1:
        parser.error("expected-regression-count 必須大於零")
    if not 0 <= args.max_regression_skips <= args.expected_regression_count:
        parser.error("max-regression-skips 必須介於 0 與預期案例數之間")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    run_id = f"{stamp}_{os.getpid()}"
    run_dir = ROOT / "reports" / "validation_runs" / run_id
    commit = git_value("rev-parse", "HEAD")
    porcelain = git_value("status", "--porcelain")
    data = {
        "schema_version": 1,
        "run_id": run_id,
        "started_at": now_taipei(),
        "finished_at": None,
        "overall": "RUNNING",
        "mode": ("gherkin" if args.gherkin else
                 "manual_activation" if args.manual_activation else "regression_only"),
        "auto_login": args.auto_login,
        "chat_send_requested": args.chat_send,
        "expected_regression_count": args.expected_regression_count,
        "max_regression_skips": args.max_regression_skips,
        "git_commit": commit,
        "git_status": (
            "無 Git 專案或無法查詢" if porcelain is None
            else "乾淨" if porcelain == "" else "有未提交修改"
        ),
        "source_sha256": source_hashes(),
        "warnings": ([] if commit else ["無法取得 Git Commit；本批次仍有檔案 SHA256 可追溯。"]),
        "stages": [
            {"id": key, "label": label, "status": "NOT_RUN", "reason": "尚未執行"}
            for key, label in STAGES
        ],
    }
    stages = {stage["id"]: stage for stage in data["stages"]}
    auth = None
    auth_module = None
    child_env = None

    def auth_action(stage_id, action):
        """記錄安全的進度；不輸出 Playwright 原始例外或帳密。"""
        log = run_dir / f"{stage_id}.log"
        update(stage_id, "RUNNING", log=str(log.relative_to(ROOT)))
        terminal = sys.stdout

        class Tee:
            def write(self, value):
                terminal.write(value)
                fp.write(value)
                return len(value)

            def flush(self):
                terminal.flush()
                fp.flush()

        start = time.monotonic()
        with log.open("w", encoding="utf-8") as fp:
            try:
                with redirect_stdout(Tee()):
                    detail = action()
            except KeyboardInterrupt:
                update(stage_id, "INTERRUPTED", "使用者中止執行")
                raise
            except Exception as exc:
                # 只有我們自己的安全步驟例外可以顯示文字。
                reason = (str(exc) if auth_module is not None
                          and isinstance(exc, auth_module.AuthStepError)
                          else "登入／登出或狀態檔操作失敗；請檢查設定、瀏覽器與畫面")
                fp.write(reason + "\n")
                update(stage_id, "FAIL", reason,
                       duration_seconds=round(time.monotonic() - start, 2))
                return False
        update(stage_id, "PASS", detail or "自動登入與本輪狀態重用驗證通過",
               duration_seconds=round(time.monotonic() - start, 2))
        return True

    def update(stage_id: str, status: str, reason: str = "", **extra) -> None:
        stage = stages[stage_id]
        stage.update(status=status, reason=reason, **extra)
        write_summary(data, run_dir)
        print(f"[{stage_id}] {status} {reason}", flush=True)

    def stop(overall: str, reason: str, code: int) -> int:
        """提前停止時仍為所有未執行關卡寫明原因，不留下含糊的狀態。"""
        for stage in data["stages"]:
            if stage["status"] != "NOT_RUN":
                continue
            if stage["id"] == "logout" and auth is not None:
                continue  # 交由 finally 真正執行，不能先標成 BLOCKED。
            optional = (
                (stage["id"] == "targeted" and not args.target)
                or (stage["id"] in {"login", "logout"} and not args.auto_login)
                or (stage["id"] in {"manual_activation", "regression_after"}
                    and not args.manual_activation)
            )
            stage.update(
                status="NOT_REQUESTED" if optional else "BLOCKED",
                reason="本次未要求執行" if optional else f"前置關卡中止：{reason}",
            )
        data["overall"] = overall
        write_summary(data, run_dir)
        return code

    def execute(stage_id: str, command: list[str], count_expected: int | None = None,
                *, require_no_skips: bool = False) -> bool:
        log = run_dir / f"{stage_id}.log"
        xml = run_dir / f"{stage_id}.xml"
        if "--junitxml" not in command:
            command += ["--junitxml", str(xml)]
        update(stage_id, "RUNNING", command=command, log=str(log.relative_to(ROOT)))
        code, duration, stdout = run_command(command, log, env=child_env)
        counts = None
        reason = ""
        skip_policy_reason = ""
        skip_policy_note = ""
        if xml.exists():
            try:
                counts = parse_junit(xml)
            except (ET.ParseError, OSError) as exc:
                reason = f"JUnit XML 無法讀取：{exc}"
        if counts and stage_id in {"regression_before", "regression_after"}:
            skip_policy_reason, skip_policy_note = regression_skip_policy(
                stage_id, counts, args.max_regression_skips,
            )
        if counts is None and not reason:
            reason = "未產生 JUnit XML，無法證明測試數量與結果"
        elif counts and counts["total"] == 0:
            reason = "JUnit 沒有任何測試案例"
        elif counts and count_expected is not None and counts["total"] != count_expected:
            reason = f"執行案例數 {counts['total']} 與預期 {count_expected} 不符"
        elif counts and require_no_skips and counts["skipped"]:
            reason = f"關鍵測試有 {counts['skipped']} 項 Skip，不能當作 PASS"
        elif skip_policy_reason:
            reason = skip_policy_reason
        elif code != 0:
            reason = f"pytest 結束碼 {code}（查看 {log.relative_to(ROOT)}）"
        elif counts and (counts["failed"] or counts["errors"]):
            reason = "JUnit 記錄仍有失敗／錯誤"
        status = "FAIL" if reason else "PASS"
        update(stage_id, status, reason, exit_code=code,
               duration_seconds=round(duration, 2), counts=counts,
               skip_policy_note=skip_policy_note,
               junit=str(xml.relative_to(ROOT)) if xml.exists() else None)
        return status == "PASS"

    try:
        if not args.auto_login:
            update("login", "NOT_REQUESTED", "未指定 --auto-login；沿用既有登入狀態")
            update("logout", "NOT_REQUESTED", "未指定 --auto-login；不操作登出")
        invalid = validate_targets(args.target)
        if invalid:
            update("targeted", "BLOCKED", f"禁止執行非一般回歸目標：{invalid}")
        missing_permissions = missing_manual_permissions(os.environ) if args.manual_activation else []
        if args.gherkin:
            missing_permissions = [name for name in missing_permissions if name.endswith("_WRITE")]
        if missing_permissions:
            update("manual_activation", "BLOCKED",
                   f"缺少明確授權：{', '.join(missing_permissions)}")
        if invalid or missing_permissions:
            return stop("BLOCKED", "目標白名單或操作授權不符", 2)

        if args.gherkin:
            missing_bdd = [
                name for name in GHERKIN_TARGETS + GHERKIN_REGRESSION_FEATURES + (
                    "tests/bdd/conftest.py", "tests/bdd/model_chat.feature", "tests/bdd/ai_app.feature",
                )
                if not (ROOT / name).is_file()
            ]
            if importlib.util.find_spec("pytest_bdd") is None:
                missing_bdd.append("pytest-bdd")
            if importlib.util.find_spec("pytest_playwright") is None:
                missing_bdd.append("pytest-playwright")
            if missing_bdd:
                update("manual_activation", "BLOCKED", f"缺少 Gherkin 所需檔案或套件：{', '.join(missing_bdd)}")
                return stop("BLOCKED", "Gherkin 執行環境未就緒", 2)

        compile_errors = []
        compiled = 0
        for name in data["source_sha256"]:
            if not name.endswith(".py"):
                continue
            try:
                source = (ROOT / name).read_bytes()
                compile(source, str(ROOT / name), "exec")
                compiled += 1
            except (SyntaxError, UnicodeError, OSError) as exc:
                compile_errors.append(f"{name}: {exc}")
        update("static", "FAIL" if compile_errors else "PASS",
               "; ".join(compile_errors) or f"已編譯檢查 {compiled} 支 Python",
               files_checked=compiled)
        if compile_errors:
            return stop("FAIL", "Python 靜態語法檢查失敗", 1)

        missing = [name for name in regression_files if not (ROOT / name).is_file()]
        if missing:
            update("collection", "BLOCKED", f"缺少完整一般回歸測試檔：{', '.join(missing)}")
            return stop("BLOCKED", "缺少一般回歸測試檔", 2)
        collection_cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q", *regression_files]
        log = run_dir / "collection.log"
        update("collection", "RUNNING", command=collection_cmd, log=str(log.relative_to(ROOT)))
        code, duration, stdout = run_command(collection_cmd, log, env=child_env)
        collected = parse_collection_count(stdout)
        collection_ok = code == 0 and collected == args.expected_regression_count
        update(
            "collection", "PASS" if collection_ok else "FAIL",
            f"收集 {collected} 項，預期 {args.expected_regression_count}；pytest 結束碼 {code}",
            collected=collected, exit_code=code, duration_seconds=round(duration, 2),
        )
        if not collection_ok:
            return stop("FAIL", "收集數量或 pytest 收集失敗", 1)

        if args.auto_login:
            helper_path = ROOT / "scripts" / "save_login_state.py"
            try:
                spec = importlib.util.spec_from_file_location("_ai_hub_validation_auth", helper_path)
                if spec is None or spec.loader is None:
                    raise ImportError("無法載入登入工具")
                auth_module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = auth_module
                spec.loader.exec_module(auth_module)
                auth = auth_module.ValidationSession(
                    ROOT / ".auth" / f"validation_{run_id}.json",
                    args.auth_browser, args.auth_browser_channel,
                )
            except Exception:
                update("login", "FAIL", "無法載入新版 scripts/save_login_state.py；請一併替換")
                return stop("FAIL", "自動登入工具未就緒", 1)
            if not auth_action("login", auth.login):
                return stop("FAIL", "自動登入或狀態重用驗證失敗；不執行回歸", 1)
            child_env = {**os.environ, "AI_HUB_AUTH_STATE": str(auth.state_path),
                         "BASE_URL": auth.config.base_url}

        # 整輪只接受命令列的明確選擇，避免繼承的環境變數意外送出訊息。
        child_env = dict(os.environ) if child_env is None else child_env
        child_env["MODEL_TEST_CHAT_SEND"] = "YES" if args.chat_send else "NO"
        if args.gherkin:
            stages["manual_activation"]["label"] = "Gherkin 模型對話與 AFS MyAgent 操作"
        elif args.chat_send:
            stages["manual_activation"]["label"] = "模型與 AI 應用操作（含一則模型對話送出驗證）"

        addons = ["-v", "-rs"]
        if importlib.util.find_spec("pytest_playwright") is not None:
            addons += ["--screenshot", "only-on-failure", "--tracing", "retain-on-failure"]
        else:
            data["warnings"].append("缺少 pytest-playwright，未啟用失敗截圖與 Trace 參數。")
        html_enabled = importlib.util.find_spec("pytest_html") is not None
        if not html_enabled:
            data["warnings"].append("缺少 pytest-html，未產生 HTML 報告；保留 JUnit 與執行日誌。")

        def pytest_cmd(stage_id: str, targets: tuple[str, ...] | list[str], *,
                       manual: bool = False) -> list[str]:
            cmd = [sys.executable, "-u", "-m", "pytest", *targets, *addons]
            if args.gherkin and stage_id in {"regression_before", "regression_after"}:
                cmd += ["--gherkin-terminal-reporter", "-vv"]
            if manual:
                cmd += ["-s", "--headed", "--slowmo", "1000"]
                if args.gherkin:
                    cmd += ["--gherkin-terminal-reporter", "-vv"]
            if html_enabled:
                cmd += ["--html", str(run_dir / f"{stage_id}.html"), "--self-contained-html"]
            return cmd

        if args.target:
            if not execute("targeted", pytest_cmd("targeted", args.target), require_no_skips=True):
                return stop("FAIL", "指定測試失敗或被略過", 1)
        else:
            update("targeted", "NOT_REQUESTED", "未指定 --target，非必做階段")

        if not execute("regression_before",
                       pytest_cmd("regression_before", regression_files),
                       count_expected=args.expected_regression_count):
            return stop("FAIL", "一般回歸失敗或範圍不符", 1)

        if args.manual_activation:
            manual_ok = execute("manual_activation",
                                pytest_cmd(
                                    "manual_activation",
                                    GHERKIN_TARGETS if args.gherkin else MANUAL_TARGETS,
                                    manual=True,
                                ),
                                count_expected=2, require_no_skips=True)
            # 即使啟停失敗，也要再測一次唯讀回歸，留下系統實際狀態。
            after_ok = execute("regression_after",
                               pytest_cmd("regression_after", regression_files),
                               count_expected=args.expected_regression_count)
            data["overall"] = "PASS" if manual_ok and after_ok else "FAIL"
        else:
            update("manual_activation", "NOT_REQUESTED", "未指定 --manual-activation；不操作服務")
            update("regression_after", "NOT_REQUESTED", "未執行操作型測試，因此不需第二輪")
            data["overall"] = "PASS"
        write_summary(data, run_dir)
        return 0 if data["overall"] == "PASS" else 1
    except KeyboardInterrupt:
        data["overall"] = "INTERRUPTED"
        for stage in data["stages"]:
            if stage["status"] == "RUNNING":
                stage.update(status="INTERRUPTED", reason="使用者中止執行")
        return stop("INTERRUPTED", "使用者中止執行", 130)
    except Exception:
        for stage in data["stages"]:
            if stage["status"] == "RUNNING":
                stage.update(status="FAIL", reason="執行器發生未預期錯誤，未輸出可能含敏感資訊的原始例外")
        return stop("FAIL", "執行器未預期錯誤", 1)
    finally:
        if auth is not None:
            previous = data["overall"]
            data["overall"] = "RUNNING"
            cleanup_ok = False
            try:
                cleanup_ok = auth_action("logout", auth.logout)
            except KeyboardInterrupt:
                previous = "INTERRUPTED"
            finally:
                try:
                    auth.close()
                except Exception:
                    cleanup_ok = False
                    update("logout", "FAIL", "瀏覽器關閉或本輪登入狀態檔清理失敗")
                data["overall"] = previous
                if not cleanup_ok and previous != "INTERRUPTED":
                    data["overall"] = "FAIL"
                write_summary(data, run_dir)
                print(f"[overall] {data['overall']}", flush=True)
            if data["overall"] == "INTERRUPTED":
                return 130
            if not cleanup_ok:
                return 1


if __name__ == "__main__":
    sys.exit(main())
