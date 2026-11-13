Feature: AI Hub 的 AFS MyAgent 啟用與使用入口

  Scenario: 確認 AFS MyAgent 已啟用並可從使用者介面開始使用
    Given 我已使用測試帳號登入 AI Hub
    And 我已開啟 AI 應用管理
    When 我依目前狀態啟用 AFS MyAgent
    Then AFS MyAgent 應顯示為已啟用
    And 使用者介面應顯示 AFS MyAgent 的開始使用入口
    When 我點擊 AFS MyAgent 的開始使用
    Then 應切換至應用畫面或開啟新分頁
