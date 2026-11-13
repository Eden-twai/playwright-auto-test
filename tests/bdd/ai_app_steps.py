"""獨立執行 AFS MyAgent 啟用與使用入口的 Gherkin 情境。"""

import pytest
from pytest_bdd import given, scenarios, then, when

from pages.user_home_page import UserHomePage
from tests.manual_ai_application_activation import (
    TARGET_APP,
    activate_ai_app,
    expect_ai_app_enabled,
    open_ai_app_management,
    require_ai_app_write,
)

scenarios("ai_app.feature")


@pytest.fixture(autouse=True)
def check_write_permission():
    require_ai_app_write()


@given("我已開啟 AI 應用管理", target_fixture="app_manager")
def open_management(auth_page):
    return open_ai_app_management(auth_page)


@when("我依目前狀態啟用 AFS MyAgent")
def activate(app_manager):
    activate_ai_app(app_manager)


@then("AFS MyAgent 應顯示為已啟用")
def check_enabled(app_manager):
    expect_ai_app_enabled(app_manager)


@then("使用者介面應顯示 AFS MyAgent 的開始使用入口", target_fixture="app_home")
def check_entry(auth_page):
    home = UserHomePage(auth_page)
    home.expect_ai_app_entry(TARGET_APP)
    return home


@when("我點擊 AFS MyAgent 的開始使用", target_fixture="app_navigation")
def click_start(app_home):
    return app_home.start_ai_app(TARGET_APP)


@then("應切換至應用畫面或開啟新分頁")
def check_navigation(app_home, app_navigation):
    app_home.expect_ai_app_started(TARGET_APP, app_navigation)
