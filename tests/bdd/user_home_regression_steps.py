from pytest_bdd import given, scenario, then, when

from pages.user_home_page import UserHomePage


@scenario("user_home_regression.feature", "載入使用者首頁")
def test_user_home_is_loaded():
    pass


@scenario("user_home_regression.feature", "顯示使用者側欄")
def test_user_sidebar_is_visible():
    pass


@scenario("user_home_regression.feature", "顯示使用者首頁內容")
def test_user_home_static_content_is_visible():
    pass


@scenario("user_home_regression.feature", "開啟模型選單")
def test_model_menu_can_be_opened():
    pass


@scenario("user_home_regression.feature", "開啟提示詞庫並返回")
def test_prompt_library_can_be_opened_and_returned():
    pass


@scenario("user_home_regression.feature", "開啟 AI 應用並返回")
def test_ai_apps_can_be_opened_and_returned():
    pass


@scenario("user_home_regression.feature", "顯示帳號及設定選單")
def test_account_settings_menu_is_visible():
    pass


@given('我已使用本輪登入狀態開啟使用者首頁', target_fixture='home')
def open_page(authenticated_page):
    home = UserHomePage(authenticated_page)
    home.goto()
    return home


@then('頁面應載入完成')
def expect_loaded(home):
    home.expect_loaded()


@then('側欄應可見')
def expect_sidebar_visible(home):
    home.expect_sidebar_visible()


@then('首頁應顯示主要內容')
def expect_home_content_visible(home):
    home.expect_home_content_visible()


@when('我開啟對話模型選單')
def open_model_menu(home):
    home.open_model_menu()


@then('對話模型選單應可見')
def expect_model_menu_visible(home):
    home.expect_model_menu_visible()


@when('我開啟提示詞庫')
def open_prompt_library(home):
    home.open_prompt_library()


@then('應顯示提示詞表格與新增按鈕')
def expect_prompt_library_static_content(home):
    home.expect_prompt_library_static_content()


@when('我回到新對話首頁')
def open_new_chat(home):
    home.open_new_chat()


@when('我開啟 AI 應用')
def open_ai_apps(home):
    home.open_ai_apps()


@then('應顯示 AI 應用卡片與開始使用按鈕')
def expect_ai_apps_static_content(home):
    home.expect_ai_apps_static_content()


@when('我開啟帳號及設定')
def open_account_settings(home):
    home.open_account_settings()


@then('帳號及設定選項應可見')
def expect_account_settings_menu_visible(home):
    home.expect_account_settings_menu_visible()
