Feature: AI Hub 模型啟用與對話歷史

  Scenario: 確認模型已啟用並從歷史重開新對話
    Given 我已使用測試帳號登入 AI Hub
    And 目標模型已下載且可操作
    When 我依目前狀態啟用目標模型
    Then 目標模型應顯示為已啟用
    When 我選取目標模型並送出一則新對話
    Then 應建立新的對話並收到非空白回覆
    When 我從歷史紀錄重開這則對話
    Then 應回到同一則對話並看到原訊息與回覆
