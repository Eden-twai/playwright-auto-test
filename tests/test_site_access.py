import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_platform_manager_endpoint_has_no_server_error(page: Page) -> None:
    response = page.goto("/platform-manager", wait_until="domcontentloaded")

    assert response is not None, "瀏覽器沒有收到任何 HTTP 回應"
    assert response.status < 500, f"伺服器回傳錯誤狀態：{response.status}"
    expect(page.locator("body")).to_be_visible()
