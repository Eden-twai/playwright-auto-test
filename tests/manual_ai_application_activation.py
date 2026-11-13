"""指定執行的 AFS MyAgent 操作測試；不納入一般 pytest -v 回歸。

依目前狀態：
- 未下載 → 需 AI_APP_TEST_ALLOW_DOWNLOAD=YES 才下載，下載完成後啟用
- 已下載未啟用 → 啟用
- 已啟用 → 不停用，直接驗證「開始使用」

上述流程均不發送對話訊息；已啟用且有停用授權時可跑完整循環。
啟用失敗預設不重試。AI_APP_TEST_ALLOW_RETRY=YES 允許短暫回退後提早重試一次；
舊參數 AI_APP_TEST_RETRY_ON_TIMEOUT=YES 只在等滿 300 秒時允許重試一次。
"""
from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import Page
from pages.platform_manager_page import PlatformManagerPage
from pages.user_home_page import UserHomePage

TARGET_APP = "AFS MyAgent"
DOWNLOAD_TIMEOUT = 2400  # 40 分鐘；下載可能很大，實際時間視網路及後端而定
DOWNLOAD_START_GRACE = 60  # 下載點擊後，容許尚未進入下載中
DOWNLOAD_FAILED_GRACE = 30  # 曾下載中但退回未下載：觀察一段時間再失敗
ENABLE_TIMEOUT = 300  # AI 應用啟用最多 5 分鐘；模型啟用等待另行維持 10 分鐘
DISABLE_TIMEOUT = 90
POLL_INTERVAL = 1.0
RETRY_CONFIRM_SECONDS = 10  # 第一次逾時後，重新確認狀態穩定才允許重試
FAST_RETRY_GRACE_SECONDS = 30  # 連續未啟用 30 秒才允許進入一次重試的確認流程


class AIAppEnableTimeout(AssertionError):
    """只代表等待 enabled 到期；和未知狀態、停用失敗等錯誤分開。"""


class AIAppEarlyFallback(AssertionError):
    """啟用後持續未啟用；僅在明確開啟快速重試時使用。"""


def _record_activation_event(event: str, state: str) -> None:
    """保留嘗試次數與逾時歷史；只寫事件及 UI 狀態，不記錄憑證。"""
    folder = Path("reports/ai_application_activation")
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    entry = f"{now}\tAFS MyAgent\t{event}\tstate={state}\n"
    with (folder / "enable_attempts.log").open("a", encoding="utf-8") as stream:
        stream.write(entry)
    print(f"啟用嘗試紀錄：{event}，狀態={state}")


def _observations(app: PlatformManagerPage):
    """狀態與 Snackbar 都由畫面讀取，不假設請求已成功。"""
    observed_messages: set[str] = set()
    def report(state: str, elapsed: float, previous: str | None) -> str:
        if state != previous:
            print(f"AI 應用狀態：{state}（經過 {elapsed:.1f} 秒）")
        for message in app.ai_app_snackbar_messages():
            if message not in observed_messages:
                print(f"Snackbar：{message}")
                observed_messages.add(message)
        return state
    return report


def wait_for_download(app: PlatformManagerPage) -> str:
    """只等待下載結果，不再次點擊下載；回傳已下載後的狀態。"""
    started_at = time.monotonic()
    reporter = _observations(app)
    previous = None
    saw_downloading = False
    not_downloaded_since = None

    while time.monotonic() - started_at < DOWNLOAD_TIMEOUT:
        # 如果下載按鈕出現未知確認對話框，不猜測按鈕文字，也不自動同意。
        # 讓測試立即失敗並截圖，避免原地等待長達一分鐘。
        dialogs = app.page.get_by_role("dialog").filter(visible=True)
        if dialogs.count():
            raise AssertionError(
                "點擊下載後出現確認對話框；目前未確認其 DOM 與安全語意，"
                "因此不自動確認。請提供對話框畫面／DOM 後再補自動化。"
            )
        state = app.ai_app_state(TARGET_APP)
        elapsed = time.monotonic() - started_at
        previous = reporter(state, elapsed, previous)
        if state in ("downloaded_disabled", "enabled"):
            print(f"{TARGET_APP} 下載階段完成（目前狀態：{state}）。")
            return state
        if state == "downloading":
            saw_downloading = True
            not_downloaded_since = None
        elif state == "not_downloaded":
            if not_downloaded_since is None:
                not_downloaded_since = time.monotonic()
            grace = DOWNLOAD_FAILED_GRACE if saw_downloading else DOWNLOAD_START_GRACE
            if time.monotonic() - not_downloaded_since >= grace:
                reason = "下載中又返回未下載" if saw_downloading else "點擊下載後未觀察到下載中"
                raise AssertionError(
                    f"AFS MyAgent 下載未完成：{reason}，狀態已持續 {grace} 秒；"
                    "請檢查是否有下載確認視窗、Snackbar、儲存空間或後端日誌。"
                )
        else:
            raise AssertionError(f"下載過程出現非預期狀態：{state}")
        time.sleep(POLL_INTERVAL)

    raise AssertionError(
        f"AFS MyAgent 下載逾時（{DOWNLOAD_TIMEOUT} 秒），最後狀態={previous}；"
        "請檢查網路、儲存空間及 Hub 日誌。"
    )


def wait_until(
    app: PlatformManagerPage,
    target: str,
    limit: int,
    *,
    early_fallback_grace: int | None = None,
) -> None:
    """等待啟用／停用狀態，啟用最多觀察 ENABLE_TIMEOUT，且不重複送出動作。"""
    start = time.monotonic()
    previous = None
    observed_enabling = False
    returned_to_disabled = False
    disabled_since = None
    reporter = _observations(app)
    last_progress = start

    while time.monotonic() - start < limit:
        state = app.ai_app_state(TARGET_APP)
        previous = reporter(state, time.monotonic() - start, previous)
        now = time.monotonic()
        if now - last_progress >= 10:
            print(f"仍在等待 AI 應用達到 {target}：目前 {state}，已等 {now - start:.0f}/{limit} 秒")
            last_progress = now
        if state == target:
            return
        if state == "enabling":
            observed_enabling = True
            disabled_since = None
        elif state == "downloaded_disabled" and target == "enabled":
            # 只有開啟重試時才以較短觀察期結束本輪；不在 enabling 時重複點擊。
            # 即使未捕捉到短暫的 enabling，也能辨識點擊後持續沒有進度。
            if observed_enabling and not returned_to_disabled:
                policy = (
                    f"若持續 {early_fallback_grace} 秒將記錄提早回退並檢查是否可重試。"
                    if early_fallback_grace is not None
                    else f"繼續觀察，最多等待 {limit} 秒，期間不重複送出啟用。"
                )
                print(
                    f"警告：{TARGET_APP} 曾進入啟用中後返回未啟用；"
                    f"{policy}"
                )
                returned_to_disabled = True
            if disabled_since is None:
                disabled_since = time.monotonic()
            if (
                early_fallback_grace is not None
                and time.monotonic() - disabled_since >= early_fallback_grace
            ):
                raise AIAppEarlyFallback(
                    f"AFS MyAgent 連續至少 {early_fallback_grace} 秒維持 downloaded_disabled；"
                    f"曾觀察到啟用中={observed_enabling}。"
                )
        elif state == "not_downloaded":
            raise AssertionError("等待啟用／停用時 AI 應用回到未下載，已停止測試。")
        elif state not in ("enabling", "disabling", "downloading", "enabled", "downloaded_disabled"):
            raise AssertionError(f"等待啟用／停用時出現非預期狀態：{state}")
        else:
            disabled_since = None
        time.sleep(POLL_INTERVAL)

    error_type = AIAppEnableTimeout if target == "enabled" else AssertionError
    raise error_type(
        f"等待 AI 應用達到 {target} 逾時（{limit} 秒），最後狀態={previous}；"
        f"曾觀察到啟用中={observed_enabling}；"
        f"曾從啟用中退回未啟用={returned_to_disabled}。"
        "請檢查 Snackbar 與後端日誌；預設不會自動重試啟用。"
    )


def _wait_enabled_with_optional_retry(app: PlatformManagerPage) -> None:
    """預設等 300 秒；有明確授權時容許提早回退重試一次並保留紀錄。"""
    fast_retry = os.getenv("AI_APP_TEST_ALLOW_RETRY") == "YES"
    timeout_retry = fast_retry or os.getenv("AI_APP_TEST_RETRY_ON_TIMEOUT") == "YES"
    print("AI 應用重試：" + (
        f"已開啟；未啟用持續 {FAST_RETRY_GRACE_SECONDS} 秒後檢查，最多重試一次。"
        if fast_retry else "僅逾時後重試一次。" if timeout_retry
        else f"未開啟；最多等待 {ENABLE_TIMEOUT} 秒，不會第二次點擊啟用。"
    ))
    try:
        wait_until(
            app,
            "enabled",
            ENABLE_TIMEOUT,
            early_fallback_grace=FAST_RETRY_GRACE_SECONDS if fast_retry else None,
        )
        return
    except AIAppEarlyFallback:
        first_state = app.ai_app_state(TARGET_APP)
        _record_activation_event("attempt_1_disabled_30s", first_state)
        print("第一輪持續未啟用 30 秒，已保留異常紀錄，準備檢查一次重試。")
    except AIAppEnableTimeout:
        # 無論有沒有授權重試，第一輪逾時都必須落盤且在 Terminal 顯示。
        first_state = app.ai_app_state(TARGET_APP)
        _record_activation_event("attempt_1_timeout_300s", first_state)
        print("第一輪啟用等待 300 秒逾時；此失敗已記錄，不會因第二輪成功而抹除。")
        if not timeout_retry:
            raise

    state = app.ai_app_state(TARGET_APP)
    if state == "enabled":
        _record_activation_event("enabled_after_first_timeout", state)
        return
    if state != "downloaded_disabled":
        raise AssertionError(f"拒絕重試：第一次逾時後狀態為 {state}，非已下載未啟用")

    # UI 長時間顯示未啟用也不保證後端沒有部署工作；因此額外授權才重試。
    print(f"已授權最多一次重試；等待 {RETRY_CONFIRM_SECONDS} 秒確認狀態仍未啟用。")
    confirmation_deadline = time.monotonic() + RETRY_CONFIRM_SECONDS
    while True:
        state = app.ai_app_state(TARGET_APP)
        if state == "enabled":
            _record_activation_event("enabled_during_retry_confirmation", state)
            return
        if state != "downloaded_disabled":
            raise AssertionError(f"拒絕重試：確認期間狀態變為 {state}，不重複點擊")
        if time.monotonic() >= confirmation_deadline:
            break
        time.sleep(POLL_INTERVAL)

    # 第二次之前再次由 Page Object 檢查狀態及寫入授權。
    app.ai_app_choose_action(TARGET_APP, "啟用")
    _record_activation_event("attempt_2_clicked", state)
    try:
        wait_until(
            app, "enabled", ENABLE_TIMEOUT,
            early_fallback_grace=FAST_RETRY_GRACE_SECONDS if fast_retry else None,
        )
    except AIAppEarlyFallback:
        _record_activation_event("attempt_2_disabled_30s", app.ai_app_state(TARGET_APP))
        raise
    except AIAppEnableTimeout:
        _record_activation_event("attempt_2_timeout_300s", app.ai_app_state(TARGET_APP))
        raise
    else:
        _record_activation_event("attempt_2_enabled", "enabled")


def save_failure(page: Page) -> None:
    folder = Path("reports/ai_application_activation")
    folder.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=str(folder / "failure.png"), full_page=True, timeout=10_000)
    except Exception as exc:
        print(f"保存截圖失敗：{type(exc).__name__}")


def require_ai_app_write() -> None:
    if os.getenv("AI_APP_TEST_WRITE") != "I_UNDERSTAND":
        pytest.skip("操作測試預設關閉；須設定 AI_APP_TEST_WRITE=I_UNDERSTAND")


def _ensure_enabled(app: PlatformManagerPage, *, allow_download: bool) -> None:
    state = app.ai_app_state(TARGET_APP)
    print(f"{TARGET_APP} 起始狀態：{state}")
    if state in ("enabling", "disabling", "downloading"):
        pytest.skip(f"AFS MyAgent 已有操作進行中：{state}，不重複操作")
    if state == "not_downloaded":
        if not allow_download:
            pytest.skip("AFS MyAgent 未下載；需額外設定 AI_APP_TEST_ALLOW_DOWNLOAD=YES 才能下載")
        print("AFS MyAgent 未下載，已授權下載；下載可能占用大量網路流量與儲存空間。")
        app.ai_app_choose_action(TARGET_APP, "下載")
        state = wait_for_download(app)
    if state == "downloaded_disabled":
        print(f"準備啟用 AI 應用：{TARGET_APP}")
        app.ai_app_choose_action(TARGET_APP, "啟用")
        _wait_enabled_with_optional_retry(app)
    elif state == "enabled":
        print("AFS MyAgent 已啟用，直接進入使用者端驗證，不執行停用。")
    else:
        pytest.fail(f"不支援的 AI 應用狀態：{state}")


def expect_ai_app_enabled(app: PlatformManagerPage) -> None:
    assert app.ai_app_state(TARGET_APP) == "enabled", "AFS MyAgent 尚未達到已啟用"


def open_ai_app_management(page: Page) -> PlatformManagerPage:
    app = PlatformManagerPage(page)
    app.goto()
    app.open_ai_application_management()
    return app


def activate_ai_app(app: PlatformManagerPage) -> None:
    state = app.ai_app_state(TARGET_APP)
    if state == "enabled" and os.getenv("AI_APP_TEST_ALLOW_DISABLE") == "YES":
        print("AFS MyAgent 已啟用且已授權停用：執行停用 → 重新啟用。")
        app.ai_app_choose_action(TARGET_APP, "停用")
        wait_until(app, "downloaded_disabled", DISABLE_TIMEOUT)
    _ensure_enabled(
        app,
        allow_download=os.getenv("AI_APP_TEST_ALLOW_DOWNLOAD") == "YES",
    )


def _verify_start(page: Page) -> None:
    home = UserHomePage(page)
    home.expect_ai_app_entry(TARGET_APP)  # 啟用已確認：入口缺失時必須 FAIL
    home.click_ai_app_start(TARGET_APP)  # 不發送任何訊息
    print("AFS MyAgent「開始使用」已點擊，確認有畫面／網址／分頁切換（未發送訊息）。")


@pytest.mark.auth
def test_ai_app_preflight(authenticated_page: Page) -> None:
    """唯讀查看狀態：不下載、不啟停。"""
    app = PlatformManagerPage(authenticated_page)
    app.goto()
    app.open_ai_application_management()
    print(f"\n{TARGET_APP} 狀態：{app.ai_app_state(TARGET_APP)}")
    print("唯讀預檢：不會下載、啟用、停用或刪除")


@pytest.mark.auth
def test_ai_app_activation(authenticated_page: Page) -> None:
    """依起始狀態自動啟用；明確授權停用時，已啟用會跑完整循環。"""
    require_ai_app_write()
    try:
        app = open_ai_app_management(authenticated_page)
        activate_ai_app(app)
        expect_ai_app_enabled(app)
        _verify_start(authenticated_page)
    except Exception:
        save_failure(authenticated_page)
        raise


@pytest.mark.auth
def test_ai_app_start_only(authenticated_page: Page) -> None:
    """不改變應用狀態：未啟用時 SKIP，已啟用才點「開始使用」。"""
    app = PlatformManagerPage(authenticated_page)
    app.goto()
    app.open_ai_application_management()
    if app.ai_app_state(TARGET_APP) != "enabled":
        pytest.skip("AFS MyAgent 未啟用，不能驗證開始使用")
    try:
        _verify_start(authenticated_page)
    except Exception:
        save_failure(authenticated_page)
        raise


@pytest.mark.auth
def test_ai_app_disable_enable_cycle(authenticated_page: Page) -> None:
    """高風險完整循環獨立測試：需獲准停用才執行，不混入一般啟用流程。"""
    require_ai_app_write()
    if os.getenv("AI_APP_TEST_ALLOW_DISABLE") != "YES":
        pytest.skip("完整循環需額外設定 AI_APP_TEST_ALLOW_DISABLE=YES")
    app = PlatformManagerPage(authenticated_page)
    try:
        app.goto()
        app.open_ai_application_management()
        state = app.ai_app_state(TARGET_APP)
        if state != "enabled":
            pytest.skip("完整停用再啟用循環需以已啟用狀態開始，不自動下載或補啟用")
        print("已授權完整循環：停用 AFS MyAgent → 重新啟用")
        app.ai_app_choose_action(TARGET_APP, "停用")
        wait_until(app, "downloaded_disabled", DISABLE_TIMEOUT)
        app.ai_app_choose_action(TARGET_APP, "啟用")
        _wait_enabled_with_optional_retry(app)
        _verify_start(authenticated_page)
    except Exception:
        save_failure(authenticated_page)
        raise
