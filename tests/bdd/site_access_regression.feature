Feature: 站台連線回歸

  @smoke
  Scenario: 平台管理入口可回應且頁面可顯示
    When 我開啟平台管理入口
    Then 應收到低於 500 的 HTTP 狀態且頁面可見
