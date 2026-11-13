Feature: AI Hub 登入與登出

  Scenario: 登出後回訪管理頁需要重新登入
    Given 我已使用測試帳號登入 AI Hub
    When 我從帳號設定選單登出
    And 我再次開啟管理頁
    Then 頁面應要求重新登入
