from __future__ import annotations

import os
import re
from urllib.parse import urlsplit

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, expect


class PlatformManagerPage:
    PATH = "/platform-manager"

    ACCOUNT_SETTINGS_NAME = re.compile(
        r"(?:帳號及設定|Account(?:\s+(?:and|&))?\s+Settings)",
        re.IGNORECASE,
    )

    MENU_ITEMS = (
        "總覽",
        "使用者管理",
        "群組管理",
        "LDAP設定",
        "模型管理",
        "AI應用管理",
        "API 端點",
        "API 金鑰管理",
        "系統日誌",
    )

    SECTION_HEADINGS = {
        "LDAP設定": "LDAP 設定",
    }

    OVERVIEW_SECTIONS = {
        "使用者": ("排名", "使用者", "Token數"),
        "API Key": ("排名", "API Key名稱", "Token數"),
        "群組": ("排名", "群組名稱", "Token數"),
    }

    OVERVIEW_SECTION_TEXT = {
        "使用者": "使用者 排名使用者Token數",
        "API Key": "API Key 排名API Key名稱Token數",
        "群組": "群組 排名群組名稱Token數",
    }

    USER_TABLE_HEADERS = (
        "名字",
        "姓氏",
        "帳號",
        "角色",
        "狀態",
        "功能",
    )

    GROUP_TABLE_HEADERS = (
        "名稱",
        "描述",
        "人數",
        "建立時間",
        "最後修改時間",
        "功能",
    )

    GROUP_MEMBER_TABLE_HEADERS = (
        "姓名",
        "帳號",
        "功能",
    )

    MODEL_TABLE_HEADERS = (
        "模型名稱",
        "模型簡介",
        "發行者",
        "檔案大小",
        "狀態",
        "使用權限",
        "功能",
    )

    MODEL_ACTIVITY_TABLE_HEADERS = (
        "模型",
        "操作者",
        "動作/狀態",
    )

    AI_APPLICATION_TABLE_HEADERS = (
        "AI應用名稱",
        "AI應用簡介",
        "發行者",
        "檔案大小",
        "狀態",
        "使用權限",
        "功能",
    )

    API_ENDPOINT_TABLE_HEADERS = (
        "API名稱",
        "API類型",
        "API端點",
        "說明",
    )

    API_ENDPOINT_ROWS = (
        (
            "Chat Completions",
            "POST",
            "/chat/completions",
            "根據歷史對話生成下一句回答",
        ),
        (
            "Embeddings",
            "POST",
            "/embeddings",
            "根據輸入文字生成向量",
        ),
        (
            "Rerank",
            "POST",
            "/rerank",
            "根據輸入文字進行重新排序評分",
        ),
        (
            "Responses",
            "POST",
            "/responses",
            "依單次輸入生成完整結構化回應",
        ),
        (
            "Models",
            "GET",
            "/models",
            "取得目前可用的模型列表",
        ),
    )

    API_KEY_TABLE_HEADERS = (
        "金鑰名稱",
        "描述",
        "建立者",
        "建立時間",
        "最後使用時間",
        "到期時間",
        "功能",
    )

    LDAP_TABLE_HEADERS = (
        "名稱",
        "LDAP URL",
        "StartTLS",
        "Bind DN",
        "Users DN",
        "功能",
    )

    LDAP_FORM_LABELS = (
        re.compile(r"^名稱\s*\*$"),
        re.compile(r"^LDAP URL\s*\*$"),
        re.compile(r"^StartTLS\s*\*$"),
        re.compile(r"^Bind DN\s*\*$"),
        re.compile(r"^Bind credentials\s*\*$"),
        re.compile(r"^Users DN\s*\*$"),
    )

    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self) -> None:
        self.page.goto(self.PATH, wait_until="domcontentloaded")

    def menu_item(self, name: str) -> Locator:
        # 左側導航的按鈕可能包含圖示 alt，導致 accessible name
        # 不完全等於畫面文字。限定 button + 精確可見文字，避開分類標題。
        return self.page.get_by_role("button").filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")
        )

    def account_settings_button(self) -> Locator:
        # accessible name 會包含使用者名稱，因此使用部分比對；
        # 同時支援切換前後的中英文標籤。
        return self.page.get_by_role(
            "button",
            name=self.ACCOUNT_SETTINGS_NAME,
        )

    def visible_text(self, text: str) -> Locator | None:
        """取得第一個目前可見的精確文字，避開下拉選單的隱藏副本。"""
        matches = self.page.get_by_text(text, exact=True)

        for index in range(matches.count()):
            candidate = matches.nth(index)
            if candidate.is_visible():
                return candidate

        return None

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(
            re.compile(r"/platform-manager(?:[/?#]|$)")
        )
        expect(self.menu_item("總覽")).to_be_visible()

    def expect_main_menu_visible(self) -> None:
        for item in self.MENU_ITEMS:
            expect(self.menu_item(item)).to_be_visible()

    def expect_chinese_interface(self) -> None:
        expect(
            self.page.get_by_role("heading", name="總覽", exact=True)
        ).to_be_visible()
        expect(self.menu_item("使用者管理")).to_be_visible()

    def expect_english_interface(self) -> None:
        expect(
            self.page.get_by_role("heading", name="Overview", exact=True)
        ).to_be_visible()
        expect(
            self.page.get_by_role(
                "button",
                name="User Management",
                exact=True,
            )
        ).to_be_visible()

    def switch_language(
        self,
        *,
        current_language: str,
        target_language: str,
    ) -> None:
        self.account_settings_button().click()

        # 語言選項位於第二層選單：帳號及設定 → 語言／Language。
        language_menu_label = (
            "語言" if current_language == "繁體中文" else "Language"
        )
        language_menu = self.visible_text(language_menu_label)
        if language_menu is None:
            raise AssertionError(
                f"找不到語言選單：{language_menu_label}"
            )

        # 右側語言子選單由 hover 觸發；等待選項完成顯示後再點擊。
        language_menu.hover()
        target_option = self.page.get_by_text(
            target_language,
            exact=True,
        ).last
        expect(target_option).to_be_visible()
        target_option.click()

    def open_overview(self) -> None:
        self.menu_item("總覽").click()
        expect(
            self.page.get_by_role("heading", name="總覽", exact=True)
        ).to_be_visible()

    def open_user_management(self) -> None:
        self.open_section("使用者管理")

    def user_table(self) -> Locator:
        return self.page.get_by_role("table")

    def expect_user_management_static_content(self) -> None:
        expect(
            self.page.get_by_role(
                "heading",
                name="使用者管理",
                exact=True,
            )
        ).to_be_visible()
        expect(
            self.page.get_by_role(
                "button",
                name="+ 新增使用者",
                exact=True,
            )
        ).to_be_visible()

        table = self.user_table()
        expect(table).to_be_visible()

        for header in self.USER_TABLE_HEADERS:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

        # 不寫死使用者姓名或帳號，只確認表格至少有一筆資料列。
        expect(table.locator("tbody tr").first).to_be_visible()

    def open_add_user_modal(self) -> None:
        self.page.get_by_role(
            "button",
            name="+ 新增使用者",
            exact=True,
        ).click()

        dialog = self.page.get_by_role("dialog")
        expect(dialog).to_be_visible()
        expect(
            dialog.get_by_text("新增使用者", exact=True)
        ).to_be_visible()

    def expect_add_user_modal_content(self) -> None:
        dialog = self.page.get_by_role("dialog")

        for label in ("帳號*", "密碼*", "角色", "姓氏/名字*", "電子郵件*"):
            expect(dialog.get_by_text(label, exact=True)).to_be_visible()

        expect(
            dialog.get_by_role("button", name=re.compile(r"產生"))
        ).to_be_visible()
        expect(
            dialog.get_by_role("radio", name="系統管理員", exact=True)
        ).to_be_visible()
        expect(
            dialog.get_by_role("radio", name="使用者", exact=True)
        ).to_be_visible()
        expect(
            dialog.get_by_text("與登入帳號相同", exact=True)
        ).to_be_visible()
        expect(
            dialog.get_by_role("button", name="取消", exact=True)
        ).to_be_visible()
        expect(
            dialog.get_by_role("button", name="新增", exact=True)
        ).to_be_visible()

    def cancel_add_user_modal(self) -> None:
        dialog = self.page.get_by_role("dialog")
        dialog.get_by_role("button", name="取消", exact=True).click()
        expect(dialog).not_to_be_visible()

    def open_first_user_action_menu(self) -> None:
        """開啟首筆有功能按鈕的使用者列，不假設第一列或最後一欄一定有按鈕。"""
        table = self.user_table()
        expect(table).to_be_visible()
        # tbody 可能有非資料用 tr；優先限定包含下拉按鈕的資料列。
        rows = table.locator("tbody tr")
        buttons = rows.locator(
            "button.more-options-btn, "
            "button[data-bs-toggle='dropdown'], "
            "button[aria-haspopup='menu'], "
            "button[aria-haspopup='true'], "
            "button:has(img[alt='更多選項']), "
            "button:has(img[alt='More Options'])"
        )
        try:
            expect(buttons.first).to_be_visible(timeout=10000)
        except AssertionError as error:
            row_count = rows.count()
            all_buttons = table.locator("tbody button")
            button_info = all_buttons.evaluate_all(
                "els => els.slice(0, 12).map(e => ({text: e.innerText, "
                "aria: e.getAttribute('aria-label'), "
                "title: e.getAttribute('title'), "
                "className: e.className, "
                "html: e.outerHTML.slice(0, 350)}))"
            )
            raise AssertionError(
                "使用者管理表格找不到可辨識的更多選項按鈕；"
                f"資料列數={row_count}；tbody 按鈕數={all_buttons.count()}；"
                f"按鈕資訊={button_info}。請提供功能欄按鈕的實際 DOM。"
            ) from error
        buttons.first.click()

    def expect_user_action_menu_visible(self) -> None:
        # 每筆資料列都有一份隱藏選單，只驗證目前展開且可見的選項。
        for text in ("修改", "刪除"):
            option = self.visible_text(text)
            if option is None:
                raise AssertionError(f"找不到可見的功能選項：{text}")

            expect(option).to_be_visible()

    def open_group_management(self) -> None:
        self.open_section("群組管理")

    def group_table(self) -> Locator:
        return self.page.get_by_role("table")

    def expect_group_management_static_content(self) -> None:
        expect(
            self.page.get_by_role(
                "heading",
                name="群組管理",
                exact=True,
            )
        ).to_be_visible()
        expect(
            self.page.get_by_role(
                "button",
                name="+ 新增群組",
                exact=True,
            )
        ).to_be_visible()

        table = self.group_table()
        expect(table).to_be_visible()

        for header in self.GROUP_TABLE_HEADERS:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

        # 群組資料可能因測試環境而為空；靜態內容測試只驗證頁面與欄位結構。

    def has_group_rows(self) -> bool:
        """目前群組表格是否至少有一筆可操作的資料列。"""
        return self.group_table().locator("tbody tr").count() > 0

    def open_add_group_page(self) -> None:
        self.page.get_by_role(
            "button",
            name="+ 新增群組",
            exact=True,
        ).click()
        expect(
            self.page.get_by_text("新增群組", exact=True)
        ).to_be_visible()

    def expect_add_group_page_content(self) -> None:
        expect(
            self.page.get_by_placeholder("限輸入1~20字元")
        ).to_be_visible()
        expect(
            self.page.get_by_placeholder("選填，可輸入0~100字元")
        ).to_be_visible()
        expect(
            self.page.get_by_text("人數", exact=True)
        ).to_be_visible()
        expect(
            self.page.get_by_text("群組成員", exact=True)
        ).to_be_visible()
        expect(
            self.page.get_by_role(
                "button",
                name="+ 選擇成員",
                exact=True,
            )
        ).to_be_visible()
        expect(
            self.page.get_by_placeholder("搜尋已選擇成員")
        ).to_be_visible()

        member_table = self.page.get_by_role("table")
        expect(member_table).to_be_visible()
        for header in self.GROUP_MEMBER_TABLE_HEADERS:
            expect(
                member_table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

        expect(
            self.page.get_by_role(
                "button",
                name="返回群組管理",
                exact=True,
            )
        ).to_be_visible()
        expect(
            self.page.get_by_role(
                "button",
                name="確認新增",
                exact=True,
            )
        ).to_be_visible()

    def return_to_group_management(self) -> None:
        self.page.get_by_role(
            "button",
            name="返回群組管理",
            exact=True,
        ).click()
        expect(
            self.page.get_by_role(
                "heading",
                name="群組管理",
                exact=True,
            )
        ).to_be_visible()

    def open_first_group_action_menu(self) -> None:
        # Codegen 確認群組列的功能按鈕 accessible name 同樣為 More Options。
        self.page.get_by_role(
            "button",
            name="More Options",
            exact=True,
        ).first.click()

    def expect_group_action_menu_visible(self) -> None:
        # 每筆群組可能各有一份隱藏選單，只驗證目前可見的選項。
        for text in ("修改", "刪除"):
            option = self.visible_text(text)
            if option is None:
                raise AssertionError(f"找不到可見的功能選項：{text}")

            expect(option).to_be_visible()

    def open_model_management(self) -> None:
        self.open_section("模型管理")

    def model_table(self) -> Locator:
        # 依專屬欄位辨識模型主表，避免依賴表格排序或操作紀錄展開狀態。
        return self.page.get_by_role("table").filter(
            has=self.page.get_by_role("columnheader", name="模型名稱", exact=True)
        ).first

    # 模型操作測試專用：與 AI 應用方法分開，避免誤操作不同資源。
    def model_row(self, name: str) -> Locator:
        rows = self.model_table().locator("tbody tr")
        target = rows.filter(has=self.page.get_by_text(name, exact=True))
        expect(target).to_have_count(1, timeout=10_000)
        expect(target.locator("td").first).to_have_text(name)
        return target

    def model_state(self, name: str) -> str:
        raw = self.model_row(name).locator("td").nth(4).inner_text()
        state = re.sub(r"\s+", "", raw)
        if "啟用中" in state:
            return "enabling"
        if "停用中" in state:
            return "disabling"
        if "下載中" in state:
            return "downloading"
        if "未下載" in state:
            return "not_downloaded"
        if "已下載" in state and "未啟用" in state:
            return "downloaded_disabled"
        if "已啟用" in state:
            return "enabled"
        raise AssertionError(f"未知模型狀態：{name}: {raw!r}")

    def other_running_models(self, target_name: str) -> list[str]:
        """保守地阻止測試干擾其他已啟用／狀態不明的模型。"""
        table = self.model_table()
        expect(table).to_be_visible(timeout=10_000)
        rows = table.locator("tbody tr")
        expect(rows.first).to_be_visible(timeout=10_000)
        active = []
        for index in range(rows.count()):
            columns = rows.nth(index).locator("td")
            if columns.count() < 5:
                raise AssertionError("模型資料列欄位不足，停止操作")
            name = columns.first.inner_text().strip()
            if name == target_name:
                continue
            state = re.sub(r"\s+", "", columns.nth(4).inner_text())
            if any(s in state for s in ("啟用中", "停用中", "下載中", "已啟用")):
                active.append(name)
            elif not ("未下載" in state or ("已下載" in state and "未啟用" in state)):
                raise AssertionError(f"其他模型 {name} 狀態無法辨識：{state!r}，停止操作")
        return active

    def click_model_action(self, name: str, action: str) -> None:
        allowed_states = {"啟用": "downloaded_disabled", "停用": "enabled"}
        if action not in allowed_states:
            raise ValueError("模型測試只允許啟用或停用，不執行下載")
        if os.getenv("MODEL_TEST_WRITE") != "I_UNDERSTAND":
            raise PermissionError("模型操作未授權：需設定 MODEL_TEST_WRITE=I_UNDERSTAND")
        if action == "停用" and os.getenv("MODEL_TEST_ALLOW_DISABLE") != "YES":
            raise PermissionError("模型停用未授權：需設定 MODEL_TEST_ALLOW_DISABLE=YES")
        current = self.model_state(name)
        if current != allowed_states[action]:
            raise AssertionError(f"拒絕模型{action}：{name} 狀態為 {current}")
        if self.other_running_models(name):
            raise AssertionError("其他模型正在運作，停止操作")

        row = self.model_row(name)
        button = row.locator("td").last.locator("button.more-options-btn")
        expect(button).to_have_count(1)
        expect(button).to_be_visible()
        button.click()
        expect(button).to_have_attribute("aria-expanded", "true", timeout=5000)
        in_row = row.locator(".dropdown-menu.show:visible")
        menus = in_row if in_row.count() == 1 else self.page.locator(".dropdown-menu.show:visible")
        expect(menus).to_have_count(1, timeout=5000)
        option = menus.first.get_by_text(action, exact=True).filter(visible=True)
        expect(option).to_have_count(1, timeout=5000)
        option.click()
        print(f"模型 {name}：已點擊{action}，等待狀態更新")

    def visible_snackbar_messages(self) -> list[str]:
        alerts = self.page.locator(
            "[role='alert']:visible, [role='status']:visible, "
            ".mat-mdc-snack-bar-container:visible, .snackbar:visible, .toast:visible"
        )
        return [message.strip() for message in alerts.all_inner_texts() if message.strip()]

    def expect_model_management_static_content(self) -> None:
        expect(
            self.page.get_by_role(
                "heading",
                name="模型管理",
                exact=True,
            )
        ).to_be_visible()

        expect(
            self.page.get_by_role(
                "button",
                name="近7天操作紀錄",
                exact=True,
            )
        ).to_be_visible()

        table = self.model_table()
        expect(table).to_be_visible()

        for header in self.MODEL_TABLE_HEADERS:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

        # 不寫死模型名稱，只確認目前環境至少顯示一筆模型資料。
        expect(table.locator("tbody tr").first).to_be_visible()

    def model_activity_button(self) -> Locator:
        return self.page.get_by_role(
            "button",
            name="近7天操作紀錄",
            exact=True,
        )

    def model_activity_table(self) -> Locator:
        # 用操作紀錄專屬欄位定位，避免收合後 .last 改指向主模型表。
        return (
            self.page.get_by_role("table")
            .filter(has_text="動作/狀態")
            .first
        )

    def open_model_activity(self) -> None:
        self.model_activity_button().click()

        table = self.model_activity_table()
        expect(table).to_be_visible()

        for header in self.MODEL_ACTIVITY_TABLE_HEADERS:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

    def close_model_activity(self) -> None:
        table = self.model_activity_table()
        self.model_activity_button().click()
        expect(table).not_to_be_visible()

    def has_model_rows(self) -> bool:
        """等待模型清單載入，避免立即 count() 把載入中的空表誤判成無資料。"""
        table = self.model_table()
        expect(table).to_be_visible(timeout=10_000)
        rows = table.locator("tbody tr").filter(has=self.page.locator("td"))
        try:
            rows.first.wait_for(state="visible", timeout=10_000)
            return True
        except PlaywrightTimeoutError:
            print("模型表格已顯示，但 10 秒內沒有出現可見的資料列")
            return False

    def open_first_model_action_menu(self) -> None:
        # 模型欄位按鈕包含 alt="更多選項"，不能依賴英文 More Options。
        row = self.model_table().locator("tbody tr").first
        expect(row).to_be_visible()
        more = row.locator("td").last.locator("button.more-options-btn")
        expect(more).to_have_count(1)
        expect(more).to_be_visible()
        more.click()

    def expect_model_action_menu_visible(self) -> None:
        # 不同模型狀態有「下載／啟用／停用」；避免寫死第一筆模型未下載。
        permission = self.visible_text("使用權限設定")
        if permission is None:
            raise AssertionError("模型選單沒有可見的「使用權限設定」")
        expect(permission).to_be_visible()
        for action in ("下載", "啟用", "停用"):
            option = self.visible_text(action)
            if option is not None:
                expect(option).to_be_visible()
                return
        raise AssertionError("模型選單沒有可見的「下載／啟用／停用」項目")

    def open_ai_application_management(self) -> None:
        self.open_section("AI應用管理")

    def ai_application_table(self) -> Locator:
        return self.page.get_by_role("table").filter(
            has=self.page.get_by_role("columnheader", name="AI應用名稱", exact=True)
        ).first

    def expect_ai_application_management_static_content(self) -> None:
        expect(
            self.page.get_by_role(
                "heading",
                name="AI應用管理",
                exact=True,
            )
        ).to_be_visible()

        table = self.ai_application_table()
        expect(table).to_be_visible()

        for header in self.AI_APPLICATION_TABLE_HEADERS:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

        # AI 應用可能因測試環境而為空；靜態內容測試不要求存在資料列。

    def ai_application_action_buttons(self) -> Locator:
        # 在功能欄找更多選項，不依賴可能因 icon alt 改變的 accessible name。
        return self.ai_application_table().locator(
            "tbody tr td:last-child button.more-options-btn"
        )

    def has_ai_application_rows(self) -> bool:
        """等待 AI 應用資料列載入，不將初始空畫面直接判定為無資料。"""
        table = self.ai_application_table()
        expect(table).to_be_visible(timeout=10_000)
        rows = table.locator("tbody tr").filter(has=self.page.locator("td"))
        try:
            rows.first.wait_for(state="visible", timeout=10_000)
            return True
        except PlaywrightTimeoutError:
            print("AI 應用表格已顯示，但 10 秒內沒有出現可見的資料列")
            return False

    def open_first_ai_application_action_menu(self) -> None:
        row = self.ai_application_table().locator("tbody tr").first
        expect(row).to_be_visible()
        more = row.locator("td").last.locator("button.more-options-btn")
        expect(more).to_have_count(1)
        expect(more).to_be_visible()
        more.click()

    def expect_ai_application_action_menu_visible(self) -> None:
        permission = self.visible_text("使用權限設定")
        if permission is None:
            raise AssertionError("AI 應用選單沒有可見的「使用權限設定」")
        expect(permission).to_be_visible()
        # 未下載/已下載/已啟用各有不同操作；只驗證選單，不執行寫入。
        for action in ("下載", "啟用", "停用"):
            option = self.visible_text(action)
            if option is not None:
                expect(option).to_be_visible()
                return
        raise AssertionError("AI 應用選單沒有可見的「下載／啟用／停用」項目")

    def open_api_endpoint(self) -> None:
        self.open_section("API 端點")

    def api_endpoint_table(self) -> Locator:
        return self.page.get_by_role("table").first

    def api_endpoint_status(self) -> Locator | None:
        """取得目前顯示的 API 端點狀態，不操作狀態開關。"""
        status = self.visible_text("已啟用")
        if status is not None:
            return status

        return self.visible_text("未啟用")

    def expect_api_endpoint_static_content(self) -> None:
        expect(
            self.page.get_by_role(
                "heading",
                name="API 端點",
                exact=True,
            )
        ).to_be_visible()

        status = self.api_endpoint_status()
        if status is None:
            raise AssertionError("找不到 API 端點狀態：已啟用或未啟用")

        expect(status).to_be_visible()

        table = self.api_endpoint_table()
        expect(table).to_be_visible()

        for header in self.API_ENDPOINT_TABLE_HEADERS:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

        # API 端點未啟用時表格會是空的；靜態內容測試不要求資料列。

    def has_api_endpoint_rows(self) -> bool:
        """目前 API 端點表格是否至少有一筆資料。"""
        return self.api_endpoint_table().locator("tbody tr").count() > 0

    def expect_enabled_api_endpoint_details(self) -> None:
        """驗證啟用狀態下的公開端點資訊，不讀取或複製 Base URL。"""
        enabled_status = self.visible_text("已啟用")
        if enabled_status is None:
            raise AssertionError("API 端點目前未顯示為已啟用")

        expect(enabled_status).to_be_visible()

        table = self.api_endpoint_table()
        for api_name, api_type, endpoint, description in self.API_ENDPOINT_ROWS:
            row = table.get_by_role("row").filter(has_text=api_name).first
            expect(row).to_be_visible()

            for cell_text in (api_name, api_type, endpoint, description):
                expect(
                    row.get_by_role(
                        "cell",
                        name=cell_text,
                        exact=True,
                    )
                ).to_be_visible()

    def open_api_key_management(self) -> None:
        self.open_section("API 金鑰管理")

    def api_key_table(self) -> Locator:
        return self.page.get_by_role("table").first

    def expect_api_key_management_static_content(self) -> None:
        expect(
            self.page.get_by_role(
                "heading",
                name="API 金鑰管理",
                exact=True,
            )
        ).to_be_visible()
        expect(
            self.page.get_by_role(
                "button",
                name=re.compile(r"^\+\s*新增\s*API\s*金鑰$"),
            )
        ).to_be_visible()
        expect(
            self.page.get_by_placeholder(
                "輸入完整API KEY查詢",
                exact=True,
            )
        ).to_be_visible()

        table = self.api_key_table()
        expect(table).to_be_visible()

        for header in self.API_KEY_TABLE_HEADERS:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

        # 靜態內容測試不寫死金鑰名稱、建立者或日期等環境資料。

    def api_key_action_buttons(self) -> Locator:
        return self.api_key_table().get_by_role(
            "button",
            name="More Options",
            exact=True,
        )

    def has_api_key_rows(self) -> bool:
        """目前 API 金鑰表格是否至少有一筆可操作的資料列。"""
        return self.api_key_action_buttons().count() > 0

    def open_first_api_key_action_menu(self) -> None:
        self.api_key_action_buttons().first.click()

    def expect_api_key_action_menu_visible(self) -> None:
        # 只驗證選項顯示，不執行展延或刪除。
        for text in ("展延", "刪除"):
            option = self.visible_text(text)
            if option is None:
                raise AssertionError(f"找不到可見的功能選項：{text}")

            expect(option).to_be_visible()

    def open_add_api_key_modal(self) -> None:
        self.page.get_by_role(
            "button",
            name=re.compile(r"^\+\s*新增\s*API\s*金鑰$"),
        ).click()

        dialog = self.page.get_by_role("dialog")
        expect(dialog).to_be_visible()
        expect(
            dialog.get_by_text("新增API金鑰", exact=True)
        ).to_be_visible()

    def expect_add_api_key_modal_content(self) -> None:
        dialog = self.page.get_by_role("dialog")

        for label in ("金鑰名稱*", "描述", "有效天數*"):
            expect(dialog.get_by_text(label, exact=True)).to_be_visible()

        expect(
            dialog.get_by_placeholder(
                "請輸入3~20字元中英文或數字字元",
                exact=True,
            )
        ).to_be_visible()
        expect(
            dialog.get_by_placeholder(
                "請輸入0~100字元",
                exact=True,
            )
        ).to_be_visible()

        valid_days = dialog.get_by_role("spinbutton")
        if valid_days.count() == 0:
            # 若 Angular 將數字欄位渲染為一般 input，退回 Modal 內最後一格。
            valid_days = dialog.locator("input").last
        expect(valid_days).to_be_visible()
        expect(valid_days).to_have_value("30")

        expect(
            dialog.get_by_text(
                "有效天數不可超過365天",
                exact=True,
            )
        ).to_be_visible()
        expect(
            dialog.get_by_role("button", name="取消", exact=True)
        ).to_be_visible()
        expect(
            dialog.get_by_role("button", name="確認", exact=True)
        ).to_be_visible()

    def cancel_add_api_key_modal(self) -> None:
        dialog = self.page.get_by_role("dialog")
        dialog.get_by_role("button", name="取消", exact=True).click()
        expect(dialog).not_to_be_visible()

    def open_system_log(self) -> None:
        self.open_section("系統日誌")

    def system_log_range_button(self) -> Locator:
        return self.page.get_by_role(
            "button",
            name="今天",
            exact=True,
        )

    def system_log_download_button(self) -> Locator:
        # Codegen 可能把圖示狀態併入 accessible name（例如 Selected），
        # 因此只比對穩定的按鈕文字。
        return self.page.get_by_role(
            "button",
            name=re.compile(r"下載日誌\s*zip檔$"),
        )

    def expect_system_log_static_content(self) -> None:
        expect(
            self.page.get_by_role(
                "heading",
                name="系統日誌",
                exact=True,
            )
        ).to_be_visible()
        expect(
            self.page.get_by_text(
                "若系統發生異常，請下載日誌並回報開發商，以協助排解問題",
                exact=True,
            )
        ).to_be_visible()
        expect(
            self.page.get_by_text(
                "請選取日誌時間範圍",
                exact=True,
            )
        ).to_be_visible()
        expect(self.system_log_range_button()).to_be_visible()
        expect(self.system_log_download_button()).to_be_visible()
        expect(
            self.page.get_by_text(
                "日誌包含系統運作紀錄，回報問題前請確認是否包含敏感資訊",
                exact=True,
            )
        ).to_be_visible()

    def open_system_log_range_menu(self) -> None:
        self.system_log_range_button().click()

        # 「最近3天」只有選單展開時才會顯示，可用來確認選單已開啟。
        option = self.visible_text("最近3天")
        if option is None:
            raise AssertionError("系統日誌時間範圍選單未展開")

        expect(option).to_be_visible()

    def expect_system_log_range_options_visible(self) -> None:
        for text in ("今天", "最近3天", "最近7天", "最近30天"):
            option = self.visible_text(text)
            if option is None:
                raise AssertionError(f"找不到日誌時間範圍選項：{text}")

            expect(option).to_be_visible()

    def close_system_log_range_menu(self) -> None:
        self.page.keyboard.press("Escape")
        expect(
            self.page.get_by_text("最近3天", exact=True).last
        ).not_to_be_visible()

    def download_system_log_zip(self) -> str:
        # 只確認瀏覽器收到下載事件與 zip 檔名；不開啟、不解壓縮、
        # 不另存日誌內容。Playwright 會在測試 Context 關閉時清理暫存檔。
        with self.page.expect_download(timeout=60_000) as download_info:
            self.system_log_download_button().click()

        return download_info.value.suggested_filename

    def open_ldap_settings(self) -> None:
        self.open_section("LDAP設定")

    def ldap_table(self) -> Locator:
        return self.page.get_by_role("table").first

    def expect_ldap_settings_static_content(self) -> None:
        expect(
            self.page.get_by_role(
                "heading",
                name="LDAP 設定",
                exact=True,
            )
        ).to_be_visible()
        expect(
            self.page.get_by_role(
                "button",
                name=re.compile(r"^\+\s*新增\s*LDAP\s*設定$"),
            )
        ).to_be_visible()

        table = self.ldap_table()
        expect(table).to_be_visible()

        for header in self.LDAP_TABLE_HEADERS:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

        # LDAP 設定可能尚未建立；靜態內容測試不要求存在資料列。

    def open_add_ldap_settings_page(self) -> None:
        # Codegen 目前取得的 accessible name 為「+ 新增LDAP設定」；
        # 使用可選空白的正規表示式，同時兼容畫面文字的排版空白。
        self.page.get_by_role(
            "button",
            name=re.compile(r"^\+\s*新增\s*LDAP\s*設定$"),
        ).click()
        expect(
            self.page.get_by_text("新增 LDAP 設定", exact=True)
        ).to_be_visible()

    def expect_ldap_form_fields(self) -> None:
        for label in self.LDAP_FORM_LABELS:
            expect(self.page.get_by_text(label).first).to_be_visible()

        expect(
            self.page.get_by_placeholder("ex: LDAP", exact=True)
        ).to_be_visible()
        expect(
            self.page.get_by_placeholder(
                "ex: ldap://dc1.company.com",
                exact=True,
            )
        ).to_be_visible()
        expect(
            self.page.get_by_placeholder(
                "ex: CN=Administrator,DC=company,DC=com",
                exact=True,
            )
        ).to_be_visible()
        expect(
            self.page.get_by_placeholder(
                "ex: CN=Users,DC=company,DC=com",
                exact=True,
            )
        ).to_be_visible()

    def expect_add_ldap_settings_page_content(self) -> None:
        self.expect_ldap_form_fields()
        expect(
            self.page.get_by_role(
                "button",
                name=re.compile(r"^返回\s*LDAP\s*設定$"),
            )
        ).to_be_visible()
        expect(
            self.page.get_by_role(
                "button",
                name="確認新增",
                exact=True,
            )
        ).to_be_visible()

    def return_to_ldap_settings(self) -> None:
        # Codegen 目前取得的 accessible name 為「返回LDAP設定」。
        self.page.get_by_role(
            "button",
            name=re.compile(r"^返回\s*LDAP\s*設定$"),
        ).click()
        expect(
            self.page.get_by_role(
                "heading",
                name="LDAP 設定",
                exact=True,
            )
        ).to_be_visible()

    def ldap_action_buttons(self) -> Locator:
        return self.ldap_table().get_by_role(
            "button",
            name="More Options",
            exact=True,
        )

    def has_ldap_rows(self) -> bool:
        """目前 LDAP 表格是否至少有一筆可操作的設定。"""
        return self.ldap_action_buttons().count() > 0

    def open_first_ldap_action_menu(self) -> None:
        self.ldap_action_buttons().first.click()

    def expect_ldap_action_menu_visible(self) -> None:
        for text in ("修改", "刪除"):
            option = self.visible_text(text)
            if option is None:
                raise AssertionError(f"找不到可見的功能選項：{text}")

            expect(option).to_be_visible()

    def open_first_ldap_edit_page(self) -> None:
        self.open_first_ldap_action_menu()
        edit_option = self.visible_text("修改")
        if edit_option is None:
            raise AssertionError("找不到可見的 LDAP 修改選項")

        edit_option.click()
        expect(
            self.page.get_by_text("修改 LDAP 設定", exact=True)
        ).to_be_visible()

    def expect_edit_ldap_settings_page_content(self) -> None:
        expect(
            self.page.get_by_text("一般設定", exact=True)
        ).to_be_visible()
        expect(
            self.page.get_by_text("Mapper 設定", exact=True)
        ).to_be_visible()
        self.expect_ldap_form_fields()

        for button_name in ("驗證", "確認修改"):
            expect(
                self.page.get_by_role(
                    "button",
                    name=button_name,
                    exact=True,
                )
            ).to_be_visible()

        expect(
            self.page.get_by_role(
                "button",
                name=re.compile(r"^返回\s*LDAP\s*設定$"),
            )
        ).to_be_visible()

    def overview_section(self, name: str) -> Locator:
        return (
            self.page.locator("section")
            .filter(has_text=self.OVERVIEW_SECTION_TEXT[name])
            .first
        )

    def expect_overview_static_content(self) -> None:
        expect(self.page.get_by_text("Token用量", exact=True)).to_be_visible()

        # 模型／日期篩選器是依資源或前端狀態變化的自製 Dropdown。
        # 舊版 accessible name 含 "Dropdown"，新版圖示 alt 可能改變；
        # 無已啟用模型的環境，也可能不顯示模型篩選器。
        # 此處只在找到「兩個舊版 Dropdown」時驗證；
        # 靜態內容測試不把選用型元件當成固定存在的先決條件。
        filters = self.page.get_by_role("button", name=re.compile(r"Dropdown"))
        if filters.count() == 2:
            expect(filters.nth(0)).to_be_visible()
            expect(filters.nth(1)).to_be_visible()
        elif filters.count() == 1:
            expect(filters.first).to_be_visible()
            print("總覽：僅找到一個舊版 Dropdown；另一個可能隱藏或名稱已改變")
        else:
            print("總覽：未找到名稱含 Dropdown 的按鈕；動態篩選器不列入靜態必備項目")

        for section_name in self.OVERVIEW_SECTIONS:
            expect(self.overview_section(section_name)).to_be_visible()
            self.expect_overview_section_expanded(section_name)

    def toggle_overview_section(self, name: str) -> None:
        section = self.overview_section(name)

        # 收合圖示目前沒有 accessible name，依 Codegen 結果縮小到區塊內定位。
        section.locator("i").click()

    def expect_overview_section_expanded(self, name: str) -> None:
        section = self.overview_section(name)

        for header in self.OVERVIEW_SECTIONS[name]:
            # 限定尋找表格欄位標題，避免「使用者」同時匹配區塊名稱與欄位名稱。
            expect(
                section.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

    def expect_overview_section_collapsed(self, name: str) -> None:
        section = self.overview_section(name)

        for header in self.OVERVIEW_SECTIONS[name]:
            # 即使欄位因收合而隱藏，仍精確定位表格欄位標題，
            # 避免同時選到「使用者」區塊標題。
            column_header = section.get_by_role(
                "columnheader",
                name=header,
                exact=True,
                include_hidden=True,
            )
            expect(column_header).not_to_be_visible()

    def open_section(self, name: str) -> None:
        item = self.menu_item(name)
        try:
            # goto() 只等待 domcontentloaded；Angular 側欄不一定已渲染。
            # 用 Playwright 自動等待，不靠固定 sleep。
            expect(item).to_be_visible(timeout=15_000)
        except AssertionError as exc:
            # 僅列出 URL path，不輸出可能帶有驗證資訊的 query string。
            path = urlsplit(self.page.url).path
            labels = [
                value.strip()[:80]
                for value in self.page.locator("button:visible").all_inner_texts()
                if value.strip()
            ][:25]
            raise AssertionError(
                f"管理側欄找不到「{name}」按鈕；"
                f"目前 URL path={path!r}；可見按鈕文字={labels!r}。"
                "請先確認是否停留在 /platform-manager、登入是否有效，"
                "或側欄按鈕的實際文字／role 是否已改變。"
            ) from exc

        item.click()

        expect(self.page).to_have_url(
            re.compile(r"/platform-manager(?:[/?#]|$)")
        )

        # 選單名稱與頁面標題可能不同，例如「LDAP設定」與「LDAP 設定」
        heading_name = self.SECTION_HEADINGS.get(name, name)

        # 確認右側主內容已切換，而不只是左側按鈕可以點擊
        expect(
            self.page.get_by_role(
                "heading",
                name=heading_name,
                exact=True,
            )
        ).to_be_visible(timeout=15_000)

    # 第二階段：AI 應用操作（集中於既有 PlatformManagerPage）
    def ai_app_row(self, name: str) -> Locator:
        rows = self.ai_application_table().locator("tbody tr")
        target = rows.filter(has=self.page.get_by_text(name, exact=True))
        expect(target).to_have_count(1)
        expect(target.locator("td").first).to_have_text(name)
        return target

    def ai_app_state(self, name: str) -> str:
        raw = self.ai_app_row(name).locator("td").nth(4).inner_text()
        state = re.sub(r"\s+", "", raw)
        if "啟用中" in state:
            return "enabling"
        if "停用中" in state:
            return "disabling"
        if "下載中" in state:
            return "downloading"
        if "未下載" in state:
            return "not_downloaded"
        if "已下載" in state and "未啟用" in state:
            return "downloaded_disabled"
        if "已啟用" in state:
            return "enabled"
        raise AssertionError(f"未知 AI 應用狀態：{raw!r}")

    def ai_app_choose_action(self, name: str, action: str) -> None:
        """指定 AI 應用的管理操作；操作前再次核對授權與目前狀態。"""
        allowed_states = {
            "下載": "not_downloaded",
            "啟用": "downloaded_disabled",
            "停用": "enabled",
        }
        if action not in allowed_states:
            raise ValueError("僅允許下載／啟用／停用；禁止刪除或修改權限")

        # 第二道防護：即使有人略過手動測試函式直接呼叫 Page Object，
        # 也不能在缺少授權的情況下載、啟用或停用後端服務。
        if os.getenv("AI_APP_TEST_WRITE") != "I_UNDERSTAND":
            raise PermissionError("AI 應用寫入操作未授權：缺少 AI_APP_TEST_WRITE=I_UNDERSTAND")
        if action == "下載" and os.getenv("AI_APP_TEST_ALLOW_DOWNLOAD") != "YES":
            raise PermissionError("下載未授權：需額外設定 AI_APP_TEST_ALLOW_DOWNLOAD=YES")
        if action == "停用" and os.getenv("AI_APP_TEST_ALLOW_DISABLE") != "YES":
            raise PermissionError("停用未授權：需額外設定 AI_APP_TEST_ALLOW_DISABLE=YES")

        current_state = self.ai_app_state(name)
        expected_state = allowed_states[action]
        if current_state != expected_state:
            raise AssertionError(
                f"拒絕 AI 應用「{action}」：{name} 目前狀態是 {current_state}，"
                f"預期為 {expected_state}。不重複點擊或強制改變狀態。"
            )

        row = self.ai_app_row(name)
        button = row.locator("td").last.locator("button.more-options-btn")
        expect(button).to_have_count(1)
        expect(button).to_be_visible()
        print(f"AI 應用 {name}：找到 ⋯ 按鈕，準備展開下拉選單")
        button.click()
        expect(button).to_have_attribute("aria-expanded", "true", timeout=5000)
        print(f"AI 應用 {name}：⋯ 下拉選單已展開")
        in_row = row.locator(".dropdown-menu.show:visible")
        menus = in_row if in_row.count() == 1 else self.page.locator(".dropdown-menu.show:visible")
        expect(menus).to_have_count(1, timeout=5000)
        option = menus.first.get_by_text(action, exact=True).filter(visible=True)
        expect(option).to_have_count(1, timeout=5000)
        expect(option).to_be_visible()
        print(f"AI 應用 {name}：已找到展開選單中的「{action}」，準備點擊")
        option.click()
        print(f"AI 應用 {name}：「{action}」點擊已執行，接著檢查狀態")

    def ai_app_snackbar_messages(self) -> list[str]:
        alerts = self.page.locator(
            "[role='alert']:visible, [role='status']:visible, "
            ".mat-mdc-snack-bar-container:visible, .snackbar:visible, .toast:visible"
        )
        return [s.strip() for s in alerts.all_inner_texts() if s.strip()]
