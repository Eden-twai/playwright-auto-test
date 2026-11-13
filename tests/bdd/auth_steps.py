"""獨立執行登入／登出的 Gherkin 情境。"""

from pytest_bdd import scenarios, then, when

from scripts.save_login_state import (
    click_logout,
    expect_login_required,
    revisit_management_page,
)

scenarios("auth.feature")


@when("我從帳號設定選單登出")
def sign_out(auth_page, auth_config):
    click_logout(auth_page, auth_config)


@when("我再次開啟管理頁")
def revisit(auth_page):
    revisit_management_page(auth_page)


@then("頁面應要求重新登入")
def check_login_required(auth_page, auth_config):
    expect_login_required(auth_page, auth_config)
