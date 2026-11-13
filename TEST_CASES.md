# AI Hub Playwright 自動化測試案例

## 2026-10-30｜一秒操作間隔更新後：完整流程實機通過

使用者在取得一秒操作間隔更新檔及完整執行指令後回報完成，並提供 `validation_summary(9).md` 與 15:26 終端截圖。

- 批次：`20261030T072126_460197Z_35669`。
- 執行時間（Asia/Taipei）：**15:21:26–15:25:34**，整輪約 **4 分 8 秒**。
- 摘要記錄 Git Commit `ff943384bcc9fe5e676c92774a9439bfab23ab30`，工作區有未提交修改；本次未取得同批次 JSON 的來源雜湊，不能僅以 Commit 表示完整實測來源。

| 階段 | 當輪實測結果 |
|---|---|
| 語法檢查與收集 | 12 支 Python 通過；收集 46 項 |
| 自動登入與狀態重用驗證 | PASS |
| 操作前一般回歸 | 41 passed、5 skipped、0 failed、0 errors |
| 模型與 AI 應用操作，含一則模型對話送出驗證 | 2 passed、0 skipped、0 failed、0 errors |
| 操作後一般回歸 | 41 passed、5 skipped、0 failed、0 errors；截圖顯示 54.56 秒 |
| 自動登出及狀態清理 | PASS；回訪管理頁仍要求登入 |
| 整體 | **PASS** |

- 五項 Skip 仍是缺少群組、LDAP、API 端點或 API 金鑰資料／啟用條件，前後兩輪一致；不屬於新增失敗。
- 這輪已完成修改後的整體功能驗證，不需為相同修改再重跑。一般回歸每輪仍為 46 項，操作型案例另計 2 項。
- 當輪資料夾：`reports/validation_runs/20261030T072126_460197Z_35669/`。Demo／成果交付可使用同批次摘要與三份 HTML 報告。
- 本摘要可證明功能流程通過；沒有逐步視窗錄影或操作時間資料，不能獨立量測每個操作確實間隔一秒，也不能由摘要判定當輪每項服務的起始狀態、是否真正觸發停用或重試。模型遵守「只回覆 OK」的評估仍按原決定延後。
- 下方「待實測」與 300 ms 說明保留為修改前歷史紀錄；本節為此次更新後的最新完整實測結果。


## 2026-10-30｜所有可見操作放慢至 1 秒

- `scripts/save_login_state.py` 新增 `AUTH_SLOW_MO_MS = 1_000`，並在兩個瀏覽器啟動入口設定 `slow_mo`：獨立登入工具，以及 `run_validation.py --auto-login` 使用的 `ValidationSession`。
- 登入與登出沿用同一視窗，皆受此設定影響；帳號密碼仍整段填入，不改為逐字輸入。
- `scripts/run_validation.py` 將操作型 pytest 階段改為 `--headed --slowmo 1000`；啟停部署、模型對話與歷史紀錄均以 1 秒間隔操作。一般回歸仍預設背景執行，不額外放慢。
- 指令不需改動，也不需在 `.env` 新增設定。將兩份 Python 分別覆蓋到專案的 `scripts/save_login_state.py`、`scripts/run_validation.py`。使用下方 `PYTEST_ADDOPTS=""` 的混合顯示指令。
- 本次完成兩份 Python 語法檢查、變更差異核對與 3 項執行器離線模擬檢查（含操作階段 1000 ms、回歸未加 headed、對話旗標傳遞及限制）。沒有登入實際 Hub；1 秒間隔的本機觀看效果待確認。先前功能測試成績不視為此修改已實測。
- 下一步可先執行 `python scripts/save_login_state.py --auto --check-cycle` 單獨確認登入／登出速度；要看所有可見流程，再用下方完整混合顯示指令執行。獨立 check-cycle 會實際登入與登出，不儲存登入狀態。
- 先前段落中的 300 ms 是修改前的設定與歷史說明；本節兩份更新程式的可見操作階段已統一為 1000 ms。直接單跑 pytest 時仍需自行加 `--headed --slowmo 1000`，不會套用執行器的參數。


## 2026-10-30｜Demo：一般回歸在背景，操作流程顯示瀏覽器

**本機版本已核對，顯示效果待執行確認**：已檢查使用者上傳的 `run_validation(3).py`、`save_login_state(1).py`、`manual_model_activation(4).py`。登入工具明確使用 `headless=False`；登出沿用該視窗；模型操作型階段使用 `--headed --slowmo 300`，對話與歷史紀錄驗證在同一個可見視窗執行。程式沒有將登入、登出或對話單獨切換成背景模式，本次不修改 Python。使用者先前表示這三個流程沒有顯示，原因尚不能從這三份檔案確認，需以完整指令執行並對照當輪日誌。

| 階段 | 預期瀏覽器顯示（非本輪實測結果） |
|---|---|
| 自動登入 | 顯示，輸入帳密並驗證登入 |
| 操作前一般回歸（46 項） | 預設背景執行，iTerm 顯示結果 |
| 模型與 AI 應用啟停部署 | 顯示，操作間隔 300 ms；依當下狀態與授權執行 |
| 模型對話送出、非空白回覆、重開歷史紀錄 | 與模型操作使用同一測試視窗，顯示操作 |
| 操作後一般回歸（46 項） | 預設背景執行，iTerm 顯示結果 |
| 自動登出及回訪管理頁驗證 | 使用保留的登入視窗顯示操作 |

登入視窗會保留至整輪結束，供最後登出；因此一般回歸期間仍可能看見該視窗。這不表示背景回歸正在那個視窗操作。`--manual-activation` 指明確選擇執行操作型測試，啟停過程由程式自動操作。

以下指令包含自動登入、最後登出及對話送出；下一步用此指令確認各階段顯示：

```bash
cd ai_hub-playwright-test
source .venv/bin/activate

PYTEST_ADDOPTS="" \
MODEL_TEST_WRITE=I_UNDERSTAND \
MODEL_TEST_ALLOW_DISABLE=YES \
MODEL_TEST_ALLOW_RETRY=YES \
AI_APP_TEST_WRITE=I_UNDERSTAND \
AI_APP_TEST_ALLOW_DISABLE=YES \
AI_APP_TEST_ALLOW_RETRY=YES \
python scripts/run_validation.py --auto-login --manual-activation --chat-send
```

- `PYTEST_ADDOPTS=""` 只在此指令清除繼承的 pytest 額外選項，避免先前全域 `--headed` 讓所有回歸開窗；它不會移除執行器在操作型階段明確加入的參數。
- 前提是 pytest 設定檔本身沒有另加全域 `--headed`；若有，需移除才能讓一般回歸在背景跑。
- `.env` 仍需設定 `BASE_URL`、`TEST_USERNAME`、`TEST_PASSWORD`。已有 `--auto-login`，不需先另跑 `save_login_state.py --auto`。
- 想看所有階段時，將 `PYTEST_ADDOPTS=""` 換成 `PYTEST_ADDOPTS="--headed --slowmo 300"`。
- 此指令會實際操作服務及建立一則真實模型對話；不驗證回覆是否精確等於 OK，也不評估模型遵守指令的能力。
- 報告結構維持不變：當輪資料夾內的 `validation_summary.md`、`regression_before.html`、`manual_activation.html`、`regression_after.html`；結束後確認 `[overall] PASS`。

**本次驗證範圍**：核對已交付執行器與登入工具，並通過 3 項離線模擬檢查（包含分階段參數、對話旗標與前置限制）。沒有修改 Python、沒有再次操作實際 Hub。已完成上傳本機三份 Python 的語法與顯示設定核對，並對上傳的執行器通過 3 項離線模擬檢查；瀏覽器是否在本機按預期顯示，仍需實際執行確認。先前網站功能實測通過不能代替瀏覽器顯示方式驗證。


## 文件目的

本文件記錄 AI Hub 的 Playwright 自動化測試範圍、預期結果與執行狀態，方便開發、測試與專案相關人員確認目前已完成及尚待補充的測試項目。

## 2026-10-30｜模型對話送出：完整流程與單項皆已實機通過

### 完整流程實測

- **批次**：`20261030T060000_575574Z_32066`；2026-10-30 **14:00:00–14:05:02（Asia/Taipei）**。
- **證據**：使用者提供的 `validation_summary(8).md` 與 14:05 終端截圖。摘要明確記錄本輪要求對話送出，模型操作案例包含該驗證；整體 **PASS**。
- **版本**：基礎 Git Commit `bbd122cc6dd959100cfffea7a5666ee51079027b`；工作區有未提交修改，不能只用此 Commit 代表完整實測來源；同批次 JSON 的來源 SHA256 尚未提供。

| 階段 | 實測結果 |
|---|---|
| Python 語法檢查與收集 | 12 支 Python 語法通過；收集 46 項，結束碼 0 |
| 自動登入及狀態驗證 | PASS |
| 操作前一般回歸 | **41 passed、5 skipped、0 failed、0 errors** |
| 模型／AI 應用操作，含一則模型對話送出驗證 | **2 passed、0 skipped、0 failed、0 errors** |
| 操作後一般回歸 | **41 passed、5 skipped、0 failed、0 errors**；截圖顯示 **86.86 秒** |
| 自動登出及本輪狀態清理 | PASS；回訪管理頁仍要求登入 |
| 整體 | **PASS** |

五項略過仍為群組選單、LDAP 選單、LDAP 修改頁、API 端點明細與 API 金鑰選單，均有當輪環境資料／啟用狀態原因；本批次前後 AI 應用入口皆通過。一般回歸每輪仍為 46 項，送出是模型操作案例中的步驟，沒有新增第 47 項一般回歸。

### 單項對話實測

- 使用者先執行 `python scripts/save_login_state.py --auto`，終端確認狀態已儲存至 `.auth/user.json`，再單獨跑 `test_model_activation_and_chat[chromium]`。
- **單項結果**：14:12 終端截圖為 **1 passed in 9.93s**；模型起始已啟用、未授權停用，直接驗證 Chat UI。
- 終端確認選取 Llama3.1-FFM-8B、送出一則訊息、建立非空白 sessionId、觀察到 2 字元非空白回覆，並從歷史開回同一 session，訊息與回覆仍存在。
- 使用者貼出的去識別化 JSON 顯示 `sent_messages=1`、`reply_nonempty=true`、`reply_length_observed=2`、`history_reopened=true`，驗證時間 **2026-10-30T14:12:32+08:00**，歷史標題為 `OK`。完整 sessionId 不納入文件。
- `history_title=OK` 是歷史標題；JSON 未保存回覆全文，因此不能只以標題和 2 字元長度證明實際回覆就是 OK。`prompt` 的隨機標記只供辨認測試批次。

| 已完成的驗證 | 目前狀態 |
|---|---|
| 選取指定 LLM、輸入文字並確認輸入值 | 已實機通過 |
| 送出一則訊息並建立動態 sessionId | 已實機通過 |
| 對話頁顯示正確的使用者訊息、輸入框清空 | 已實機通過 |
| 模型出現非空白回覆 | 已實機通過 |
| 側欄歷史可開回同一對話，訊息及回覆仍存在 | 已實機通過 |
| 自動登入、前後回歸、服務操作與登出整輪 | 已實機通過 |

### 延後與尚未有實機證據的項目

| 項目 | 分類與界線 |
|---|---|
| 模型是否遵守「只回覆 OK」及回答品質 | **使用者決定延後再做**；不納入本次通過條件 |
| 模型或 AI 應用啟用失敗後的第二次重試 | 已有程式與離線檢查；目前提供的證據未確認本輪實機觸發，需核對重試事件日誌 |
| 自動登入失敗、回歸失敗、回覆逾時、登出失敗或按 Ctrl+C 的異常處理 | 各分支只有既有離線檢查範圍內的證據；本次正常 PASS 不代表這些異常分支皆已實機驗證 |
| AI 應用從「未下載」開始下載再啟用 | 尚未有實機通過證據 |
| 本批次模型與 AI 應用是否都實際先停用再啟用 | 需核對本批次操作日誌，不能只憑摘要固定階段名稱或 2 passed 判斷；既有歷史循環證據保留 |

另曾觀察到單項測試沿用失效登入狀態而停在 Keycloak 登入頁；重新執行 `save_login_state.py --auto` 後成功。這證明單項前的重新登入解法有效，不等於自動登入失敗處理分支已實機通過。

**目前操作方式**：先自動登入並儲存狀態，再執行單項 pytest；單項本身不自動登入或登出。`--chat-only` 只到未交付草稿，本次不納入已完成功能，也不要求套用該草稿。

**收尾**：保留完整批次報告與原始對話證據 JSON，依本次實測更新文件即可。不新增程式行為、不要求現在補測上述項目；這次純文件更新不需重跑完整回歸。

## 2026-10-30｜模型對話送出驗證範圍

此為 `test_model_activation_and_chat` 中的新可選步驟，不加入既有 46 項一般回歸數量。整輪使用 `--auto-login --manual-activation --chat-send`，並保留原有服務操作授權；未要求 `--chat-send` 時不送出。

| 步驟 | 預期結果 | 目前狀態 |
|---|---|---|
| 模型前置檢查 | 指定 LLM 已啟用，首頁明確選取 Llama3.1-FFM-8B | **正常流程已實機通過**；沿用既有啟用與選取檢查 |
| 文字輸入與送出 | 填入一則含隨機標記的短訊息、送出按鈕可用，點擊一次 | **已實機通過** |
| 建立新對話 | 同來源／路徑產生一個非空白動態 sessionId；使用者訊息內容正確，輸入框清空 | **已實機通過** |
| 模型回覆 | 出現非空白回覆；不以固定回答文字或生成完整結束為判定 | **已實機通過** |
| 側欄歷史 | 有當前歷史標題，切換到新對話後能由歷史開回同一 sessionId，訊息及回覆仍存在 | **已實機通過** |
| 失敗處理 | 空訊息／既有 session 不送出；送出後驗證失敗不重送；保留既有失敗證據流程 | 離線情境通過；尚未有對應實機證據 |
| 相容性 | 不加新旗標仍為原有輸入檢查；一般回歸 46 項、操作 2 項維持 | 本輪加旗標已實機通過；未加旗標的新版相容性仍為離線檢查 |

通過時會產生 `reports/model_chat/chat_<隨機標記>.json`；同一個案例通過須包含新送出步驟，不能只拿舊版 2 passed 證明新功能完成。測試會保留真實對話歷史，不自動刪除。15 項離線檢查與後續正常流程的實機結果分開記錄；異常分支不得沿用正常 PASS。

## 2026-10-30｜自動登入、服務操作、前後回歸與登出整輪 PASS

- **批次**：`20261030T031505_022088Z_28383`。
- **時間**：2026-10-30 **11:15:05–11:26:26（Asia/Taipei）**，共 11 分 21 秒。
- **證據**：使用者提供的 `validation_summary(7).md` 與 11:26:40 終端截圖；摘要與截圖的整體結果均為 **PASS**。這是使用者環境的實機結果，非本次文件編輯重新執行測試。
- **版本**：基礎 Git Commit `3abe937372fbe4a7954546d7e76a1a434ba5cc95`；工作區有未提交修改，不能只靠此 Commit 代表全部實測程式。完整來源 SHA256 應由同批次 JSON 追溯，本次未提供該 JSON。

| 階段 | 本批次實機結果 | 判定 |
|---|---|---|
| Python 靜態語法檢查 | 12 支 Python 通過 | PASS |
| 一般回歸收集 | 46 項，pytest 結束碼 0 | PASS |
| 自動登入與本輪狀態重用 | 登入成功，狀態可供各階段使用 | PASS |
| 指定單項測試 | 未指定 `--target` | NOT_REQUESTED |
| 操作前一般回歸 | **40 passed、6 skipped、0 failed、0 errors** | PASS |
| 模型與 AI 應用操作 | **2 passed、0 skipped、0 failed、0 errors** | PASS |
| 操作後一般回歸 | **41 passed、5 skipped、0 failed、0 errors**；截圖顯示 **56.21 秒** | PASS |
| 自動登出與本輪狀態清理 | 已點擊登出，回訪管理頁仍要求登入 | PASS |

**入口恢復與略過判讀**：操作前缺少 AI 應用入口的指定案例保留為 Skip，額外允許 1 項；操作後該入口測試通過，因此由 40／6 變為 41／5。其餘五項為群組選單、LDAP 選單、LDAP 修改頁、API 端點明細、API 金鑰選單，均有當輪環境原因。每輪回歸仍為 46 項，登入／登出是另外的執行階段，不改變既有案例數。

**已確認範圍**：自動登入 → 操作前回歸 → 模型與 AI 應用操作 → 操作後回歸 → 登出整輪已實機完成。先前 11:14 的唯讀整輪也已通過，當輪為 40 passed／6 skipped，登出與整體 PASS；唯讀截圖未提供批次編號，不與本批次混用。

**仍待證據確認**：摘要固定階段名稱為「模型與 AI 應用完整啟停」，但未提供操作日誌，不能單靠這個名稱或 2 passed 證明兩者本次都曾先停用再啟用，也不能證明第二次重試實際觸發；需核對本批次 `manual_activation.log` 與對應時間的重試事件。首次下載、登入失敗、回歸失敗、登出失敗與 Ctrl+C 的處理分支，均未由本次正常 PASS 證明實機通過；原有離線檢查紀錄仍保留。

**後續**：保留 `reports/validation_runs/20261030T031505_022088Z_28383/` 的摘要、JSON、HTML 與日誌。文件更新不需重跑；如要補充停用循環或重試證據，先核對既有日誌。

## 2026-10-30｜登入／登出與整輪串接的驗證狀態

下列流程檢查不加入既有 46 項 pytest 回歸數量；登入／登出由整輪執行器另列階段。

| 驗證項目 | 預期結果 | 目前證據與狀態 |
|---|---|---|
| 獨立自動登入／登出 | 開啟設定網址、自動填帳密、進入管理頁、登出；再訪管理頁仍要求登入 | **實機通過**；使用者 10/30 10:44 終端截圖；命令為 `save_login_state.py --auto --check-cycle` |
| 自動登入後一般回歸 | `login` 通過後執行原有 46 項回歸，最後 `logout` 通過 | **實機通過**；11:14 唯讀整輪 40 passed／6 skipped，logout／overall PASS |
| 自動登入後啟停與前後回歸 | 同一輪登入狀態提供各階段，後回歸完成後才登出 | **正常整輪實機通過**；11:15–11:26 批次 login／前回歸／操作／後回歸／logout 全部 PASS；失敗情境仍僅離線模擬 |
| 登入失敗 | 不跑回歸，嘗試清理；摘要標示失敗 | 離線模擬通過；尚未實機驗證 |
| 回歸或啟停失敗 | 保留原本失敗結果；啟停失敗仍跑後回歸，最後嘗試登出 | 離線模擬通過；尚未實機驗證 |
| 登出／清理失敗 | 整輪不可為 PASS；摘要保留原因 | 離線模擬通過；尚未實機驗證 |
| 執行中按一次 Ctrl+C | 記錄 INTERRUPTED，嘗試登出與清除本輪狀態，回傳 130 | 離線模擬通過；尚未實機驗證 |
| 未指定自動登入 | 沿用原本登入狀態方式，不操作登出 | 離線相容性檢查通過；新版尚未實機驗證 |

唯讀整輪與含服務操作的正常整輪均已由使用者實機通過，本次只更新文件，不需再跑。失敗／中止分支仍僅有離線檢查，不與正常整輪的實機結果混用。

## 歷史完整回歸結果｜2026-10-29 Mac 啟用與前後回歸

- **批次**：`20261029T034521_440063Z_8770`；2026-10-29 **11:45:21–11:56:07（Asia/Taipei）**。
- **整體結果**：**PASS**；證據為使用者提供的 `validation_summary(5).md` 與 11:55、11:56 終端機截圖。
- **版本**：基礎 Git Commit `2cbbbe4e4e922f35be37e702099c3d209bf71ab5`；執行時**有未提交修改**，不能只用這個 Commit 代表全部實測程式；來源版本另以同批次 JSON 的 SHA256 追溯。

| 階段 | 本批次實機結果 | 判定 |
|---|---|---|
| Python 語法檢查 | 12 支 Python 通過 | PASS |
| 一般回歸收集 | 46 項 | PASS |
| 指定單項測試 | 未指定 `--target` | NOT_REQUESTED |
| 啟用前一般回歸 | **40 passed、6 skipped、0 failed、0 errors**；入口缺少另行允許 1 項，其餘 5 項有環境原因 | PASS |
| 模型與 AI 應用操作 | **2 passed、0 skipped、0 failed、0 errors** | PASS |
| 啟用後一般回歸 | **41 passed、5 skipped、0 failed、0 errors**；終端機顯示 **55.32 秒** | PASS |

**操作證據與界線**：Llama3.1-FFM-8B 最終達 `enabled`，Chat 模型選取與文字輸入驗證通過；AFS MyAgent 由 `downloaded_disabled` 啟用，約 **29.9 秒**達 `enabled`，點擊「開始使用」並確認畫面／網址／分頁切換。兩者均**未送出訊息**，模型實際推論回覆不在本輪已驗證範圍。摘要中的「模型與 AI 應用完整啟停」是執行器固定階段名稱，實際操作依起始狀態決定；**這份摘要不單獨證明兩者本輪都執行過停用**。已知 AFS MyAgent 本輪由未啟用開始，不能把它記成停用再啟用循環。

**尚未確認**：本次提供的截圖沒有完整的 `attempt_2_clicked` 紀錄；重試旗標已開啟不等於第二次點擊實際觸發。模型與 AI 應用的重試分支仍須以當輪日誌核實，維持「尚未確認實機觸發」。AI 應用首次下載仍未實機驗證；先前啟用回退及 Chat 偶發載入失敗的根因仍未確認。10/28 的完整停用循環 PASS 與歷史 FAIL 均保留，與本輪分開判讀。

### 啟用前後的 Skip 判定

- 其他一般回歸的略過上限仍預設 **5 項**，每項必須有原因；上限本身不是五個測試的白名單，仍要核對實際略過清單。
- 只有 `regression_before` 階段，指定案例 `tests.test_user_home::test_ai_apps_can_be_opened_and_returned[chromium]` 因「使用者介面沒有 AI 應用入口」而略過時，才額外允許最多 **1 項**。仍如實顯示 **6 skipped**，不把它改成 Pass 或從報告刪除。此情境已由使用者確認目前沒有啟用的 AI 應用；執行器是依案例與略過原因判定，沒有額外查管理端狀態。
- `regression_after` 階段要求 AI 應用入口案例實際通過；略過、失敗或未出現在通過清單，都使本階段 FAIL。即使手動提高略過上限，也不會放行這項入口檢查。
- 本輪 TC-045 的變化是 **啟用前 Skip → 啟用後 Pass**，所以由 40／6 變為 41／5；每輪仍是 46 項。不要加成單輪的案例總數。
- 五項仍略過：TC-022 群組選單、TC-028 LDAP 選單、TC-029 LDAP 修改頁、TC-033 API 端點明細、TC-035 API 金鑰選單。相關頁面顯示等其他檢查已有通過，不代表這四類功能完全沒有測試。

### 本次修正的覆蓋狀態（不增加一般回歸數量）

| 檢查內容 | 狀態 | 證據／限制 |
|---|---|---|
| 啟用前允許指定入口缺少、繼續操作 | 實機 PASS | 40 passed／6 skipped，前置關卡通過 |
| 模型啟用後 Chat 模型選取與輸入 | 實機 PASS | 模型達 enabled；未傳訊息，不驗證推論回覆 |
| AFS MyAgent 由未啟用狀態啟用並開始使用 | 實機 PASS | 約 29.9 秒達 enabled；確認畫面／網址／分頁切換，未傳訊息 |
| 啟用後入口恢復與一般回歸 | 實機 PASS | TC-045 通過，回歸 41 passed／5 skipped，55.32 秒 |
| 模型與 AI 應用第二次自動點擊 | 尚未確認實機觸發 | 開關已開啟；提供的截圖與摘要未含完整第二次點擊事件 |
| 本次修正的等待與重試邏輯 | 20 個離線情境通過 | 開發環境模擬，與 Mac 實機／既有 18 項工具結果分開 |
| AFS MyAgent 首次下載 | Not Run（實機） | 不因已下載狀態的成功而推定下載分支通過 |
| 完整停用再啟用循環 | 保留 2026-10-28 的已確認 PASS | 本輪由起始狀態決定操作，不能只靠固定階段名稱宣稱重驗完整循環 |

現行執行方式及兩個重試開關見 [README.md](README.md)；等待秒數、事件名稱與踩坑說明見 [PLAYWRIGHT_NOTES.md](PLAYWRIGHT_NOTES.md)。以下 10/28 及更早結果均保留為歷史，不覆蓋本節當輪統計。

## 歷史已確認結果｜2026-10-28 Mac 授權啟停與最終回歸（同一批次）

- **執行批次**：`20261028T073927_087203Z_80555`
- **時間**：15:39:27–15:44:08（Asia/Taipei）
- **整體結果**：**PASS**；Git Commit `1b1ed29fe19612516f86cb39b12852360ccbeb8c`，執行當時工作區**乾淨**。

| 固定關卡 | 本批次實測結果 | 判定 |
|---|---|---|
| Python 靜態語法 | 12 支 Python 檢查通過 | **PASS** |
| 一般回歸收集 | 46 collected，數量正確 | **PASS** |
| 啟停前一般回歸 | **41 passed、5 skipped、0 failed、0 errors** | **PASS** |
| 模型與 AI 應用完整啟停 | **2 passed in 155.52s，0 failed／skipped**；含模型恢復啟用後的 Chat 使用者端驗證、AFS MyAgent 重新啟用及「開始使用」驗證 | **PASS** |
| 啟停後最終一般回歸 | **41 passed、5 skipped、0 failed、0 errors**；其中終端機顯示 `66.26s` | **PASS** |
| AI 應用自動提早回退／重試實機分支 | 本批次無已提供的重試觸發事件；18 項離線檢查另有 PASS | **尚未實機驗證** |

每輪一般回歸的五項 Skip 為群組選單、LDAP 功能選單、LDAP 修改頁、API 端點明細及 API 金鑰選單，均因測試環境缺少對應資料／啟用條件，且已附明確原因。**41 Pass／5 Skip 是各輪的 46 項結果，不把前後兩輪或兩項操作型測試合併成「單輪 94 項 Pass」。**

本次修正了 Chat 首頁等待策略：一般首頁 `expect_loaded()` 預設上限 **20 秒**，模型重新啟用後的 Chat 驗證指定 **100 秒**；失敗時補充頁面 URL（移除查詢參數）、標題及載入狀態。此前 15:06–15:10 的批次曾在模型達 `enabled` 後因 Chat 首頁顯示／登入導向而使操作型階段 **1 passed、1 failed**，但 AI 應用及後驗一般回歸通過；該輪整體仍為 **FAIL**。本次通過不代表已證明舊故障的唯一根因，歷史失敗與 Trace 應保留。

**資料邊界**：`scripts/selfcheck_validation.py` 的 **5 tests OK** 與 `verify_flow_offline.py` 的 **18 項 PASS** 為獨立離線證據；真正「未下載 → 下載」以及 AI 應用有條件自動重試的實機分支仍未完成。報表及畫面／Trace 不提交公開 Git。

## 較早已確認結果｜2026-10-28 Mac 一般回歸與離線檢查（歷史批次）

| 驗證範圍 | 當次實測結果 | 是否操作 AI Hub |
|---|---|---|
| 統一執行器自檢 `scripts/selfcheck_validation.py` | **5 tests，OK** | 否；隔離模擬 |
| `verify_flow_offline.py` 新版狀態／重試分支 | **18 項 PASS**（6 原有狀態、10 重試、1 授權、1 事件紀錄） | 否；模擬時鐘、不連服務 |
| 一般回歸 `python scripts/run_validation.py` | **46 collected，41 passed、5 skipped、0 failed、0 errors；整體 PASS** | 是；一般唯讀／低風險 UI 測試 |
| 該一般模式批次的服務完整啟停 | **NOT_REQUESTED** | 當時未執行；最新完整批次已於上節 PASS |
| 該一般模式批次的啟停後最終回歸 | **NOT_REQUESTED** | 當時未進行啟停；最新完整批次已於上節 PASS |
| AI 應用提早回退／重試的實機分支 | **尚未實機觸發驗證** | 只完成離線分支驗證 |

該較早一般模式批次依使用者提供的 `reports/validation_summary.md` 確認：2026-10-28 14:11:17–14:12:16（Asia/Taipei），靜態檢查 12 支 Python、收集 46 項、41 Pass／5 Skip／0 Failed。Git 基礎 Commit：`5c91ddf89593effce5369c64bbdab57227b164e2`；當時工作區有未提交修改，因此 Commit 本身**不代表**所有實測檔案已提交。當輪 JSON 另存各來源檔 SHA256。

五項 Skip 均有前置條件理由：群組功能選單、LDAP 功能選單、LDAP 修改頁、API 端點明細、API 金鑰功能選單。**此次 46 項回歸已在 Mac 實測 PASS**，不可再以先前「交付副本 BLOCKED」代表最新狀態。

本次離線 18 項 PASS 由使用者在 Mac 的 Terminal 回報；它確認的是目前程式邏輯分支，**不代表 18 項 Playwright 實機測試**。執行這兩支離線工具不需要登入 AI Hub；要跑真正 UI 回歸，則需有效的 `.auth/user.json` 登入狀態，操作步驟見 [README.md](README.md)。

## 2026-10-28｜固定驗證制度導入（初版交付副本的歷史紀錄）

本次新增 `scripts/run_validation.py` 及其離線單元檢查，建立「語法 → 46 項收集核對 → 指定測試（若有）→ 一般回歸 → 授權啟停（若有）→ 最終回歸」的固定關卡。每輪輸出 `reports/validation_summary.json`、`reports/validation_summary.md` 並歸檔個別階段日誌／JUnit、版本資訊與 Skip 原因。詳細指令與授權條件見 [README.md](README.md#0-固定驗證入口與交付門檻2026-10-28-新增)。

| 項目 | 初版交付副本當時的狀態 | 證據／界線 |
|---|---|---|
| 統一執行器 Python 語法 | **PASS** | 交付副本檢查 6 支 Python |
| 執行器離線單元／整合測試 | **5 passed** | 測試收集解析、授權、安全目標範圍、JUnit 統計、隔離假 pytest 完整流程 |
| 46 項一般回歸（修改後） | **BLOCKED／尚未執行** | 本次只取得修正版檔案與文件 ZIP，缺少原專案三支一般回歸測試檔；需回到完整專案執行 |
| 模型／AI 應用完整啟停（本次執行器） | **NOT_RUN** | 未取得服務操作授權，也未連上目標 AI Hub；下節的 2 passed 是先前單獨執行的歷史實測 |
| AI 應用提早回退重試分支（實機） | **NOT_RUN** | 不因條件旗標存在或其他路徑 PASS 就標成已驗證 |

**交付門檻：** 不得把不同日期的完整回歸與兩項啟停結果相加成「同一版本全數通過」。上表 BLOCKED 僅為初版交付副本當時的環境結果；Mac 正式專案後續已取得本文件最上方的 46 項 PASS。操作型測試後的最終回歸仍須另外取得當輪報表；5 項歷史 Skip 有既定原因，若本輪清單發生變動，需重新確認。

## 測試環境

| 項目 | 內容 |
|---|---|
| 測試框架 | Playwright for Python |
| 測試執行工具 | pytest 9.1.1 |
| Playwright 版本 | 1.62.0 |
| Python 版本 | 3.12.14 |
| 瀏覽器 | Chromium |
| 測試介面語言 | 繁體中文 |
<!-- | 測試環境 | `https://afs-aihub.com/` |
| Platform Manager | `https://afs-aihub.com/platform-manager` | -->
<!-- | 測試環境 | `https://inference.afs-suite.ai/` |
| Platform Manager | `https://inference.afs-suite.ai/platform-manager` | -->
| 測試環境 | `https://202.5.254.27/` |
| Platform Manager | `https://202.5.254.27/platform-manager` |
| 登入方式 | 使用測試帳號及已儲存的登入狀態 |

> 注意：`.auth/user.json` 含登入狀態，不可提交至 GitHub 或分享給其他人。

## 較早獨立操作測試（2026-10-28；不併入 46 項回歸）

| 執行批次 | 模型 Llama3.1-FFM-8B | AFS MyAgent | pytest 結果 |
|---|---|---|---|
| 統一一般啟用／使用者端驗證 | 原已 `enabled`，選取 Chat 模型與輸入驗證 PASS | `downloaded_disabled` → 自動啟用 →「開始使用」PASS，約 26.2 秒啟用 | `2 passed in 36.57s` |
| **先前統一完整啟停循環（已授權停用）** | 停用 → 重新啟用 → Chat PASS | 停用 → 重新啟用（約 26.1 秒）→「開始使用」PASS | `2 passed in 139.70s` |
| 前一輪完整啟停循環（歷史失敗） | 停用 → 重新啟用 → Chat PASS | 停用成功；點擊重新啟用後曾 `enabling`，返回 `downloaded_disabled`，300 秒逾時 FAILED | `1 passed, 1 failed in 406.08s` |

**此歷史完整循環結果為兩項 PASS。** 當輪 AFS MyAgent 約 26.1 秒重新啟用成功，並點「開始使用」；截圖中沒有出現提早回退或第二次自動重試紀錄，因此**新版自動重試分支仍未實機驗證**。更早前曾經發生 `1 passed, 1 failed in 406.08s`：AFS MyAgent 管理頁確實點過「啟用」並顯示部署提示，但退回 `downloaded_disabled`，300 秒逾時。此失敗不可改寫成 PASS，根因仍待確認。2026-10-21 的歷史完整啟停 PASS 也繼續保留；**這是 10/28 的完整循環紀錄；最新 10/29 啟用與回歸結果見文件開頭**。

**後續人工操作觀察（不計入 pytest）：** 使用者在前述測試結束後於 UI 再點一次「啟用」，畫面顯示「啟用中…」。目前尚未取得此輪最終 `enabled` 截圖，**不能標記為人工恢復成功**。前一次自動點擊其實也曾短暫觀察到 `enabling`，因此尚不足以斷定第一次完全沒有觸發。

**新修正版可選重試（未實機驗證）：** 額外設定 `AI_APP_TEST_ALLOW_RETRY=YES` 時，第一次若觀察到 `enabling → downloaded_disabled` 且連續 30 秒仍未恢復，會記錄 `attempt_1_enabling_reverted_30s`（不是 300 秒逾時）並提前檢查重試。若沒有發生這種穩定回退而等滿 300 秒，才記錄 `attempt_1_timeout_300s`。兩種事件都寫入 `reports/ai_application_activation/enable_attempts.log`；確認狀態仍未啟用、再經 10 秒確認後最多自動點第二次，第二輪再等最多 300 秒。即使第二輪成功，第一次失敗跡象仍保留。舊參數 `AI_APP_TEST_RETRY_ON_TIMEOUT=YES` 只允許 300 秒後重試，不允許提早重試。預設不重試，且 UI 無法完全證明後端部署已結束。

新版 `test_model_activation_and_chat` 與 `test_ai_app_activation` 依起始狀態自動選擇直接驗證、啟用或（設定 `*_ALLOW_DISABLE=YES` 時）完整停用／重新啟用。以下為**當時**的離線六項分支及操作型測試紀錄；後續 2026-10-28 Mac 已另行完成本文件最上方的 46 項正式回歸，離線工具亦更新為 18 項 PASS。

## 歷史完整回歸紀錄：2026-10-21

| 項目 | 結果 |
|---|---:|
| 共收集 | 46 |
| Pass | 41 |
| Fail | 0 |
| Skip | 5 |
| 執行時間 | 53.14 秒 |

```text
41 passed, 5 skipped in 53.14s
```

五項 Skip 都是前置條件不足，**不是測試失敗**：群組功能選單、LDAP 功能選單、LDAP 修改頁、API 端點明細、API 金鑰功能選單。

此次使用者端 AI 應用入口測試 **TC-045 已從原本 Skip 轉為 Pass**。先前 AFS MyAgent 未啟用時，使用者端沒有 AI 應用入口；後續獲授權啟用 AFS MyAgent 後，完整回歸已能執行 AI 應用列表測試。這次完整回歸仍是原本的 **46 項**，並未新增一項測試。

同日獨立檢查：模型＋AI 應用管理五項唯讀回歸 `5 passed in 8.40s`；`test_ai_app_start_only` 因 AFS MyAgent 未啟用而 `1 skipped in 3.17s`，兩者皆**不另外加進**上述 46 項。

### HTML 測試報告（本機已驗證可產出並開啟）

於專案根目錄使用：

```bash
mkdir -p reports
python -m pytest -v -rs \
  --html=reports/report.html \
  --self-contained-html
open reports/report.html
```

已確認 `reports/report.html` 可以產生並開啟。執行 `pytest --html` **不等同** 已啟用 GitHub Actions／CI；截圖或 Trace 也不會因為加上 HTML 參數就自動完整保存。

曾發生登入狀態過期，導致許多需要登入的測試從第一項起連續 `FAILED`。重新登入後已恢復正常操作。報告成功本身不等於所有測試通過；**當時**成功的完整 pytest 統計為 `41 passed, 5 skipped in 53.14s`；更早一輪成功結果為 `41 passed, 5 skipped in 44.85s`。最新 10/29 Mac 執行器結果已更新於本文件開頭。

### 前一次成功完整回歸（歷史，2026-10-21）

```text
41 passed, 5 skipped in 44.85s
```

### 更早一次完整回歸（歷史，2026-10-21）

```text
40 passed, 6 skipped in 48.60s
```

當時使用者端 AI 應用入口因沒有已啟用應用而 Skip；本次應用啟用後已 Pass。一般回歸與手動操作型測試仍分開計算。

### 本次修正前的完整回歸（更早期歷史）

| 共收集 | Pass | Fail | Skip |
|---:|---:|---:|---:|
| 46 | 36 | 5 | 5 |

當時失敗原因包括總覽元件名稱、使用者功能選單定位，以及未啟用資源的使用者首頁空狀態，後續已完成回歸修正。

## 前一次歷史完整回歸（供對照）

| 項目 | 結果 |
|---|---:|
| 測試總數 | 46 |
| 通過 | 43 |
| 失敗 | 0 |
| 略過 | 3 |
| 執行時間 | 43.26 秒 |

```text
43 passed, 3 skipped in 43.26s
```

## 測試案例

| 測試編號 | 測試功能 | 測試項目 | 測試檔案 | 預期結果 | 執行結果 | 狀態 | 備註 |
|---|---|---|---|---|---|---|---|
| TC-001 | 網站連線 | 確認 AI Hub 測試站可正常開啟 | `tests/test_site_access.py` | 網站成功載入，Playwright 可正常連線 | 網站成功載入 | Pass | 已設定忽略測試站 HTTPS 憑證錯誤 |
| TC-002 | Platform Manager | 使用已儲存的登入狀態進入管理頁 | `tests/test_platform_manager.py` | 不需再次登入即可進入 `/platform-manager` | 成功進入管理頁 | Pass | 使用 `.auth/user.json`，該檔案不得提交至 Git |
| TC-003 | Platform Manager | 確認左側 9 個主要功能選單皆正常顯示 | `tests/test_platform_manager.py` | 9 個功能按鈕皆可見 | 9 個功能按鈕皆正常顯示 | Pass | 不包含灰色的側欄分類標題 |
| TC-004 | 使用者管理 | 點擊「使用者管理」並驗證頁面切換 | `tests/test_platform_manager.py` | 保持在 Platform Manager，並顯示「使用者管理」頁面標題 | 成功切換並顯示正確標題 | Pass | 僅驗證頁面導航，未新增或修改使用者 |
| TC-005 | 群組管理 | 點擊「群組管理」並驗證頁面切換 | `tests/test_platform_manager.py` | 保持在 Platform Manager，並顯示「群組管理」頁面標題 | 成功切換並顯示正確標題 | Pass | 僅驗證頁面導航，未新增或修改群組 |
| TC-006 | LDAP 設定 | 點擊「LDAP設定」並驗證頁面切換 | `tests/test_platform_manager.py` | 保持在 Platform Manager，並顯示「LDAP 設定」頁面標題 | 成功切換並顯示正確標題 | Pass | 左側選單為「LDAP設定」，右側標題為「LDAP 設定」 |
| TC-007 | 模型管理 | 點擊「模型管理」並驗證頁面切換 | `tests/test_platform_manager.py` | 保持在 Platform Manager，並顯示「模型管理」頁面標題 | 成功切換並顯示正確標題 | Pass | 僅驗證頁面導航，未新增或修改模型 |
| TC-008 | AI 應用管理 | 點擊「AI應用管理」並驗證頁面切換 | `tests/test_platform_manager.py` | 保持在 Platform Manager，並顯示「AI應用管理」頁面標題 | 成功切換並顯示正確標題 | Pass | 僅驗證頁面導航，未新增或修改 AI 應用 |
| TC-009 | API 端點 | 點擊「API 端點」並驗證頁面切換 | `tests/test_platform_manager.py` | 保持在 Platform Manager，並顯示「API 端點」頁面標題 | 成功切換並顯示正確標題 | Pass | 僅驗證頁面導航，未新增或修改 API 端點 |
| TC-010 | API 金鑰管理 | 點擊「API 金鑰管理」並驗證頁面切換 | `tests/test_platform_manager.py` | 保持在 Platform Manager，並顯示「API 金鑰管理」頁面標題 | 成功切換並顯示正確標題 | Pass | 僅驗證頁面導航，未新增、展延或刪除金鑰 |
| TC-011 | 系統日誌 | 點擊「系統日誌」並驗證頁面切換 | `tests/test_platform_manager.py` | 保持在 Platform Manager，並顯示「系統日誌」頁面標題 | 成功切換並顯示正確標題 | Pass | 僅驗證頁面導航，未驗證日誌內容 |
| TC-012 | 總覽 | 驗證總覽頁靜態內容與篩選元件 | `tests/test_platform_manager.py` | 顯示 Token 用量與三個統計區塊；模型／日期篩選器依資源狀態及介面版本驗證，不以英文 Dropdown 名稱作固定斷言 | 最近一次已確認的完整回歸：總覽靜態內容通過 | Pass | 篩選器是條件式 UI；靜態測試不依賴英文圖示 accessible name |
| TC-013 | 總覽－使用者 | 收合並重新展開使用者區塊 | `tests/test_platform_manager.py` | 收合後欄位標題隱藏，重新展開後恢復顯示 | 使用者區塊可正常收合與展開 | Pass | 以 `columnheader` 驗證排名、使用者與 Token 數 |
| TC-014 | 總覽－API Key | 收合並重新展開 API Key 區塊 | `tests/test_platform_manager.py` | 收合後欄位標題隱藏，重新展開後恢復顯示 | API Key 區塊可正常收合與展開 | Pass | 以 `columnheader` 驗證排名、API Key 名稱與 Token 數 |
| TC-015 | 總覽－群組 | 收合並重新展開群組區塊 | `tests/test_platform_manager.py` | 收合後欄位標題隱藏，重新展開後恢復顯示 | 群組區塊可正常收合與展開 | Pass | 以 `columnheader` 驗證排名、群組名稱與 Token 數 |
| TC-016 | 語言切換 | 將介面由繁體中文切換為英文，再切回繁體中文 | `tests/test_platform_manager.py` | 「總覽／使用者管理」切換為 `Overview`／`User Management`，切回後恢復中文 | 中英文介面可正常來回切換 | Pass | 語言為 hover 觸發的第二層選單；測試結束前切回繁體中文 |
| TC-017 | 使用者管理 | 驗證頁面標題、新增按鈕、表格欄位與資料列 | `tests/test_platform_manager.py` | 顯示「使用者管理」、新增使用者按鈕及完整表格欄位，且至少有一筆資料列 | 頁面靜態內容正常顯示 | Pass | 不寫死姓名、帳號或目前資料筆數 |
| TC-018 | 使用者管理－新增使用者 | 開啟新增使用者 Dialog，驗證內容後取消 | `tests/test_platform_manager.py` | Dialog 顯示帳號、密碼、角色、姓名、電子郵件及操作按鈕；取消後關閉 | Dialog 可正常開啟及取消 | Pass | 不輸入資料、不點擊新增，不影響測試站資料 |
| TC-019 | 使用者管理－功能選單 | 展開第一筆使用者的功能選單 | `tests/test_platform_manager.py` | 展開使用者表格第一筆的功能選單，顯示修改與刪除 | 最近一次已確認的完整回歸：功能選單可展開，修改／刪除選項可見 | Pass | 不能假設首筆資料列的最後一格必有按鈕；按實際功能按鈕 DOM 定位，僅展開不修改或刪除 |
| TC-020 | 群組管理 | 驗證頁面標題、新增按鈕與表格欄位 | `tests/test_platform_manager.py` | 顯示「群組管理」、新增群組按鈕及完整表格欄位 | 頁面靜態內容正常顯示 | Pass | 群組資料可為空，不寫死群組名稱、人數或資料筆數 |
| TC-021 | 群組管理－新增群組 | 進入新增群組頁，驗證內容後返回群組管理 | `tests/test_platform_manager.py` | 顯示名稱、描述、成員選擇、成員表格與操作按鈕；返回後恢復群組管理頁 | 新增群組頁可正常進入及返回 | Pass | 新增群組是獨立頁面，不是 Modal；不輸入或送出資料 |
| TC-022 | 群組管理－功能選單 | 展開第一筆群組的功能選單 | `tests/test_platform_manager.py` | 有群組資料時，功能選單顯示「修改／刪除」 | 目前環境沒有群組資料，測試自動略過 | Skip | 使用 `pytest.skip()` 處理缺少測試資料的情況；不是測試失敗 |
| TC-023 | 模型管理 | 驗證頁面標題、操作紀錄按鈕、表格欄位與資料列 | `tests/test_platform_manager.py` | 顯示「模型管理」、「近7天操作紀錄」及完整表格欄位，且至少有一筆模型資料 | 模型管理靜態內容正常顯示 | Pass | 不寫死模型名稱、發行者或資料筆數 |
| TC-024 | 模型管理－操作紀錄 | 展開並收合「近7天操作紀錄」 | `tests/test_platform_manager.py` | 展開後顯示模型、操作者及動作／狀態欄位；收合後操作紀錄表隱藏 | 操作紀錄可正常展開與收合 | Pass | 操作紀錄可為空，只驗證區塊與欄位結構 |
| TC-025 | 模型管理－功能選單 | 展開第一筆模型的功能選單 | `tests/test_platform_manager.py` | 可見的功能選單顯示「下載／使用權限設定」 | 功能選單正常顯示 | Pass | 僅展開選單，不下載模型、不變更使用權限 |
| TC-026 | LDAP 設定 | 驗證頁面標題、新增按鈕與表格欄位 | `tests/test_platform_manager.py` | 顯示「LDAP 設定」、「＋新增 LDAP 設定」及名稱、LDAP URL、StartTLS、Bind DN、Users DN、功能等欄位 | LDAP 設定靜態內容正常顯示 | Pass | LDAP 資料可為空，不寫死設定名稱或資料筆數 |
| TC-027 | LDAP 設定－新增設定 | 進入新增 LDAP 設定頁，驗證欄位後返回 | `tests/test_platform_manager.py` | 顯示名稱、LDAP URL、StartTLS、Bind DN、Bind credentials、Users DN 與操作按鈕；返回後恢復 LDAP 設定頁 | 新增 LDAP 設定頁可正常進入及返回 | Pass | 不輸入資料、不切換 StartTLS、不驗證連線、不確認新增 |
| TC-028 | LDAP 設定－功能選單 | 展開第一筆 LDAP 設定的功能選單 | `tests/test_platform_manager.py` | 有 LDAP 資料時，功能選單顯示「修改／刪除」 | 目前環境沒有 LDAP 資料，測試自動略過 | Skip | 使用 `pytest.skip()` 處理缺少測試資料的情況；不執行刪除 |
| TC-029 | LDAP 設定－修改頁 | 進入第一筆 LDAP 設定的修改頁並驗證唯讀內容 | `tests/test_platform_manager.py` | 有 LDAP 資料時，顯示一般設定、Mapper 設定、LDAP 欄位與操作按鈕 | 目前環境沒有 LDAP 資料，測試自動略過 | Skip | 不修改欄位、不點擊驗證或確認修改；待有測試資料時自動執行 |
| TC-030 | AI 應用管理 | 驗證頁面標題與表格欄位 | `tests/test_platform_manager.py` | 顯示「AI應用管理」及 AI應用名稱、AI應用簡介、發行者、檔案大小、狀態、使用權限、功能等欄位 | AI 應用管理靜態內容正常顯示 | Pass | AI 應用資料可為空，不寫死應用名稱、狀態或資料筆數 |
| TC-031 | AI 應用管理－功能選單 | 展開第一筆 AI 應用的功能選單 | `tests/test_platform_manager.py` | 功能選單顯示「啟用」或「停用」，以及「使用權限設定」 | 功能選單正常顯示 | Pass | 「刪除」依應用類型或操作權限決定是否顯示，因此不列為固定必要選項；不執行任何功能 |
| TC-032 | API 端點 | 驗證頁面標題、啟用狀態與表格欄位 | `tests/test_platform_manager.py` | 顯示「API 端點」、「已啟用」或「未啟用」，以及 API名稱、API類型、API端點、說明等欄位 | API 端點靜態內容正常顯示 | Pass | 不操作狀態開關；啟用與未啟用兩種狀態皆可執行 |
| TC-033 | API 端點－端點明細 | 在 API 端點已啟用且有資料時驗證五組端點資訊 | `tests/test_platform_manager.py` | 顯示 Chat Completions、Embeddings、Rerank、Responses、Models 的方法、路徑與說明 | 最近一次完整回歸略過（無啟用 API 端點或資料） | Skip | 無 API 端點資料時屬正常略過 |
| TC-034 | API 金鑰管理 | 驗證頁面標題、新增按鈕、搜尋框與表格欄位 | `tests/test_platform_manager.py` | 顯示「API 金鑰管理」、「＋新增API金鑰」、完整 API KEY 搜尋框，以及金鑰名稱、描述、建立者、建立時間、最後使用時間、到期時間、功能等欄位 | API 金鑰管理靜態內容正常顯示 | Pass | 不寫死金鑰名稱、建立者、日期或資料筆數，不讀取任何實際金鑰值 |
| TC-035 | API 金鑰管理－功能選單 | 展開第一筆 API 金鑰的功能選單 | `tests/test_platform_manager.py` | 有 API 金鑰資料時，功能選單顯示「展延／刪除」 | 最近一次完整回歸略過（無 API 金鑰資料） | Skip | 無 API 金鑰資料時屬正常略過 |
| TC-036 | API 金鑰管理－新增金鑰 | 開啟新增 API 金鑰 Dialog，驗證欄位後取消 | `tests/test_platform_manager.py` | Dialog 顯示金鑰名稱、描述、有效天數、有效天數上限提示及操作按鈕；有效天數預設為 30；取消後關閉 | Dialog 可正常開啟及取消 | Pass | 不輸入資料、不點擊確認，不建立 API 金鑰 |
| TC-037 | 系統日誌 | 驗證頁面標題、說明、時間範圍及下載按鈕 | `tests/test_platform_manager.py` | 顯示「系統日誌」、異常處理說明、「請選取日誌時間範圍」、「今天」、下載按鈕及敏感資訊提醒 | 系統日誌靜態內容正常顯示 | Pass | 不讀取或記錄任何實際日誌內容 |
| TC-038 | 系統日誌－時間範圍 | 展開日誌時間範圍選單並驗證選項 | `tests/test_platform_manager.py` | 選單顯示「今天、最近3天、最近7天、最近30天」 | 四個時間範圍皆正常顯示 | Pass | 僅展開選單確認選項，最後以 Escape 關閉，不變更系統資料 |
| TC-039 | 系統日誌－下載 | 觸發日誌下載並驗證瀏覽器收到 zip 檔 | `tests/test_platform_manager.py` | 瀏覽器收到下載事件，建議檔名以 `.zip` 結尾 | 日誌 zip 下載事件正常 | Pass | 不開啟、不解壓縮、不另存或提交日誌；測試結束後由 Playwright 清理暫存檔 |
| TC-040 | 使用者首頁 | 使用已儲存的登入狀態開啟使用者首頁 | `tests/test_user_home.py` | 顯示「開始新的對話」與「詢問任何問題」輸入框 | 使用者首頁正常載入 | Pass | 使用 `pages/user_home_page.py`，不需重新輸入帳號密碼 |
| TC-041 | 使用者首頁－側欄 | 驗證使用者介面主要側欄項目 | `tests/test_user_home.py` | 顯示 Logo、開始新的對話、提示詞庫、對話歷史、平台管理與帳號及設定；AI應用入口有資源時可見 | 最近一次完整回歸：固定側欄正常；當前已有啟用的 AI 應用 | Pass | 無已啟用 AI 應用時，缺少側欄 AI 應用入口是允許的空狀態 |
| TC-042 | 使用者首頁－靜態內容 | 驗證歡迎文字、AI 應用卡片及訊息輸入區 | `tests/test_user_home.py` | 顯示歡迎文字、輸入框及停用狀態的送出按鈕；有已啟用 AI 應用時才要求卡片區塊 | 最近一次完整回歸：歡迎文字與輸入區正常，已啟用應用時相關 UI 驗證通過 | Pass | 已啟用應用時仍需同時顯示區塊標題及至少一張卡片 |
| TC-043 | 使用者首頁－模型選單 | 展開模型選單 | `tests/test_user_home.py` | 模型選單可正常展開並顯示選單容器 | 模型選單正常展開 | Pass | 不切換模型、不送出訊息；可用模型清單依環境資料而定，不列為固定條件 |
| TC-044 | 使用者介面－提示詞庫 | 開啟提示詞庫、驗證靜態內容後返回首頁 | `tests/test_user_home.py` | 顯示提示詞庫標題、新增按鈕與表格欄位；點擊開始新的對話後返回首頁 | 提示詞庫可正常開啟及返回 | Pass | 不新增、修改、刪除或套用提示詞 |
| TC-045 | 使用者介面－AI 應用 | 開啟 AI 應用列表、驗證卡片後返回首頁 | `tests/test_user_home.py` | 啟用前無入口可依指定原因略過；啟用後入口案例必須通過 | 2026-10-29 同批次：啟用前 Skip，啟用後 Pass；後驗回歸 41 passed／5 skipped | 啟用前 Skip／啟用後 Pass | 執行器只在 regression_before 額外允許指定入口缺少；regression_after 若略過、失敗或缺少皆 FAIL |
| TC-046 | 使用者介面－帳號及設定 | 展開帳號及設定選單 | `tests/test_user_home.py` | 顯示系統提示詞、模型參數設定、語言與登出 | 帳號及設定選單正常顯示 | Pass | 僅展開選單，不修改設定、不切換語言、不登出 |

## 左側功能選單範圍

目前已確認以下 9 個功能按鈕皆正常顯示；「總覽」已完成靜態內容與展開收合測試，其餘 8 個管理頁面也已完成第一階段唯讀測試：

1. 總覽
2. 使用者管理
3. 群組管理
4. LDAP設定
5. 模型管理
6. AI應用管理
7. API 端點
8. API 金鑰管理
9. 系統日誌

## 測試流程

1. 在 VS Code 或 iTerm 開啟專案 Terminal。
2. 進入專案資料夾並啟用 virtual environment。
3. 確認本機已有 `.auth/user.json`；此檔案只存放在本機，不提交至 Git。
4. 先執行新增或修改的單一測試，必要時使用 `--headed` 觀察操作。
5. 單一測試通過後，執行完整回歸測試。
6. 確認測試總數、通過數量與執行時間。
7. 更新本文件與 `PLAYWRIGHT_NOTES.md`，再分別提交測試程式及文件。

```bash
cd ai_hub-playwright-test
source .venv/bin/activate
python -m pytest -v
```

若所有需要登入的測試同時失敗或被導向登入頁，先確認 `.auth/user.json` 是否存在及登入狀態是否過期；重新儲存登入狀態後再執行測試。

## 執行方式

### 執行全部測試

```bash
python -m pytest -v
```

### 顯示瀏覽器執行全部測試

```bash
python -m pytest -v --headed
```

### 只執行 Platform Manager 測試

```bash
python -m pytest tests/test_platform_manager.py -v
```

### 只執行使用者介面唯讀與低風險互動測試

```bash
python -m pytest tests/test_user_home.py -v
```

### 只執行總覽測試

```bash
python -m pytest tests/test_platform_manager.py -k overview -v --headed
```

### 只執行中英文切換測試

```bash
python -m pytest tests/test_platform_manager.py::test_interface_language_can_be_switched -v --headed
```

### 只執行使用者管理唯讀測試

```bash
python -m pytest tests/test_platform_manager.py -k "user_management or add_user_modal or user_action_menu" -v --headed
```

### 只執行群組管理唯讀測試

```bash
python -m pytest tests/test_platform_manager.py -k "group_management or add_group_page or group_action_menu" -v --headed
```

### 只執行模型管理唯讀測試

```bash
python -m pytest tests/test_platform_manager.py -k "model_management or model_activity or model_action" -v --headed
```

### 只執行 LDAP 設定唯讀測試

```bash
python -m pytest tests/test_platform_manager.py -k "ldap" -v --headed
```

### 只執行 AI 應用管理唯讀測試

```bash
python -m pytest tests/test_platform_manager.py -k "ai_application" -v --headed
```

### 只執行 API 端點唯讀測試

```bash
python -m pytest tests/test_platform_manager.py -k "api_endpoint" -v --headed
```

### 只執行 API 金鑰管理唯讀測試

```bash
python -m pytest tests/test_platform_manager.py -k "api_key" -v --headed
```

### 只執行系統日誌唯讀測試

```bash
python -m pytest tests/test_platform_manager.py -k "system_log" -v --headed
```

## 第二階段 AI 應用獨立測試（2026-10-21）

以下測試需指定 `tests/manual_ai_application_activation.py`，**不納入**上述 `41 passed, 5 skipped` 的完整回歸統計；`manual_*.py` 不會被 pytest 預設收集。

| 案例 | 對象及預期 | 已知實測 | 狀態 |
|---|---|---|---|
| TC-049 | AFS MyAgent 唯讀預檢：正確讀取狀態，不下載／啟停／刪除 | 曾讀得 `enabled`、`PASSED` | Pass |
| TC-050 | AFS MyAgent 已下載未啟用 → 展開指定列 ⋯ → 點「啟用」→ enabled → 使用者端「開始使用」 | 2026-10-29 批次 `20261029T034521_440063Z_8770`：約 29.9 秒達 enabled，「開始使用」驗證通過；該操作型階段共 2 passed。歷史成功：1 passed in 31.05s、1 passed in 30.98s | Pass |
| TC-051 | 已啟用 → 自動停用 → 重新啟用（須明確授權）→ 使用者端驗證 | **最近已確認的完整停用循環：2026-10-28 PASS**：15:39 統一完整批次 `2 passed in 155.52s`，AFS MyAgent 完整啟停及「開始使用」PASS；同批次前後一般回歸也 PASS。歷史成功：`2 passed in 139.70s`、2026-10-21 `1 passed in 34.87s`。歷史失敗：應用曾在 `1 passed, 1 failed in 406.08s` 中返回未啟用且 300 秒逾時，根因未明。 本輪 10/29 AFS MyAgent 起始未啟用，不將本輪算作此循環重驗。 | 歷史 Pass／Fail 保留 |
| TC-052 | 使用者端 AFS MyAgent 卡片 → 點擊「開始使用」→ 確認畫面／網址／分頁切換；不傳訊息 | 2026-10-29 隨 test_ai_app_activation 實機通過；先前獨立結果 1 passed in 4.19s、未啟用時 1 skipped in 3.17s 保留 | Pass |
| TC-053 | AFS MyAgent 未下載 → 經雙重授權點「下載」→ 等待「已下載未啟用」→ 點「啟用」→ `enabled` → 點「開始使用」；不發送訊息 | 下載白名單、授權與狀態檢查已補強；未下載分支僅通過本機模擬，**實際 Hub 下載仍未執行**。另需 `AI_APP_TEST_WRITE=I_UNDERSTAND` + `AI_APP_TEST_ALLOW_DOWNLOAD=YES`；不納入一般回歸。 | Not Run |
| TC-054 | AFS MyAgent 原本已啟用 → 不停用，直接點「開始使用」；未啟用時唯讀測試略過 | 已啟用狀態下，`test_ai_app_start_only` 實測 `1 passed in 4.19s`；不下載、不啟停、未傳訊息。`test_ai_app_start_only` 維持唯讀；新版 `test_ai_app_activation` 無停用授權時直接驗證，有 `AI_APP_TEST_ALLOW_DISABLE=YES` 且已啟用時會執行停用／重新啟用。 | Pass |



**AFS MyAgent 條件式操作流程（三種起始狀態已實作；「未下載」分支待實機驗證）**

**2026-10-21 歷史完整啟停循環（TC-051）曾通過；2026-10-28 一度逾時失敗，後續 15:39 同批次完整驗證再次 PASS，詳見本文件開頭。以下保留 10/21 的歷史證據：**

```text
tests/manual_ai_application_activation.py::test_ai_app_disable_enable_cycle[chromium] PASSED
1 passed in 34.87s
```

- 本次以 `enabled` 開始；停用後 `downloaded_disabled`（約 1.1 秒），重新啟用至 `enabled`（約 27.3 秒）；「開始使用」已點擊並確認畫面／網址／分頁切換，未發送訊息。
- 需明確設定 `AI_APP_TEST_WRITE=I_UNDERSTAND` 與 `AI_APP_TEST_ALLOW_DISABLE=YES`；這是獨立的會中斷服務的操作型測試，不列入一般 46 項回歸。
- 啟用等待上限為 **300 秒（5 分鐘）**，取消舊版「退回未啟用 20 秒就提前失敗」判斷；等待期間不重複送出啟用。模型的啟用上限仍為 **600 秒（10 分鐘）**。
- 修正前曾有 `1 failed in 27.48s`，觀察到 `enabling → downloaded_disabled`，不能直接認定是 20 秒等待造成後端失敗；此紀錄保留供追查。



`test_ai_app_activation` 在 `not_downloaded` 狀態下，需同時設定 `AI_APP_TEST_WRITE=I_UNDERSTAND` 及 `AI_APP_TEST_ALLOW_DOWNLOAD=YES`，才會執行真正下載；下載完成後啟用。若已下載未啟用則直接啟用（歷史及 2026-10-28 一般模式實測通過）；若已啟用且沒有 `AI_APP_TEST_ALLOW_DISABLE=YES`，則不停用、直接驗證「開始使用」。**若已啟用且有停用授權，則改為停用 → 重新啟用。** 過程中不發送訊息，並且不納入一般 46 項唯讀回歸。

```bash
# 唯讀預檢：先確認 AFS MyAgent 當下的真實狀態
python -m pytest tests/manual_ai_application_activation.py::test_ai_app_preflight -v -s --headed

# 已經確認授權下載與啟用後，再單獨執行
AI_APP_TEST_WRITE=I_UNDERSTAND \
AI_APP_TEST_ALLOW_DOWNLOAD=YES \
python -m pytest tests/manual_ai_application_activation.py::test_ai_app_activation -v -s --headed --slowmo 300
```

檔案很大（先前畫面約 2.49 GB），執行下載前應確認環境、儲存空間、網路流量與授權。若已有下載／啟用／停用中的操作，測試將略過以避免干擾。「已下載未啟用 → 啟用 → 開始使用」及「已啟用 → 開始使用」已實際執行並標記 Pass；**未下載 → 下載**分支仍需在符合條件的測試環境實測；按下 `Control + C` 只能停止本機測試，不能保證取消已送出的後端下載或啟用。失敗時可查閱 `reports/ai_application_activation/failure.png`（如成功存檔）。

早前兩次啟用失敗觀察到 `enabling → downloaded_disabled`，且連續 20 秒未恢復。修正下拉選單展開與可見選項驗證後，已有一次成功紀錄；**尚不能確認前兩次失敗的單一根因**。操作型測試不應自動納入 CI 或一般回歸。

## 狀態定義

| 狀態 | 說明 |
|---|---|
| Pass | 實際結果符合預期結果 |
| Fail | 實際結果不符合預期結果，需進一步確認網站或測試程式 |
| Skip | 因目前環境缺少資料或未啟用資源等前置條件而略過；不代表測試失敗 |
| Blocked | 因環境、權限、資料或其他前置條件而無法執行 |
| Not Run | 測試案例已建立，但尚未執行 |

## 後續測試規劃

第一階段 A＋B 共 46 項測試，2026-10-29 啟用前為 40 項通過／6 項略過，啟用後為 41 項通過／5 項略過、0 項失敗；後驗仍略過的五項因缺少群組、LDAP、API 端點或 API 金鑰資料／條件；平台管理 9 個側欄功能頁面，以及使用者首頁、提示詞庫、AI 應用與帳號設定的唯讀／低風險互動測試已完成。以下項目列為第二階段候選，不影響第一階段結案：

| 功能 | 建議測試內容 | 目前狀態 |
|---|---|---|
| 總覽資料驗證 | 有可控制的測試資料後，補充 Token 排名、資料列與數值驗證 | 第二階段；待測試資料 |
| 搜尋、篩選與分頁 | 依各管理頁的實際元件與資料狀態驗證查詢、篩選及換頁結果 | 第二階段；待測試資料 |
| 資料異動流程 | 新增、修改、刪除、啟用／停用、展延、權限與成員管理等流程 | 第二階段；待專用帳號與可控制資料 |
| 本機 HTML 測試報告 | 使用 pytest-html 產出單一 HTML 報告，確認可開啟及查看測試結果／Skip 原因 | 已完成，本機報告可產生並開啟 |
| CI 自動執行 | 評估 Push 後執行 Playwright，須先確認測試站連線與安全登入機制 | 尚未進行；與本機報告分開 |

## 維護原則

- 新增自動化測試時，同步新增或更新本文件的測試案例。
- 測試案例名稱應描述使用者操作與預期結果，不以 `.py` 檔名代替測試項目。
- 正式回歸測試完成後，更新最近執行日期、通過數量、失敗數量及執行時間。
- 測試失敗時，先判斷是網站功能問題、測試資料問題、環境問題，或 Locator／預期文字需要調整。
- 涉及新增、修改或刪除資料的測試，應使用專用測試資料，避免影響正式資料。


### 2026-10-21｜AFS MyAgent 兩項操作驗證與下載安全檢查

- `test_ai_app_activation`：起始為 `downloaded_disabled`，按「啟用」，畫面轉為 `enabling`，約 26.8 秒後到 `enabled`，點「開始使用」並觀察到切換；`1 passed in 30.98s`。**此批次沒有下載。**
- `test_ai_app_start_only`：在 `enabled` 狀態下直接點「開始使用」，不執行下載／啟用／停用，未發送訊息；`1 passed in 4.19s`。
- `test_ai_app_activation` 的 `not_downloaded` 分支：允許「下載」操作前會核對 `AI_APP_TEST_WRITE=I_UNDERSTAND` 及 `AI_APP_TEST_ALLOW_DOWNLOAD=YES`，並要求目前狀態確實為 `not_downloaded`，避免誤點或重複下載。
- 任何寫入都需要主授權，停用另需 `AI_APP_TEST_ALLOW_DISABLE=YES`；下載若出現未確認的對話框，停止並截圖，不自動同意。
- **實際 Hub 下載尚未實測**；不為了取得 Pass 刪除已下載的 AI 應用。該歷史段落記錄的一般 46 項回歸為 `41 passed, 5 skipped in 53.14s`；最新同批次完整驗證請見本文件開頭，真正下載分支仍未實測。


### 2026-10-21｜AFS MyAgent 啟用後的歷史完整回歸（44.85 秒）

- **共 46 項、41 passed、5 skipped、0 failed，44.85 秒**。
- `TC-045` 使用者介面 AI 應用列表測試：原先無應用啟用時 `Skip`，現在已能執行並 `Pass`。
- 五項略過分別為 `TC-022` 群組功能選單、`TC-028` LDAP 功能選單、`TC-029` LDAP 修改頁、`TC-033` API 端點明細、`TC-035` API 金鑰功能選單；不建立額外資料來消除 Skip。
- 本批 46 項是一般唯讀／低風險回歸，與先前 `test_ai_app_activation`、`test_ai_app_start_only`、`test_ai_app_preflight` 的獨立執行結果分開計算。
- 當時下載分支及完整停用→重新啟用循環尚未取得成功紀錄；**此後完整停用→重新啟用循環已實測 PASS（34.87 秒），僅真正下載分支仍待實測。**


### 後續獨立操作型測試（2026-10-21，更新狀態）

`test_ai_app_disable_enable_cycle` 在調整 AI 應用 300 秒啟用上限、移除 20 秒提前判失敗後，於實際測試環境重新執行 **`1 passed in 34.87s`**；因此 **TC-051 現已 Pass**。真正「未下載 → 下載」分支仍 **Not Run**（TC-053），不應為了測試而移除已下載的應用。此結果不另外加進一般 46 項回歸的 Passed 數量。

## Gherkin 情境與回歸驗證進度

| 驗證項目 | 結果 |
|---|---|
| 登入、登出與回訪管理頁 | 實機 `1 passed in 13.77s` |
| 模型啟用、非空白回覆與重開對話 | 實機 `1 passed in 507.39s`，此輪未觀察到重試 |
| AFS MyAgent 啟用與開始使用 | 實機 `1 passed in 89.16s` |
| 三條獨立情境一起執行 | 實機 `3 passed in 39.17s`，模型與 MyAgent 起始已啟用 |
| 先前整合流程（既有 pytest 回歸） | 後回歸 `41 passed, 5 skipped in 55.88s`，登出與回訪通過，整輪 `[overall]` 待確認 |
| 46 項 Gherkin 回歸 | 已收集 46 項，離線模擬 46 項通過 |
| 新版 Gherkin 完整流程 | 2026-11-13 實機 PASS，批次 `20261113T075051_482154Z_94086`。後回歸 `41 passed, 5 skipped in 61.02s`。登出與登入狀態清理 PASS，回訪管理頁仍要求登入 |

### 既有回歸與 Gherkin 對照

平台管理共 38 項，使用者首頁 7 項，站台連線 1 項。`Scenario Outline` 的每列各自執行並計為一項。

| 原測試檔 | pytest 案例 | Gherkin 情境 | 項數 |
|---|---|---|---:|
| `test_site_access.py` | `test_platform_manager_endpoint_has_no_server_error` | 平台管理入口可回應且頁面可顯示 | 1 |
| `test_platform_manager.py` | `test_platform_manager_is_loaded` | 載入平台管理頁 | 1 |
| `test_platform_manager.py` | `test_main_menu_is_visible` | 顯示平台管理主選單 | 1 |
| `test_platform_manager.py` | `test_interface_language_can_be_switched` | 繁體中文與英文切換 | 1 |
| `test_platform_manager.py` | `test_main_menu_sections_can_be_opened` | 開啟平台管理主選單項目 | 8 |
| `test_platform_manager.py` | `test_overview_static_content_is_visible` | 顯示總覽主要內容 | 1 |
| `test_platform_manager.py` | `test_overview_section_can_be_collapsed_and_expanded` | 總覽區塊可收合並重新展開 | 3 |
| `test_platform_manager.py` | `test_user_management_static_content_is_visible` | 顯示使用者管理內容 | 1 |
| `test_platform_manager.py` | `test_add_user_modal_can_be_opened_and_cancelled` | 開啟並取消新增使用者 | 1 |
| `test_platform_manager.py` | `test_user_action_menu_is_visible` | 顯示使用者功能選單 | 1 |
| `test_platform_manager.py` | `test_group_management_static_content_is_visible` | 顯示群組管理內容 | 1 |
| `test_platform_manager.py` | `test_add_group_page_can_be_opened_and_returned` | 開啟新增群組頁並返回 | 1 |
| `test_platform_manager.py` | `test_group_action_menu_is_visible` | 顯示群組功能選單 | 1 |
| `test_platform_manager.py` | `test_model_management_static_content_is_visible` | 顯示模型管理內容 | 1 |
| `test_platform_manager.py` | `test_model_activity_can_be_expanded_and_collapsed` | 展開與收合模型活動 | 1 |
| `test_platform_manager.py` | `test_model_action_menu_is_visible` | 顯示模型功能選單 | 1 |
| `test_platform_manager.py` | `test_ldap_settings_static_content_is_visible` | 顯示 LDAP 設定內容 | 1 |
| `test_platform_manager.py` | `test_add_ldap_settings_page_can_be_opened_and_returned` | 開啟新增 LDAP 設定頁並返回 | 1 |
| `test_platform_manager.py` | `test_ldap_action_menu_is_visible` | 顯示 LDAP 功能選單 | 1 |
| `test_platform_manager.py` | `test_edit_ldap_settings_page_is_visible` | 開啟 LDAP 修改頁並返回 | 1 |
| `test_platform_manager.py` | `test_ai_application_management_static_content_is_visible` | 顯示 AI 應用管理內容 | 1 |
| `test_platform_manager.py` | `test_ai_application_action_menu_is_visible` | 顯示 AI 應用功能選單 | 1 |
| `test_platform_manager.py` | `test_api_endpoint_static_content_is_visible` | 顯示 API 端點內容 | 1 |
| `test_platform_manager.py` | `test_enabled_api_endpoint_details_are_visible` | 查看已啟用的 API 端點明細 | 1 |
| `test_platform_manager.py` | `test_api_key_management_static_content_is_visible` | 顯示 API 金鑰管理內容 | 1 |
| `test_platform_manager.py` | `test_api_key_action_menu_is_visible` | 顯示 API 金鑰功能選單 | 1 |
| `test_platform_manager.py` | `test_add_api_key_modal_can_be_opened_and_cancelled` | 開啟並取消新增 API 金鑰 | 1 |
| `test_platform_manager.py` | `test_system_log_static_content_is_visible` | 顯示系統日誌內容 | 1 |
| `test_platform_manager.py` | `test_system_log_range_options_are_visible` | 顯示系統日誌時間範圍選項 | 1 |
| `test_platform_manager.py` | `test_system_log_zip_can_be_downloaded` | 下載系統日誌 ZIP | 1 |
| `test_user_home.py` | `test_user_home_is_loaded` | 載入使用者首頁 | 1 |
| `test_user_home.py` | `test_user_sidebar_is_visible` | 顯示使用者側欄 | 1 |
| `test_user_home.py` | `test_user_home_static_content_is_visible` | 顯示使用者首頁內容 | 1 |
| `test_user_home.py` | `test_model_menu_can_be_opened` | 開啟模型選單 | 1 |
| `test_user_home.py` | `test_prompt_library_can_be_opened_and_returned` | 開啟提示詞庫並返回 | 1 |
| `test_user_home.py` | `test_ai_apps_can_be_opened_and_returned` | 開啟 AI 應用並返回 | 1 |
| `test_user_home.py` | `test_account_settings_menu_is_visible` | 顯示帳號及設定選單 | 1 |
