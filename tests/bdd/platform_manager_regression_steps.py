import pytest
from pytest_bdd import given, parsers, scenario, then, when

from pages.platform_manager_page import PlatformManagerPage


@scenario("platform_manager_regression.feature", "載入平台管理頁")
def test_platform_manager_is_loaded():
    pass


@scenario("platform_manager_regression.feature", "顯示平台管理主選單")
def test_main_menu_is_visible():
    pass


@scenario("platform_manager_regression.feature", "繁體中文與英文切換")
def test_interface_language_can_be_switched():
    pass


@scenario("platform_manager_regression.feature", "開啟平台管理主選單項目")
def test_main_menu_sections_can_be_opened():
    pass


@scenario("platform_manager_regression.feature", "顯示總覽主要內容")
def test_overview_static_content_is_visible():
    pass


@scenario("platform_manager_regression.feature", "總覽區塊可收合並重新展開")
def test_overview_section_can_be_collapsed_and_expanded():
    pass


@scenario("platform_manager_regression.feature", "顯示使用者管理內容")
def test_user_management_static_content_is_visible():
    pass


@scenario("platform_manager_regression.feature", "開啟並取消新增使用者")
def test_add_user_modal_can_be_opened_and_cancelled():
    pass


@scenario("platform_manager_regression.feature", "顯示使用者功能選單")
def test_user_action_menu_is_visible():
    pass


@scenario("platform_manager_regression.feature", "顯示群組管理內容")
def test_group_management_static_content_is_visible():
    pass


@scenario("platform_manager_regression.feature", "開啟新增群組頁並返回")
def test_add_group_page_can_be_opened_and_returned():
    pass


@scenario("platform_manager_regression.feature", "顯示群組功能選單")
def test_group_action_menu_is_visible():
    pass


@scenario("platform_manager_regression.feature", "顯示模型管理內容")
def test_model_management_static_content_is_visible():
    pass


@scenario("platform_manager_regression.feature", "展開與收合模型活動")
def test_model_activity_can_be_expanded_and_collapsed():
    pass


@scenario("platform_manager_regression.feature", "顯示模型功能選單")
def test_model_action_menu_is_visible():
    pass


@scenario("platform_manager_regression.feature", "顯示 LDAP 設定內容")
def test_ldap_settings_static_content_is_visible():
    pass


@scenario("platform_manager_regression.feature", "開啟新增 LDAP 設定頁並返回")
def test_add_ldap_settings_page_can_be_opened_and_returned():
    pass


@scenario("platform_manager_regression.feature", "顯示 LDAP 功能選單")
def test_ldap_action_menu_is_visible():
    pass


@scenario("platform_manager_regression.feature", "開啟 LDAP 修改頁並返回")
def test_edit_ldap_settings_page_is_visible():
    pass


@scenario("platform_manager_regression.feature", "顯示 AI 應用管理內容")
def test_ai_application_management_static_content_is_visible():
    pass


@scenario("platform_manager_regression.feature", "顯示 AI 應用功能選單")
def test_ai_application_action_menu_is_visible():
    pass


@scenario("platform_manager_regression.feature", "顯示 API 端點內容")
def test_api_endpoint_static_content_is_visible():
    pass


@scenario("platform_manager_regression.feature", "查看已啟用的 API 端點明細")
def test_enabled_api_endpoint_details_are_visible():
    pass


@scenario("platform_manager_regression.feature", "顯示 API 金鑰管理內容")
def test_api_key_management_static_content_is_visible():
    pass


@scenario("platform_manager_regression.feature", "顯示 API 金鑰功能選單")
def test_api_key_action_menu_is_visible():
    pass


@scenario("platform_manager_regression.feature", "開啟並取消新增 API 金鑰")
def test_add_api_key_modal_can_be_opened_and_cancelled():
    pass


@scenario("platform_manager_regression.feature", "顯示系統日誌內容")
def test_system_log_static_content_is_visible():
    pass


@scenario("platform_manager_regression.feature", "顯示系統日誌時間範圍選項")
def test_system_log_range_options_are_visible():
    pass


@scenario("platform_manager_regression.feature", "下載系統日誌 ZIP")
def test_system_log_zip_can_be_downloaded():
    pass


@given('我已使用本輪登入狀態開啟平台管理頁', target_fixture='manager')
def open_page(authenticated_page):
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    return manager


@then('頁面應載入完成')
def expect_loaded(manager):
    manager.expect_loaded()


@then('主選單應可見')
def expect_main_menu_visible(manager):
    manager.expect_main_menu_visible()


@then('介面應顯示繁體中文')
def expect_chinese_interface(manager):
    manager.expect_chinese_interface()


@when('我將介面語言切換為「English」')
def switch_language_english(manager):
    manager.switch_language(current_language='繁體中文', target_language='English')


@then('介面應顯示英文')
def expect_english_interface(manager):
    manager.expect_english_interface()


@when('我將介面語言切換為「繁體中文」')
def switch_language_chinese(manager):
    manager.switch_language(current_language='English', target_language='繁體中文')


@when(parsers.parse('我開啟主選單的「{section}」'))
def open_section(manager, section):
    manager.open_section(section)


@when('我開啟總覽')
def open_overview(manager):
    manager.open_overview()


@then('總覽應顯示既有欄位與操作入口')
def expect_overview_static_content(manager):
    manager.expect_overview_static_content()


@then(parsers.parse('「{section}」區塊應展開'))
def expect_overview_section_expanded(manager, section):
    manager.expect_overview_section_expanded(section)


@when(parsers.parse('我切換「{section}」區塊的展開狀態'))
def toggle_overview_section(manager, section):
    manager.toggle_overview_section(section)


@then(parsers.parse('「{section}」區塊應收合'))
def expect_overview_section_collapsed(manager, section):
    manager.expect_overview_section_collapsed(section)


@when('我開啟使用者管理')
def open_user_management(manager):
    manager.open_user_management()


@then('使用者管理應顯示既有欄位與操作入口')
def expect_user_management_static_content(manager):
    manager.expect_user_management_static_content()


@when('我開啟新增使用者視窗')
def open_add_user_modal(manager):
    manager.open_add_user_modal()


@then('新增使用者視窗應顯示預期欄位')
def expect_add_user_modal_content(manager):
    manager.expect_add_user_modal_content()


@when('我取消新增使用者')
def cancel_add_user_modal(manager):
    manager.cancel_add_user_modal()


@when('我開啟第一筆使用者的功能選單')
def open_first_user_action_menu(manager):
    manager.open_first_user_action_menu()


@then('使用者的功能選單應顯示預期選項')
def expect_user_action_menu_visible(manager):
    manager.expect_user_action_menu_visible()


@when('我開啟群組管理')
def open_group_management(manager):
    manager.open_group_management()


@then('群組管理應顯示既有欄位與操作入口')
def expect_group_management_static_content(manager):
    manager.expect_group_management_static_content()


@when('我開啟新增群組頁')
def open_add_group_page(manager):
    manager.open_add_group_page()


@then('新增群組頁應顯示預期欄位')
def expect_add_group_page_content(manager):
    manager.expect_add_group_page_content()


@when('我返回群組管理')
def return_to_group_management(manager):
    manager.return_to_group_management()


@given('環境有群組資料')
def require_group_rows(manager):
    if not manager.has_group_rows():
        pytest.skip('目前測試環境沒有群組資料，略過群組功能選單測試')


@when('我開啟第一筆群組的功能選單')
def open_first_group_action_menu(manager):
    manager.open_first_group_action_menu()


@then('群組的功能選單應顯示預期選項')
def expect_group_action_menu_visible(manager):
    manager.expect_group_action_menu_visible()


@when('我開啟模型管理')
def open_model_management(manager):
    manager.open_model_management()


@then('模型管理應顯示既有欄位與操作入口')
def expect_model_management_static_content(manager):
    manager.expect_model_management_static_content()


@when('我展開模型活動')
def open_model_activity(manager):
    manager.open_model_activity()


@when('我收合模型活動')
def close_model_activity(manager):
    manager.close_model_activity()


@given('環境有模型資料')
def require_model_rows(manager):
    if not manager.has_model_rows():
        pytest.skip('目前測試環境沒有模型資料，略過模型功能選單測試')


@when('我開啟第一筆模型的功能選單')
def open_first_model_action_menu(manager):
    manager.open_first_model_action_menu()


@then('模型的功能選單應顯示預期選項')
def expect_model_action_menu_visible(manager):
    manager.expect_model_action_menu_visible()


@when('我開啟LDAP 設定')
def open_ldap_settings(manager):
    manager.open_ldap_settings()


@then('LDAP 設定應顯示既有欄位與操作入口')
def expect_ldap_settings_static_content(manager):
    manager.expect_ldap_settings_static_content()


@when('我開啟新增 LDAP 設定頁')
def open_add_ldap_settings_page(manager):
    manager.open_add_ldap_settings_page()


@then('新增 LDAP 設定頁應顯示預期欄位')
def expect_add_ldap_settings_page_content(manager):
    manager.expect_add_ldap_settings_page_content()


@when('我返回 LDAP 設定')
def return_to_ldap_settings(manager):
    manager.return_to_ldap_settings()


@given('環境有 LDAP 資料')
def require_ldap_rows(manager):
    if not manager.has_ldap_rows():
        pytest.skip('目前測試環境沒有 LDAP 資料，略過 LDAP 功能選單測試')


@when('我開啟第一筆LDAP的功能選單')
def open_first_ldap_action_menu(manager):
    manager.open_first_ldap_action_menu()


@then('LDAP的功能選單應顯示預期選項')
def expect_ldap_action_menu_visible(manager):
    manager.expect_ldap_action_menu_visible()


@when('我開啟第一筆 LDAP 的修改頁')
def open_first_ldap_edit_page(manager):
    manager.open_first_ldap_edit_page()


@then('修改 LDAP 設定頁應顯示預期欄位')
def expect_edit_ldap_settings_page_content(manager):
    manager.expect_edit_ldap_settings_page_content()


@when('我開啟AI 應用管理')
def open_ai_application_management(manager):
    manager.open_ai_application_management()


@then('AI 應用管理應顯示既有欄位與操作入口')
def expect_ai_application_management_static_content(manager):
    manager.expect_ai_application_management_static_content()


@given('環境有 AI 應用資料')
def require_ai_application_rows(manager):
    if not manager.has_ai_application_rows():
        pytest.skip('目前測試環境沒有 AI 應用資料，略過功能選單測試')


@when('我開啟第一筆AI 應用的功能選單')
def open_first_ai_application_action_menu(manager):
    manager.open_first_ai_application_action_menu()


@then('AI 應用的功能選單應顯示預期選項')
def expect_ai_application_action_menu_visible(manager):
    manager.expect_ai_application_action_menu_visible()


@when('我開啟API 端點')
def open_api_endpoint(manager):
    manager.open_api_endpoint()


@then('API 端點應顯示既有欄位與操作入口')
def expect_api_endpoint_static_content(manager):
    manager.expect_api_endpoint_static_content()


@given('環境有已啟用的 API 端點')
def require_api_endpoint_rows(manager):
    if not manager.has_api_endpoint_rows():
        pytest.skip('目前 API 端點未啟用或沒有資料，略過端點明細測試')


@then('應顯示已啟用 API 端點的明細')
def expect_enabled_api_endpoint_details(manager):
    manager.expect_enabled_api_endpoint_details()


@when('我開啟API 金鑰管理')
def open_api_key_management(manager):
    manager.open_api_key_management()


@then('API 金鑰管理應顯示既有欄位與操作入口')
def expect_api_key_management_static_content(manager):
    manager.expect_api_key_management_static_content()


@given('環境有 API 金鑰資料')
def require_api_key_rows(manager):
    if not manager.has_api_key_rows():
        pytest.skip('目前測試環境沒有 API 金鑰資料，略過功能選單測試')


@when('我開啟第一筆API 金鑰的功能選單')
def open_first_api_key_action_menu(manager):
    manager.open_first_api_key_action_menu()


@then('API 金鑰的功能選單應顯示預期選項')
def expect_api_key_action_menu_visible(manager):
    manager.expect_api_key_action_menu_visible()


@when('我開啟新增 API 金鑰視窗')
def open_add_api_key_modal(manager):
    manager.open_add_api_key_modal()


@then('新增 API 金鑰視窗應顯示預期欄位')
def expect_add_api_key_modal_content(manager):
    manager.expect_add_api_key_modal_content()


@when('我取消新增 API 金鑰')
def cancel_add_api_key_modal(manager):
    manager.cancel_add_api_key_modal()


@when('我開啟系統日誌')
def open_system_log(manager):
    manager.open_system_log()


@then('系統日誌應顯示既有欄位與操作入口')
def expect_system_log_static_content(manager):
    manager.expect_system_log_static_content()


@when('我開啟系統日誌時間範圍選單')
def open_system_log_range_menu(manager):
    manager.open_system_log_range_menu()


@then('應顯示系統日誌的時間範圍選項')
def expect_system_log_range_options_visible(manager):
    manager.expect_system_log_range_options_visible()


@when('我關閉系統日誌時間範圍選單')
def close_system_log_range_menu(manager):
    manager.close_system_log_range_menu()


@when('我下載系統日誌', target_fixture='suggested_filename')
def download_log(manager):
    return manager.download_system_log_zip()


@then('下載的日誌檔名應以 .zip 結尾')
def check_zip(suggested_filename):
    assert suggested_filename.lower().endswith('.zip'), f'預期下載 zip 日誌，實際檔名：{suggested_filename}'
