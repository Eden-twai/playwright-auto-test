from playwright.sync_api import expect
from pytest_bdd import scenario, then, when


@scenario("site_access_regression.feature", "平台管理入口可回應且頁面可顯示")
def test_platform_manager_endpoint_has_no_server_error():
    pass


@when("我開啟平台管理入口", target_fixture="response")
def open_management_endpoint(page):
    return page.goto("/platform-manager", wait_until="domcontentloaded")


@then("應收到低於 500 的 HTTP 狀態且頁面可見")
def check_endpoint_response(page, response):
    assert response is not None, "瀏覽器沒有收到任何 HTTP 回應"
    assert response.status < 500, f"伺服器回傳錯誤狀態：{response.status}"
    expect(page.locator("body")).to_be_visible()
