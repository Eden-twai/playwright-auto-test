@auth
Feature: 使用者首頁回歸

  @smoke
  Scenario: 載入使用者首頁
    Given 我已使用本輪登入狀態開啟使用者首頁
    Then 頁面應載入完成

  @smoke
  Scenario: 顯示使用者側欄
    Given 我已使用本輪登入狀態開啟使用者首頁
    Then 側欄應可見

  Scenario: 顯示使用者首頁內容
    Given 我已使用本輪登入狀態開啟使用者首頁
    Then 首頁應顯示主要內容

  Scenario: 開啟模型選單
    Given 我已使用本輪登入狀態開啟使用者首頁
    When 我開啟對話模型選單
    Then 對話模型選單應可見

  Scenario: 開啟提示詞庫並返回
    Given 我已使用本輪登入狀態開啟使用者首頁
    When 我開啟提示詞庫
    Then 應顯示提示詞表格與新增按鈕
    When 我回到新對話首頁

  Scenario: 開啟 AI 應用並返回
    Given 我已使用本輪登入狀態開啟使用者首頁
    When 我開啟 AI 應用
    Then 應顯示 AI 應用卡片與開始使用按鈕
    When 我回到新對話首頁

  Scenario: 顯示帳號及設定選單
    Given 我已使用本輪登入狀態開啟使用者首頁
    When 我開啟帳號及設定
    Then 帳號及設定選項應可見
