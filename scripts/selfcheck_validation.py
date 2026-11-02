"""統一執行器的離線單元測試（不觸及 AI Hub、Playwright 或服務狀態）。

執行：python -m unittest scripts/selfcheck_validation.py -v
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.run_validation import (
    MANUAL_TARGETS,
    missing_manual_permissions,
    parse_collection_count,
    parse_junit,
    validate_targets,
)


class ValidationRunnerSelfCheck(unittest.TestCase):
    def test_collection_count(self) -> None:
        self.assertEqual(parse_collection_count("46 tests collected in 0.8s"), 46)
        self.assertEqual(parse_collection_count("collected 46 items"), 46)
        self.assertIsNone(parse_collection_count("ImportError: failed"))

    def test_permissions_required(self) -> None:
        self.assertEqual(len(missing_manual_permissions({})), 4)
        self.assertEqual(missing_manual_permissions({
            "MODEL_TEST_WRITE": "I_UNDERSTAND",
            "MODEL_TEST_ALLOW_DISABLE": "YES",
            "AI_APP_TEST_WRITE": "I_UNDERSTAND",
            "AI_APP_TEST_ALLOW_DISABLE": "YES",
        }), [])

    def test_manual_targets_cannot_be_injected(self) -> None:
        self.assertEqual(
            validate_targets(["tests/test_user_home.py::test_safe"]), []
        )
        self.assertEqual(validate_targets([MANUAL_TARGETS[0]]), [MANUAL_TARGETS[0]])
        self.assertEqual(validate_targets(["--override-ini=x"]), ["--override-ini=x"])

    def test_junit_distinguishes_skips_and_failures(self) -> None:
        xml = '''<?xml version="1.0"?>
<testsuites><testsuite>
  <testcase classname="a" name="pass"/>
  <testcase classname="a" name="skip"><skipped message="缺少 LDAP 資料"/></testcase>
  <testcase classname="a" name="fail"><failure message="定位失敗"/></testcase>
</testsuite></testsuites>'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.xml"
            path.write_text(xml, encoding="utf-8")
            result = parse_junit(path)
        self.assertEqual(
            (result["total"], result["passed"], result["failed"], result["skipped"]),
            (3, 1, 1, 1),
        )
        self.assertEqual(result["skip_reasons"][0]["reason"], "缺少 LDAP 資料")

    def test_cli_integration_fake_pytest_and_manual_guard(self) -> None:
        """隔離專案加上假 pytest，檢驗整條流程；不連線、不啟停。"""
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            scripts = root / "scripts"
            scripts.mkdir()
            shutil.copy2(Path(__file__).with_name("run_validation.py"), scripts / "run_validation.py")
            tests = root / "tests"
            tests.mkdir()
            for name in ("test_site_access.py", "test_platform_manager.py", "test_user_home.py"):
                (tests / name).write_text("def test_safe(): assert True\n", encoding="utf-8")
            fake_pytest = root / "pytest"
            fake_pytest.mkdir()
            # 必須是「正式套件」：沒有 __init__.py 時只會是 namespace package，
            # macOS 若已安裝真正的 pytest，可能優先載入 site-packages 的 pytest。
            # 結果會意外執行真 pytest，並找不到這個隔離專案的 manual_*.py。
            (fake_pytest / "__init__.py").write_text(
                "# 只供隔離整合測試使用；不得連線 AI Hub。\n", encoding="utf-8"
            )
            (fake_pytest / "__main__.py").write_text(
                """
import os
import sys
from pathlib import Path
print('AI_HUB_FAKE_PYTEST_ACTIVE')
args = sys.argv[1:]
if '--collect-only' in args:
    print('3 tests collected in 0.01s')
else:
    manual = any('manual_' in a for a in args)
    count = 2 if manual else 3
    path = Path(args[args.index('--junitxml') + 1])
    path.parent.mkdir(parents=True, exist_ok=True)
    cases = ''.join('<testcase classname="safe" name="test_%s"/>' % n for n in range(count))
    if manual and os.environ.get('FAKE_MANUAL_FAIL') == 'YES':
        cases = '<testcase classname="manual" name="failed"><failure message="mock"/></testcase>'
        cases += '<testcase classname="manual" name="passed"/>'
    path.write_text('<testsuites><testsuite>' + cases + '</testsuite></testsuites>')
    print('%s passed in 0.01s' % count)
    if manual and os.environ.get('FAKE_MANUAL_FAIL') == 'YES':
        sys.exit(1)
""".strip() + "\n", encoding="utf-8",
            )
            # 模擬 Mac 已安裝真正 pytest 的情況：外層另有一份同名正式套件。
            # 隔離目錄的 fake pytest 仍必須優先被載入。
            simulated_site = root / "simulated_site_packages" / "pytest"
            simulated_site.mkdir(parents=True)
            (simulated_site / "__init__.py").write_text("", encoding="utf-8")
            (simulated_site / "__main__.py").write_text(
                "raise SystemExit('WRONG_PYTEST_PACKAGE')\n", encoding="utf-8"
            )
            isolated_env = os.environ.copy()
            isolated_env["PYTHONPATH"] = (
                str(simulated_site.parent)
                + os.pathsep
                + isolated_env.get("PYTHONPATH", "")
            )
            cmd = [sys.executable, "scripts/run_validation.py",
                   "--expected-regression-count", "3", "--max-regression-skips", "0"]
            result = subprocess.run(
                cmd, cwd=root, env=isolated_env, capture_output=True, text=True, timeout=15
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(
                "AI_HUB_FAKE_PYTEST_ACTIVE", result.stdout,
                "隔離測試未使用 fake pytest，禁止以真正 pytest 結果冒充模擬。",
            )
            summary_path = root / "reports" / "validation_summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["overall"], "PASS")
            statuses = {s["id"]: s["status"] for s in summary["stages"]}
            self.assertEqual(statuses["regression_before"], "PASS")
            self.assertEqual(statuses["manual_activation"], "NOT_REQUESTED")
            self.assertEqual(statuses["regression_after"], "NOT_REQUESTED")

            no_auth = isolated_env.copy()
            for name in ("MODEL_TEST_WRITE", "MODEL_TEST_ALLOW_DISABLE",
                         "AI_APP_TEST_WRITE", "AI_APP_TEST_ALLOW_DISABLE"):
                no_auth.pop(name, None)
            rejected = subprocess.run(
                [*cmd, "--manual-activation"], cwd=root, env=no_auth,
                capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(rejected.returncode, 2)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            statuses = {s["id"]: s["status"] for s in summary["stages"]}
            self.assertEqual(summary["overall"], "BLOCKED")
            self.assertEqual(statuses["manual_activation"], "BLOCKED")
            self.assertEqual(statuses["regression_before"], "BLOCKED")

            auth = {**no_auth,
                    "MODEL_TEST_WRITE": "I_UNDERSTAND",
                    "MODEL_TEST_ALLOW_DISABLE": "YES",
                    "AI_APP_TEST_WRITE": "I_UNDERSTAND",
                    "AI_APP_TEST_ALLOW_DISABLE": "YES"}
            authorized = subprocess.run(
                [*cmd, "--manual-activation"], cwd=root, env=auth,
                capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(authorized.returncode, 0, authorized.stdout + authorized.stderr)
            self.assertIn("AI_HUB_FAKE_PYTEST_ACTIVE", authorized.stdout)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            statuses = {s["id"]: s["status"] for s in summary["stages"]}
            self.assertEqual(summary["overall"], "PASS")
            self.assertEqual(statuses["manual_activation"], "PASS")
            self.assertEqual(statuses["regression_after"], "PASS")

            failed = subprocess.run(
                [*cmd, "--manual-activation"], cwd=root,
                env={**auth, "FAKE_MANUAL_FAIL": "YES"},
                capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(failed.returncode, 1)
            self.assertIn("AI_HUB_FAKE_PYTEST_ACTIVE", failed.stdout)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            statuses = {s["id"]: s["status"] for s in summary["stages"]}
            self.assertEqual(summary["overall"], "FAIL")
            self.assertEqual(statuses["manual_activation"], "FAIL")
            self.assertEqual(statuses["regression_after"], "PASS")


if __name__ == "__main__":
    unittest.main()
