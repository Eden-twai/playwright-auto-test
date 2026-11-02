import pytest
from playwright.sync_api import Page

from pages.platform_manager_page import PlatformManagerPage


@pytest.mark.smoke
@pytest.mark.auth
def test_platform_manager_is_loaded(authenticated_page: Page) -> None:
    manager = PlatformManagerPage(authenticated_page)

    manager.goto()

    manager.expect_loaded()


@pytest.mark.smoke
@pytest.mark.auth
def test_main_menu_is_visible(authenticated_page: Page) -> None:
    manager = PlatformManagerPage(authenticated_page)

    manager.goto()

    manager.expect_main_menu_visible()


@pytest.mark.auth
def test_interface_language_can_be_switched(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()

    manager.expect_chinese_interface()

    manager.switch_language(
        current_language="繁體中文",
        target_language="English",
    )
    manager.expect_english_interface()

    manager.switch_language(
        current_language="English",
        target_language="繁體中文",
    )
    manager.expect_chinese_interface()


@pytest.mark.auth
@pytest.mark.parametrize(
    "section",
    PlatformManagerPage.MENU_ITEMS[1:],
    ids=lambda section: section.lower().replace(" ", "-"),
)
def test_main_menu_sections_can_be_opened(
    authenticated_page: Page, section: str
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()

    manager.open_section(section)


@pytest.mark.auth
def test_overview_static_content_is_visible(authenticated_page: Page) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()

    manager.open_overview()

    manager.expect_overview_static_content()


@pytest.mark.auth
@pytest.mark.parametrize(
    "section",
    PlatformManagerPage.OVERVIEW_SECTIONS,
    ids=lambda section: section.lower().replace(" ", "-"),
)
def test_overview_section_can_be_collapsed_and_expanded(
    authenticated_page: Page, section: str
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_overview()

    manager.expect_overview_section_expanded(section)

    manager.toggle_overview_section(section)
    manager.expect_overview_section_collapsed(section)

    manager.toggle_overview_section(section)
    manager.expect_overview_section_expanded(section)


@pytest.mark.auth
def test_user_management_static_content_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()

    manager.open_user_management()
    manager.expect_user_management_static_content()


@pytest.mark.auth
def test_add_user_modal_can_be_opened_and_cancelled(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_user_management()

    manager.open_add_user_modal()
    manager.expect_add_user_modal_content()
    manager.cancel_add_user_modal()


@pytest.mark.auth
def test_user_action_menu_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_user_management()

    manager.open_first_user_action_menu()
    manager.expect_user_action_menu_visible()


@pytest.mark.auth
def test_group_management_static_content_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()

    manager.open_group_management()
    manager.expect_group_management_static_content()


@pytest.mark.auth
def test_add_group_page_can_be_opened_and_returned(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_group_management()

    manager.open_add_group_page()
    manager.expect_add_group_page_content()
    manager.return_to_group_management()


@pytest.mark.auth
def test_group_action_menu_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_group_management()

    if not manager.has_group_rows():
        pytest.skip("目前測試環境沒有群組資料，略過群組功能選單測試")

    manager.open_first_group_action_menu()
    manager.expect_group_action_menu_visible()


@pytest.mark.auth
def test_model_management_static_content_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()

    manager.open_model_management()
    manager.expect_model_management_static_content()


@pytest.mark.auth
def test_model_activity_can_be_expanded_and_collapsed(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_model_management()

    manager.open_model_activity()
    manager.close_model_activity()


@pytest.mark.auth
def test_model_action_menu_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_model_management()

    if not manager.has_model_rows():
        pytest.skip("目前測試環境沒有模型資料，略過模型功能選單測試")

    manager.open_first_model_action_menu()
    manager.expect_model_action_menu_visible()


@pytest.mark.auth
def test_ldap_settings_static_content_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()

    manager.open_ldap_settings()
    manager.expect_ldap_settings_static_content()


@pytest.mark.auth
def test_add_ldap_settings_page_can_be_opened_and_returned(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_ldap_settings()

    manager.open_add_ldap_settings_page()
    manager.expect_add_ldap_settings_page_content()
    manager.return_to_ldap_settings()


@pytest.mark.auth
def test_ldap_action_menu_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_ldap_settings()

    if not manager.has_ldap_rows():
        pytest.skip("目前測試環境沒有 LDAP 資料，略過 LDAP 功能選單測試")

    manager.open_first_ldap_action_menu()
    manager.expect_ldap_action_menu_visible()


@pytest.mark.auth
def test_edit_ldap_settings_page_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_ldap_settings()

    if not manager.has_ldap_rows():
        pytest.skip("目前測試環境沒有 LDAP 資料，略過 LDAP 修改頁面測試")

    manager.open_first_ldap_edit_page()
    manager.expect_edit_ldap_settings_page_content()
    manager.return_to_ldap_settings()


@pytest.mark.auth
def test_ai_application_management_static_content_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()

    manager.open_ai_application_management()
    manager.expect_ai_application_management_static_content()


@pytest.mark.auth
def test_ai_application_action_menu_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_ai_application_management()

    if not manager.has_ai_application_rows():
        pytest.skip("目前測試環境沒有 AI 應用資料，略過功能選單測試")

    manager.open_first_ai_application_action_menu()
    manager.expect_ai_application_action_menu_visible()


@pytest.mark.auth
def test_api_endpoint_static_content_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()

    manager.open_api_endpoint()
    manager.expect_api_endpoint_static_content()


@pytest.mark.auth
def test_enabled_api_endpoint_details_are_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_api_endpoint()

    if not manager.has_api_endpoint_rows():
        pytest.skip("目前 API 端點未啟用或沒有資料，略過端點明細測試")

    manager.expect_enabled_api_endpoint_details()


@pytest.mark.auth
def test_api_key_management_static_content_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()

    manager.open_api_key_management()
    manager.expect_api_key_management_static_content()


@pytest.mark.auth
def test_api_key_action_menu_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_api_key_management()

    if not manager.has_api_key_rows():
        pytest.skip("目前測試環境沒有 API 金鑰資料，略過功能選單測試")

    manager.open_first_api_key_action_menu()
    manager.expect_api_key_action_menu_visible()


@pytest.mark.auth
def test_add_api_key_modal_can_be_opened_and_cancelled(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_api_key_management()

    manager.open_add_api_key_modal()
    manager.expect_add_api_key_modal_content()
    manager.cancel_add_api_key_modal()


@pytest.mark.auth
def test_system_log_static_content_is_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()

    manager.open_system_log()
    manager.expect_system_log_static_content()


@pytest.mark.auth
def test_system_log_range_options_are_visible(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_system_log()

    manager.open_system_log_range_menu()
    manager.expect_system_log_range_options_visible()
    manager.close_system_log_range_menu()


@pytest.mark.auth
def test_system_log_zip_can_be_downloaded(
    authenticated_page: Page,
) -> None:
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_system_log()

    suggested_filename = manager.download_system_log_zip()

    assert suggested_filename.lower().endswith(".zip"), (
        f"預期下載 zip 日誌，實際檔名：{suggested_filename}"
    )
