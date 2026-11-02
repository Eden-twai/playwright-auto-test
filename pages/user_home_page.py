from __future__ import annotations

import re
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, expect


class UserHomePage:
    """AI Hub 使用者首頁；送出對話僅由明確要求的操作測試呼叫。"""

    PATH = "/"

    SIDEBAR_ITEMS = (
        "開始新的對話",
        "提示詞庫",
    )

    ACCOUNT_MENU_ITEMS = (
        "系統提示詞",
        "模型參數設定",
        "語言",
        "登出",
    )

    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self) -> None:
        self.page.goto(self.PATH, wait_until="domcontentloaded")

    def sidebar_button(self, name: str) -> Locator:
        # 按鈕內的圖片 alt 也會被算進 accessible name，例如：
        # "New Chat 開始新的對話"。改以按鈕可見文字定位，避免 alt
        # 讓 get_by_role(..., exact=True) 找不到元素。
        return self.page.locator("button.user-sidebar-btns").filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")
        )

    def visible_text(self, text: str) -> Locator | None:
        matches = self.page.get_by_text(text, exact=True)

        for index in range(matches.count()):
            candidate = matches.nth(index)
            if candidate.is_visible():
                return candidate

        return None

    def expect_loaded(self, timeout_ms: int = 20_000) -> None:
        """等待 Chat 首頁就緒；一般測試最多 20 秒，啟停後測試可個別延長。"""
        expect(self.sidebar_button("開始新的對話")).to_be_visible(timeout=timeout_ms)
        expect(
            self.page.get_by_placeholder("詢問任何問題", exact=True)
        ).to_be_visible(timeout=timeout_ms)

    def expect_sidebar_visible(self) -> None:
        expect(
            self.page.get_by_role("img", name="AFS AI Hub", exact=True)
        ).to_be_visible()

        for item in self.SIDEBAR_ITEMS:
            expect(self.sidebar_button(item)).to_be_visible()

        # 未啟用 AI 應用時，使用者側欄不一定顯示「AI應用」。
        # 有入口時仍驗證它可見；缺少時不要把正常空狀態判為故障。
        apps_button = self.sidebar_button("AI應用")
        if apps_button.count():
            expect(apps_button).to_be_visible()
        else:
            print("使用者側欄：目前沒有 AI 應用入口（允許無已啟用 AI 應用的空狀態）")

        expect(
            self.page.get_by_text("對話歷史", exact=True)
        ).to_be_visible()
        expect(self.sidebar_button("平台管理")).to_be_visible()
        expect(self.sidebar_button("帳號及設定")).to_be_visible()

    def expect_home_content_visible(self) -> None:
        expect(
            self.page.get_by_role(
                "heading",
                name=re.compile(r".+，您好[！!]$"),
            )
        ).to_be_visible()
        # 無已啟用 AI 應用時，首頁不顯示「您的 AI 應用程式」與卡片屬正常。
        # 有卡片或區塊標題時，則必須同時顯示兩者，避免掩蓋半套 UI。
        apps_heading = self.page.get_by_text("您的 AI 應用程式", exact=True)
        app_cards = self.page.locator(".ai-card")
        if apps_heading.count() or app_cards.count():
            expect(apps_heading).to_be_visible()
            expect(app_cards.first).to_be_visible()
        else:
            print("首頁：沒有已啟用 AI 應用卡片，驗證基本對話介面")

        message_input = self.page.get_by_placeholder("詢問任何問題", exact=True)
        expect(message_input).to_be_visible()

        send_button = self.page.locator("button.send-message")
        expect(send_button).to_be_visible()
        expect(send_button).to_be_disabled()

    def model_menu_button(self) -> Locator:
        # 新對話首頁中最後一個 chat-dropdown-btn 為模型選單；
        # 不使用重複的 id="modelDropdown"。
        return self.page.locator(
            ".no-session .chat-dropdown-btn:visible"
        ).last

    def open_model_menu(self) -> None:
        button = self.model_menu_button()
        expect(button).to_be_visible()
        button.click()

    def expect_model_menu_visible(self) -> None:
        menu = self.model_menu_button().locator("xpath=following-sibling::ul[1]")
        expect(menu).to_be_visible()

    def select_chat_model(self, name: str) -> None:
        """在新對話中明確選擇指定模型，不送出任何訊息。"""
        button = self.model_menu_button()
        expect(button).to_be_visible(timeout=15_000)
        # 已經選取的模型不需要重新開選單。
        if name in button.inner_text():
            print(f"Chat 已選擇模型：{name}")
            return

        self.open_model_menu()
        self.expect_model_menu_visible()
        menu = button.locator("xpath=following-sibling::ul[1]")
        option = menu.get_by_text(name, exact=True)
        expect(option).to_have_count(1, timeout=10_000)
        expect(option).to_be_visible()
        option.click()
        # 若實際 UI 沒有更新選擇器標籤，必須報錯，不能誤判為已選取。
        expect(button).to_contain_text(name, timeout=10_000)
        print(f"Chat 已選擇模型：{name}")

    def expect_chat_text_can_be_entered(self) -> None:
        """驗證可輸入並恢復原文字，絕不點擊送出。"""
        editor = self.page.get_by_placeholder("詢問任何問題", exact=True)
        expect(editor).to_be_visible(timeout=15_000)
        expect(editor).to_be_editable()
        previous = editor.input_value()
        probe = "Playwright UI input check (not sent)"
        try:
            editor.fill(probe)
            expect(editor).to_have_value(probe)
        finally:
            editor.fill(previous)
        expect(editor).to_have_value(previous)

    @staticmethod
    def chat_session_id(url: str) -> str | None:
        values = parse_qs(urlsplit(url).query, keep_blank_values=True).get("sessionId", [])
        if len(values) != 1 or not values[0].strip():
            return None
        return values[0]

    def send_chat_and_expect_reply(self, message: str, timeout_ms: int = 120_000) -> dict:
        """只送出一則，驗證新對話與回覆，再從歷史開回同一 session。

        此方法會建立真正的對話紀錄。送出後失敗不自動重送、不刪除歷史。
        回覆僅檢查非空白及可從歷史重新開啟，不宣稱生成已完整結束或語意正確。
        """
        if not message.strip():
            raise ValueError("測試訊息不可為空白")
        before_url = urlsplit(self.page.url)
        if self.chat_session_id(self.page.url) is not None:
            raise AssertionError("送出前必須位於新對話首頁，不能接續既有 session")
        expect(self.page.locator(".message-wrapper.user-message")).to_have_count(0)
        expect(self.page.locator(".message-wrapper.assistant-message")).to_have_count(0)
        editor = self.page.get_by_placeholder("詢問任何問題", exact=True)
        send = self.page.locator("button.send-message:visible")
        expect(editor).to_be_editable(timeout=15_000)
        editor.fill(message)
        expect(editor).to_have_value(message)
        expect(send).to_have_count(1)
        expect(send).to_be_enabled(timeout=15_000)
        print("Chat：送出一則測試訊息；後續檢查失敗不會自動重送。", flush=True)
        send.click()

        def is_new_session(url):
            parsed = urlsplit(str(url))
            return (parsed.scheme == before_url.scheme
                    and parsed.netloc == before_url.netloc
                    and parsed.path == before_url.path
                    and self.chat_session_id(str(url)) is not None)

        self.page.wait_for_url(is_new_session, timeout=30_000)
        session_id = self.chat_session_id(self.page.url)
        assert session_id is not None
        print("Chat：已建立非空白 sessionId。", flush=True)
        users = self.page.locator(".message-wrapper.user-message")
        expect(users).to_have_count(1, timeout=30_000)
        expect(users).to_have_text(message)
        expect(editor).to_have_value("", timeout=30_000)
        replies = self.page.locator(".message-wrapper.assistant-message .message-content")
        expect(replies).to_have_count(1, timeout=timeout_ms)
        expect(replies).to_have_text(re.compile(r"\S"), timeout=timeout_ms)
        reply_length = len(replies.inner_text().strip())
        print(f"Chat：出現非空白模型回覆（目前 {reply_length} 字元）。", flush=True)

        active_title = self.page.locator(".session-list .session-item.active .session-title")
        expect(active_title).to_have_count(1, timeout=30_000)
        expect(active_title).to_have_text(re.compile(r"\S"), timeout=30_000)
        title = active_title.inner_text().strip()
        # 以當輪產生的標題找候選，最後以 sessionId 確認是同一個對話。
        # 相同標題可能存在，因此逐一開候選，絕不只憑標題判定成功。
        self.open_new_chat()
        self.page.wait_for_url(lambda url: self.chat_session_id(str(url)) is None, timeout=15_000)
        candidates = self.page.locator(".session-list .session-item .session-title").filter(
            has_text=re.compile(rf"^\s*{re.escape(title)}\s*$"))
        expect(candidates.first).to_be_visible(timeout=30_000)
        candidate_count = candidates.count()
        found = False
        for index in range(candidate_count):
            candidate = candidates.nth(index)
            old_session = self.chat_session_id(self.page.url)
            candidate.click()
            # 同標題的不同對話也會導覽；等 sessionId 出現後再比較。
            self.page.wait_for_url(lambda url: is_new_session(url)
                                   and self.chat_session_id(str(url)) != old_session,
                                   timeout=15_000)
            if self.chat_session_id(self.page.url) == session_id:
                found = True
                break
        if not found:
            raise AssertionError("歷史紀錄候選未開回本輪新建立的 sessionId")
        expect(users).to_have_count(1, timeout=30_000)
        expect(users).to_have_text(message)
        expect(replies).to_have_count(1, timeout=timeout_ms)
        expect(replies).to_have_text(re.compile(r"\S"), timeout=timeout_ms)
        print("Chat：歷史紀錄可開回同一 session，送出內容與回覆均存在。", flush=True)
        return {"session_id": session_id, "history_title": title,
                "reply_nonempty": True, "reply_length_observed": reply_length,
                "history_reopened": True, "sent_messages": 1}

    def open_prompt_library(self) -> None:
        self.sidebar_button("提示詞庫").click()
        expect(
            self.page.get_by_role("heading", name="提示詞庫", exact=True)
        ).to_be_visible()

    def expect_prompt_library_static_content(self) -> None:
        expect(
            self.page.get_by_role("button", name=re.compile(r"新增提示詞"))
        ).to_be_visible()
        expect(self.page.get_by_role("table")).to_be_visible()

        for header in ("名稱", "描述", "建立時間", "最後修改時間", "功能"):
            expect(
                self.page.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

    def open_new_chat(self) -> None:
        self.sidebar_button("開始新的對話").click()
        self.expect_loaded()

    def open_ai_apps(self, *, required: bool = False) -> None:
        apps_button = self.sidebar_button("AI應用")
        if not required and apps_button.count() == 0:
            # 給 Angular 一小段載入時間，避免入口稍晚出現而被誤判為空。
            # 這是使用者端 UI 前置判斷；剛啟用成功的嚴格測試使用 required=True。
            try:
                apps_button.wait_for(state="visible", timeout=3_000)
            except PlaywrightTimeoutError:
                import pytest
                pytest.skip(
                    "使用者介面沒有 AI 應用入口；若目前無已啟用應用則屬預期，"
                    "啟用後須使用 required=True 嚴格驗證"
                )
        expect(apps_button).to_be_visible(timeout=10_000)
        apps_button.click()
        expect(
            self.page.get_by_role("heading", name="AI應用", exact=True)
        ).to_be_visible()

    def expect_ai_apps_static_content(self) -> None:
        cards = self.page.locator(".card-agent")
        expect(cards.first).to_be_visible()
        expect(
            cards.first.locator("button.btn-agentCard-default").filter(
                has_text=re.compile(r"^\s*開始使用\s*$")
            )
        ).to_be_visible()

    def open_account_settings(self) -> None:
        self.sidebar_button("帳號及設定").click()

    def expect_account_settings_menu_visible(self) -> None:
        for item in self.ACCOUNT_MENU_ITEMS:
            option = self.visible_text(item)
            if option is None:
                raise AssertionError(f"找不到可見的帳號設定選項：{item}")

            expect(option).to_be_visible()

    def ai_app_card(self, name: str) -> Locator:
        card = self.page.locator(".card-agent").filter(has_text=name)
        expect(card).to_have_count(1)
        return card

    def expect_ai_app_entry(self, name: str) -> None:
        self.goto()
        self.expect_loaded()
        # 已由管理端確認啟用，因此入口必須顯示；不能 Skip 掩蓋問題。
        self.open_ai_apps(required=True)
        card = self.ai_app_card(name)
        expect(card).to_be_visible()
        start = card.locator("button.btn-agentCard-default").filter(
            has_text=re.compile(r"^\s*開始使用\s*$")
        )
        expect(start).to_have_count(1)
        expect(start).to_be_visible()

    def click_ai_app_start(self, name: str) -> None:
        """只點開始使用，不傳送訊息；要求有可觀測的導覽變化。"""
        card = self.ai_app_card(name)
        start = card.locator("button.btn-agentCard-default").filter(
            has_text=re.compile(r"^\s*開始使用\s*$")
        )
        expect(start).to_be_visible()
        old_url = self.page.url
        old_pages = len(self.page.context.pages)
        start.click()
        # 不假設 App 內頁有 Chat 輸入框；確認卡片離開當前畫面、網址變化或開新分頁。
        import time
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.page.url != old_url or len(self.page.context.pages) > old_pages or not card.is_visible():
                return
            self.page.wait_for_timeout(300)
        raise AssertionError(f"點擊「開始使用」後未觀察到導覽或畫面切換：{name}")
