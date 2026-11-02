"""放在 scripts/：手動登入、--auto 自動登入、--auto --check-cycle 登入登出驗證。"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTH_STATE = PROJECT_ROOT / ".auth" / "user.json"
# 方便觀看登入與登出；pytest 啟停與對話視窗的速度另行設定。
AUTH_SLOW_MO_MS = 1_000


@dataclass(frozen=True)
class Settings:
    base_url: str
    username: str
    password: str
    username_selector: str
    password_selector: str
    submit_selector: str
    success_selector: str
    account_menu_selector: str
    logout_selector: str
    timeout_ms: int


def settings_from_env(auto: bool) -> Settings:
    raw = os.getenv("BASE_URL", "").strip()
    parts = urlsplit(raw)
    if (parts.scheme not in {"http", "https"} or not parts.hostname
            or parts.username is not None or parts.password is not None
            or parts.query or parts.fragment):
        raise ValueError("請設定有效的 BASE_URL（http/https，不含帳密、查詢參數或片段）。")
    if parts.path not in {"", "/"}:
        raise ValueError("BASE_URL 請填 AI Hub 網站根網址；目前沿用 /platform-manager 路徑。")
    username = os.getenv("TEST_USERNAME", "")
    password = os.getenv("TEST_PASSWORD", "")
    if auto and (not username.strip() or not password):
        raise ValueError("自動登入需要 TEST_USERNAME 與 TEST_PASSWORD。")
    try:
        timeout = int(os.getenv("AUTH_TIMEOUT_MS", "60000"))
    except ValueError:
        raise ValueError("AUTH_TIMEOUT_MS 必須是正整數。") from None
    if timeout <= 0:
        raise ValueError("AUTH_TIMEOUT_MS 必須是正整數。")
    selectors = [os.getenv(name, default).strip() for name, default in (
        ("AUTH_USERNAME_SELECTOR", "#usernameInput"),
        ("AUTH_PASSWORD_SELECTOR", "#password"),
        ("AUTH_SUBMIT_SELECTOR", "#loginButton"),
        ("AUTH_SUCCESS_SELECTOR", 'text="模型管理"'),
        ("AUTH_ACCOUNT_MENU_SELECTOR", 'text="帳號及設定"'),
        ("AUTH_LOGOUT_SELECTOR", 'text="登出"'),
    )]
    if not all(selectors):
        raise ValueError("登入與登出定位設定不可為空。")
    return Settings(raw.rstrip("/"), username, password, *selectors, timeout)


def is_management_url(url: str, base_url: str) -> bool:
    actual, expected = urlsplit(url), urlsplit(base_url)
    return (actual.scheme == expected.scheme
            and actual.netloc == expected.netloc
            and actual.path.rstrip("/") == "/platform-manager")


class AuthStepError(RuntimeError):
    """只攜帶安全的步驟名稱，不轉印 Playwright 帳密與 URL。"""


def run_step(label, action):
    print(f"[登入流程] {label}…", flush=True)
    try:
        return action()
    except Exception:
        raise AuthStepError(f"{label}失敗；請核對目前畫面與對應定位。") from None


def confirm_logged_in(page, config: Settings) -> None:
    # URL 與登入後畫面均要確認，不能只靠網址包含管理路徑。
    run_step("等待返回管理頁", lambda: page.wait_for_url(
        lambda url: is_management_url(str(url), config.base_url)))
    run_step("確認模型管理入口", lambda: page.locator(
        config.success_selector).wait_for(state="visible"))


def automatic_login(page, config: Settings) -> None:
    # 依實際登入頁 DOM 定位；仍可用環境變數覆寫其他環境的定位。
    run_step("尋找帳號欄位並填入", lambda: page.locator(
        config.username_selector).fill(config.username))
    run_step("尋找密碼欄位並填入", lambda: page.locator(
        config.password_selector).fill(config.password))
    run_step("完成密碼欄位輸入", lambda: page.locator(
        config.password_selector).press("Tab"))
    # click 會等待 disabled 解除，不使用 force 繞過頁面的必填檢查。
    run_step("等待登入按鈕可用並點擊", lambda: page.locator(config.submit_selector).click())
    confirm_logged_in(page, config)


def confirm_logout(page, config: Settings) -> None:
    run_step("開啟帳號及設定", lambda: page.locator(config.account_menu_selector).click())
    run_step("點擊登出", lambda: page.locator(config.logout_selector).click())
    run_step("確認登出後帳號欄位", lambda: page.locator(
        config.username_selector).wait_for(state="visible"))
    run_step("確認登出後密碼欄位", lambda: page.locator(
        config.password_selector).wait_for(state="visible"))
    # 不清 Cookie；回訪同一受保護頁，確認 SSO 不會直接登入回去。
    run_step("重新進入受保護的管理頁", lambda: page.goto(
        "/platform-manager", wait_until="domcontentloaded"))
    run_step("確認仍要求輸入帳號", lambda: page.locator(
        config.username_selector).wait_for(state="visible"))
    run_step("確認仍要求輸入密碼", lambda: page.locator(
        config.password_selector).wait_for(state="visible"))
    if is_management_url(page.url, config.base_url):
        raise ValueError("登出後仍停留在管理頁，不能判定登出成功。")


def save_verified_state(browser, context, config: Settings, state_path: Path | None = None) -> None:
    # 先在另一個 context 確認狀態可重用，成功後才取代原本檔案。
    state = context.storage_state()
    verification = browser.new_context(
        base_url=config.base_url, ignore_https_errors=True,
        locale="zh-TW", storage_state=state,
    )
    try:
        verification.set_default_timeout(config.timeout_ms)
        check_page = verification.new_page()
        check_page.goto("/platform-manager", wait_until="domcontentloaded")
        confirm_logged_in(check_page, config)
    finally:
        verification.close()
    target = state_path if state_path is not None else AUTH_STATE
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, suffix=".json", delete=False) as fp:
            temporary = Path(fp.name)
        context.storage_state(path=str(temporary))
        os.chmod(temporary, 0o600)
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class ValidationSession:
    """整輪驗證持有同一登入頁；各 pytest 程序沿用本輪專用狀態。"""

    def __init__(self, state_path: Path, browser_name="chromium", channel=None):
        self.state_path = state_path
        self.browser_name = browser_name
        self.channel = channel
        self.playwright = self.browser = self.context = self.page = None
        self.logged_in = False
        self.login_attempted = False

    def login(self):
        from dotenv import load_dotenv
        from playwright.sync_api import sync_playwright
        load_dotenv(PROJECT_ROOT / ".env")
        self.config = settings_from_env(True)
        self.playwright = sync_playwright().start()
        options = {"headless": False, "slow_mo": AUTH_SLOW_MO_MS}
        if self.channel:
            options["channel"] = self.channel
        self.browser = getattr(self.playwright, self.browser_name).launch(**options)
        self.context = self.browser.new_context(
            base_url=self.config.base_url, ignore_https_errors=True,
            locale="zh-TW", viewport={"width": 1440, "height": 900},
        )
        self.context.set_default_timeout(self.config.timeout_ms)
        self.page = self.context.new_page()
        self.page.goto("/platform-manager", wait_until="domcontentloaded")
        self.login_attempted = True
        automatic_login(self.page, self.config)
        self.logged_in = True
        save_verified_state(self.browser, self.context, self.config, self.state_path)

    def logout(self):
        if self.page is None or not self.login_attempted:
            return "未開始登入，無本輪工作階段可登出"
        # 登入後標記驗證失敗時，也檢查是否已實際登入，以便盡力清理。
        if not self.logged_in:
            if not self.page.locator(self.config.account_menu_selector).is_visible():
                self.page.goto("/platform-manager", wait_until="domcontentloaded")
                self.page.locator(self.config.username_selector).wait_for(state="visible")
                self.page.locator(self.config.password_selector).wait_for(state="visible")
                return "登入未完成；已確認管理頁仍要求登入"
        confirm_logout(self.page, self.config)
        self.logged_in = False
        return "已點擊登出，回訪管理頁仍要求登入"

    def close(self):
        try:
            if self.browser is not None:
                self.browser.close()
        finally:
            try:
                if self.playwright is not None:
                    self.playwright.stop()
            finally:
                # 只清除此輪檔案，不動既有 .auth/user.json。
                self.state_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Hub 手動／自動登入與獨立登出驗證")
    parser.add_argument("--auto", action="store_true", help="自動輸入本機設定的測試帳密")
    parser.add_argument("--check-cycle", action="store_true", help="只驗證登入、登出，不保存登入狀態")
    parser.add_argument("--browser", choices=("chromium", "firefox", "webkit"), default="chromium")
    parser.add_argument("--browser-channel", choices=("chrome", "msedge"))
    args = parser.parse_args(argv)
    if args.check_cycle and not args.auto:
        parser.error("--check-cycle 必須搭配 --auto")
    if args.browser_channel and args.browser != "chromium":
        parser.error("Chrome/Edge channel 必須搭配 --browser chromium")
    try:
        from dotenv import load_dotenv
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("缺少 python-dotenv 或 playwright；請先啟用專案 .venv 並安裝專案套件。")
        return 2
    load_dotenv(PROJECT_ROOT / ".env")
    try:
        config = settings_from_env(args.auto)
    except ValueError as exc:
        print(str(exc))
        return 2
    phase = "開啟瀏覽器與測試網址"
    try:
        with sync_playwright() as playwright:
            launch_options = {"headless": False, "slow_mo": AUTH_SLOW_MO_MS}
            if args.browser_channel:
                launch_options["channel"] = args.browser_channel
            browser = getattr(playwright, args.browser).launch(**launch_options)
            try:
                context = browser.new_context(
                    base_url=config.base_url, ignore_https_errors=True, locale="zh-TW",
                    viewport={"width": 1440, "height": 900},
                )
                context.set_default_timeout(config.timeout_ms)
                page = context.new_page()
                page.goto("/platform-manager", wait_until="domcontentloaded")
                phase = "登入與管理頁驗證"
                if args.auto:
                    print("開始自動登入（不顯示帳密）。", flush=True)
                    automatic_login(page, config)
                else:
                    print("請在瀏覽器完成登入，並進入 Platform Manager。")
                    input("完成後回到這裡按 Enter：")
                    confirm_logged_in(page, config)
                print("登入與管理頁驗證通過。", flush=True)
                if args.check_cycle:
                    phase = "登出與受保護頁面驗證"
                    confirm_logout(page, config)
                    print("登入／登出驗證通過；本次未寫入登入狀態。")
                else:
                    phase = "登入狀態重用驗證與儲存"
                    save_verified_state(browser, context, config)
                    print("登入狀態已驗證並儲存至 .auth/user.json。")
            finally:
                browser.close()
    except (KeyboardInterrupt, EOFError):
        print("操作已中止；未確認完成的步驟不可視為通過。")
        return 130
    except AuthStepError as exc:
        print(str(exc))
        print("本次驗證失敗；未輸出帳密與原始例外。")
        return 1
    except Exception:
        # Playwright 原始例外可能包含 fill 值與登入 URL 參數，不能直接印出。
        print(f"{phase}失敗；請確認畫面、帳號權限與定位設定。未完成步驟不算通過。")
        print("未輸出原始例外，以免帳密或登入參數出現在終端紀錄。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
