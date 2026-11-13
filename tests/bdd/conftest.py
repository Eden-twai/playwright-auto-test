"""共用 Gherkin 登入工作階段與即時步驟輸出。"""

import os

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pytest_bdd import given

from scripts.save_login_state import (
    AUTH_SLOW_MO_MS,
    PROJECT_ROOT,
    automatic_login,
    confirm_logged_in,
    revisit_management_page,
    settings_from_env,
)


@pytest.fixture
def auth_config():
    load_dotenv(PROJECT_ROOT / ".env")
    return settings_from_env(auto=not os.getenv("AI_HUB_AUTH_STATE"))


@pytest.fixture
def auth_page(auth_config, request):
    if os.getenv("AI_HUB_AUTH_STATE"):
        page = request.getfixturevalue("authenticated_page")
        page.set_default_timeout(auth_config.timeout_ms)
        yield page
        return

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, slow_mo=AUTH_SLOW_MO_MS)
        try:
            context = browser.new_context(
                base_url=auth_config.base_url,
                ignore_https_errors=True,
                locale="zh-TW",
                viewport={"width": 1440, "height": 900},
            )
            try:
                page = context.new_page()
                page.set_default_timeout(auth_config.timeout_ms)
                yield page
            finally:
                context.close()
        finally:
            browser.close()


@given("我已使用測試帳號登入 AI Hub")
def sign_in(auth_page, auth_config):
    revisit_management_page(auth_page)
    if os.getenv("AI_HUB_AUTH_STATE"):
        confirm_logged_in(auth_page, auth_config)
    else:
        automatic_login(auth_page, auth_config)


def pytest_bdd_before_step(request, feature, scenario, step, step_func):
    if request.config.getoption("capture") == "no":
        print(f"\n▶ {step.keyword} {step.name}", flush=True)
