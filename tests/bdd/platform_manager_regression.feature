@auth
Feature: 平台管理回歸

  @smoke
  Scenario: 載入平台管理頁
    Given 我已使用本輪登入狀態開啟平台管理頁
    Then 頁面應載入完成

  @smoke
  Scenario: 顯示平台管理主選單
    Given 我已使用本輪登入狀態開啟平台管理頁
    Then 主選單應可見

  Scenario: 繁體中文與英文切換
    Given 我已使用本輪登入狀態開啟平台管理頁
    Then 介面應顯示繁體中文
    When 我將介面語言切換為「English」
    Then 介面應顯示英文
    When 我將介面語言切換為「繁體中文」
    Then 介面應顯示繁體中文

  Scenario Outline: 開啟平台管理主選單項目
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟主選單的「<section>」

    Examples:
      | section |
      | 使用者管理 |
      | 群組管理 |
      | LDAP設定 |
      | 模型管理 |
      | AI應用管理 |
      | API 端點 |
      | API 金鑰管理 |
      | 系統日誌 |

  Scenario: 顯示總覽主要內容
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟總覽
    Then 總覽應顯示既有欄位與操作入口

  Scenario Outline: 總覽區塊可收合並重新展開
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟總覽
    Then 「<section>」區塊應展開
    When 我切換「<section>」區塊的展開狀態
    Then 「<section>」區塊應收合
    When 我切換「<section>」區塊的展開狀態
    Then 「<section>」區塊應展開

    Examples:
      | section |
      | 使用者 |
      | API Key |
      | 群組 |

  Scenario: 顯示使用者管理內容
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟使用者管理
    Then 使用者管理應顯示既有欄位與操作入口

  Scenario: 開啟並取消新增使用者
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟使用者管理
    And 我開啟新增使用者視窗
    Then 新增使用者視窗應顯示預期欄位
    When 我取消新增使用者

  Scenario: 顯示使用者功能選單
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟使用者管理
    And 我開啟第一筆使用者的功能選單
    Then 使用者的功能選單應顯示預期選項

  Scenario: 顯示群組管理內容
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟群組管理
    Then 群組管理應顯示既有欄位與操作入口

  Scenario: 開啟新增群組頁並返回
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟群組管理
    And 我開啟新增群組頁
    Then 新增群組頁應顯示預期欄位
    When 我返回群組管理

  Scenario: 顯示群組功能選單
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟群組管理
    Given 環境有群組資料
    When 我開啟第一筆群組的功能選單
    Then 群組的功能選單應顯示預期選項

  Scenario: 顯示模型管理內容
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟模型管理
    Then 模型管理應顯示既有欄位與操作入口

  Scenario: 展開與收合模型活動
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟模型管理
    And 我展開模型活動
    And 我收合模型活動

  Scenario: 顯示模型功能選單
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟模型管理
    Given 環境有模型資料
    When 我開啟第一筆模型的功能選單
    Then 模型的功能選單應顯示預期選項

  Scenario: 顯示 LDAP 設定內容
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟LDAP 設定
    Then LDAP 設定應顯示既有欄位與操作入口

  Scenario: 開啟新增 LDAP 設定頁並返回
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟LDAP 設定
    And 我開啟新增 LDAP 設定頁
    Then 新增 LDAP 設定頁應顯示預期欄位
    When 我返回 LDAP 設定

  Scenario: 顯示 LDAP 功能選單
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟LDAP 設定
    Given 環境有 LDAP 資料
    When 我開啟第一筆LDAP的功能選單
    Then LDAP的功能選單應顯示預期選項

  Scenario: 開啟 LDAP 修改頁並返回
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟LDAP 設定
    Given 環境有 LDAP 資料
    When 我開啟第一筆 LDAP 的修改頁
    Then 修改 LDAP 設定頁應顯示預期欄位
    When 我返回 LDAP 設定

  Scenario: 顯示 AI 應用管理內容
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟AI 應用管理
    Then AI 應用管理應顯示既有欄位與操作入口

  Scenario: 顯示 AI 應用功能選單
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟AI 應用管理
    Given 環境有 AI 應用資料
    When 我開啟第一筆AI 應用的功能選單
    Then AI 應用的功能選單應顯示預期選項

  Scenario: 顯示 API 端點內容
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟API 端點
    Then API 端點應顯示既有欄位與操作入口

  Scenario: 查看已啟用的 API 端點明細
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟API 端點
    Given 環境有已啟用的 API 端點
    Then 應顯示已啟用 API 端點的明細

  Scenario: 顯示 API 金鑰管理內容
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟API 金鑰管理
    Then API 金鑰管理應顯示既有欄位與操作入口

  Scenario: 顯示 API 金鑰功能選單
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟API 金鑰管理
    Given 環境有 API 金鑰資料
    When 我開啟第一筆API 金鑰的功能選單
    Then API 金鑰的功能選單應顯示預期選項

  Scenario: 開啟並取消新增 API 金鑰
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟API 金鑰管理
    And 我開啟新增 API 金鑰視窗
    Then 新增 API 金鑰視窗應顯示預期欄位
    When 我取消新增 API 金鑰

  Scenario: 顯示系統日誌內容
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟系統日誌
    Then 系統日誌應顯示既有欄位與操作入口

  Scenario: 顯示系統日誌時間範圍選項
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟系統日誌
    And 我開啟系統日誌時間範圍選單
    Then 應顯示系統日誌的時間範圍選項
    When 我關閉系統日誌時間範圍選單

  Scenario: 下載系統日誌 ZIP
    Given 我已使用本輪登入狀態開啟平台管理頁
    When 我開啟系統日誌
    And 我下載系統日誌
    Then 下載的日誌檔名應以 .zip 結尾
