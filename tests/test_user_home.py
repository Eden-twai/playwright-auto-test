import pytest
from playwright.sync_api import Page

from pages.user_home_page import UserHomePage


@pytest.mark.smoke
@pytest.mark.auth
def test_user_home_is_loaded(authenticated_page: Page) -> None:
    home = UserHomePage(authenticated_page)

    home.goto()

    home.expect_loaded()


@pytest.mark.smoke
@pytest.mark.auth
def test_user_sidebar_is_visible(authenticated_page: Page) -> None:
    home = UserHomePage(authenticated_page)
    home.goto()

    home.expect_sidebar_visible()


@pytest.mark.auth
def test_user_home_static_content_is_visible(
    authenticated_page: Page,
) -> None:
    home = UserHomePage(authenticated_page)
    home.goto()

    home.expect_home_content_visible()


@pytest.mark.auth
def test_model_menu_can_be_opened(authenticated_page: Page) -> None:
    home = UserHomePage(authenticated_page)
    home.goto()

    home.open_model_menu()
    home.expect_model_menu_visible()


@pytest.mark.auth
def test_prompt_library_can_be_opened_and_returned(
    authenticated_page: Page,
) -> None:
    home = UserHomePage(authenticated_page)
    home.goto()

    home.open_prompt_library()
    home.expect_prompt_library_static_content()
    home.open_new_chat()


@pytest.mark.auth
def test_ai_apps_can_be_opened_and_returned(
    authenticated_page: Page,
) -> None:
    home = UserHomePage(authenticated_page)
    home.goto()

    home.open_ai_apps()
    home.expect_ai_apps_static_content()
    home.open_new_chat()


@pytest.mark.auth
def test_account_settings_menu_is_visible(
    authenticated_page: Page,
) -> None:
    home = UserHomePage(authenticated_page)
    home.goto()

    home.open_account_settings()
    home.expect_account_settings_menu_visible()
