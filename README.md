# AI Hub 自動化測試

使用 Python＋Playwright，透過瀏覽器驗證 AI Hub 的平台管理、使用者介面、模型與 AI 應用操作，以及模型對話流程。

本專案由本機指令啟動，目前不包含 CI。一般回歸與服務操作分開授權；完整驗證會實際呼叫後端、可能暫時中斷服務，並建立一則真實對話。

## 測試內容

| 範圍 | 驗證內容 |
|---|---|
| 登入與登出 | 自動輸入帳密、驗證登入狀態；結束後登出，回訪管理頁確認仍要求登入 |
| 一般回歸 | 46 項案例，涵蓋網站連線、平台管理頁面、側欄導航、表格／功能選單、空狀態與使用者介面 |
| 模型操作 | 依起始狀態啟用，或停用後重新啟用；確認使用者端可選模型與輸入 |
| AI 應用操作 | 依起始狀態啟用，或停用後重新啟用；確認 AFS MyAgent「開始使用」可進入 |
| 模型對話 | 送出一則訊息、確認新 sessionId 與非空白回覆，從歷史紀錄重新開啟同一對話 |

目前主要操作對象為 **Llama3.1-FFM-8B** 與 **AFS MyAgent**。測試站需具備對應資料及操作權限；若目標名稱或介面不同，需先核對測試程式。

## 1. 執行前準備

- Python 3.10 以上；實際相容版本與套件依專案 `requirements.txt` 為準。
- 取得完整專案，保留資料夾結構，不要只複製個別測試檔。
- 電腦能連線至測試站；若有公司內網或 VPN 限制，先完成連線。
- 自備可登入且具備測試範圍所需權限的測試帳號。
- 完整驗證前，確認環境允許模型與 AI 應用暫時停用、重新啟用及建立測試對話。

以下指令以 **macOS／Linux 的 Bash 或 Zsh** 為例，可在 Terminal 或 iTerm 執行。

## 2. 首次安裝

取得 Git 專案後，進入專案根目錄：

```bash
cd ai_hub-playwright-test
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

之後每次重新開啟終端機，只需進入專案並啟用虛擬環境：

```bash
cd ai_hub-playwright-test
source .venv/bin/activate
```

`.venv` 是 Python 虛擬環境；`source .venv/bin/activate` 不會讀取 `.env`。網址與帳密由程式另外載入。

## 3. 設定測試網址與帳密

若專案提供 `.env.example`，複製後填入自己的設定：

```bash
cp .env.example .env
```

若沒有範例檔，在專案根目錄自行建立 `.env`，至少包含：

```dotenv
BASE_URL=https://your-ai-hub.example.com
TEST_USERNAME=your_test_account
TEST_PASSWORD=your_test_password
```

- `BASE_URL` 填網站根網址，不要包含 `/platform-manager`、登入網址、查詢參數或帳密。
- 請將範例值換成實際設定；帳密含特殊字元時，依 dotenv 格式使用引號包住。
- 切換測試站時修改 `BASE_URL`，並重新登入；不要沿用另一站的登入狀態。
- `.env` 與 `.auth/` 屬於本機資料，不可提交 Git 或當作交接檔傳送。

目前自動登入使用既有 AI Hub 的登入／登出元件定位。其他環境若介面不同，可核對 `scripts/save_login_state.py` 的 `AUTH_*_SELECTOR` 設定；不要只替換網址就假設所有定位都相容。

## 4. 選擇執行模式

### A. 一般回歸：不操作服務啟停

建議第一次接手先執行此模式，確認環境、帳號與介面可用：

```bash
PYTEST_ADDOPTS="" \
python scripts/run_validation.py --auto-login
```

執行自動登入、46 項一般回歸與最後登出；不加入模型／AI 應用啟停，也不送出模型對話。

若已有有效的本機登入狀態，可執行：

```bash
python scripts/run_validation.py
```

沒有 `--auto-login` 時，不會自動輸入帳密或提供整輪自動登出流程。登入狀態不存在或過期時，可先另行執行：

```bash
python scripts/save_login_state.py --auto
```

這個獨立指令會驗證並儲存 `.auth/user.json`，供後續測試使用。

### B. 完整驗證／Demo：登入、前後回歸、啟停與對話

**此模式可能中斷目前運作中的模型與 AI 應用，並保留一則測試對話。請只在已允許操作的環境執行。**

```bash
PYTEST_ADDOPTS="" \
MODEL_TEST_WRITE=I_UNDERSTAND \
MODEL_TEST_ALLOW_DISABLE=YES \
MODEL_TEST_ALLOW_RETRY=YES \
AI_APP_TEST_WRITE=I_UNDERSTAND \
AI_APP_TEST_ALLOW_DISABLE=YES \
AI_APP_TEST_ALLOW_RETRY=YES \
python scripts/run_validation.py --auto-login --manual-activation --chat-send
```

不需要先執行 `save_login_state.py --auto`，完整指令已包含自動登入。

流程順序：

1. 檢查 Python 語法與一般回歸案例收集範圍。
2. 自動登入並驗證登入狀態。
3. 執行操作前的 46 項一般回歸。
4. 執行模型操作，並送出一則訊息，確認回覆與歷史紀錄。
5. 執行 AI 應用操作，確認「開始使用」可進入。
6. 再執行一次 46 項一般回歸。
7. 登出並回訪管理頁，確認仍要求登入，產出整輪摘要。

前置檢查或前回歸未通過時，不會進入後續服務操作。實際已執行與未執行階段，以該批次摘要為準。

| 指令參數 | 意思 |
|---|---|
| `--auto-login` | 本輪自動登入，結束時執行登出驗證 |
| `--manual-activation` | 加入模型與 AI 應用操作，以及操作後回歸；瀏覽器點擊仍由程式執行 |
| `--chat-send` | 在模型操作案例內加入真實對話送出、回覆與歷史重開驗證 |

| 環境變數 | 授權內容 |
|---|---|
| `MODEL_TEST_WRITE=I_UNDERSTAND` | 允許模型寫入操作 |
| `MODEL_TEST_ALLOW_DISABLE=YES` | 允許停用已啟用模型 |
| `MODEL_TEST_ALLOW_RETRY=YES` | 符合條件時允許最多一次啟用重試 |
| `AI_APP_TEST_WRITE=I_UNDERSTAND` | 允許 AI 應用寫入操作 |
| `AI_APP_TEST_ALLOW_DISABLE=YES` | 允許停用已啟用 AI 應用 |
| `AI_APP_TEST_ALLOW_RETRY=YES` | 符合條件時允許最多一次啟用重試 |

重試不是固定點擊兩次；第一次成功就繼續下一步。上述指令沒有授予下載權限：模型未下載時不會自行下載；AI 應用的下載需另有專門授權與前置條件，不能把上述啟用指令視為已允許下載。

實際操作依起始狀態決定：已下載未啟用時直接啟用；已啟用且獲停用授權時，先停用再啟用。`2 passed` 本身不能證明兩者都實際走過停用流程，需對照日誌。

### 瀏覽器顯示與速度

| 階段 | 目前設定 |
|---|---|
| 登入與登出 | 顯示瀏覽器，操作間隔 1 秒 |
| 前後一般回歸 | 背景執行，不額外放慢 |
| 模型／AI 應用操作、對話與歷史紀錄 | 顯示瀏覽器，操作間隔 1 秒 |

登入視窗可能保留到最後登出；一般回歸仍在背景執行。1 秒是 Playwright 操作間隔，不是帳密逐字輸入速度，也不是每個等待都固定 1 秒。

指令最前方的 `PYTEST_ADDOPTS=""` 用來清除繼承的額外 pytest 參數，避免先前全域 `--headed` 讓一般回歸也顯示視窗。

## 5. 查看結果與交付報告

執行結束先確認終端機的 **`[overall] PASS`**，再查看：

- `reports/validation_summary.md`：最近一次執行摘要。
- `reports/validation_summary.json`：最近一次結構化結果。
- `reports/validation_runs/<批次目錄>/`：該次執行的摘要、日誌、JUnit XML 與 HTML 報告。

完整驗證的三份 HTML 各自代表不同階段：

| 報告 | 用途 |
|---|---|
| `regression_before.html` | 操作前一般回歸 |
| `manual_activation.html` | 模型與 AI 應用操作；啟用 `--chat-send` 時，對話驗證包含於模型案例內 |
| `regression_after.html` | 操作後一般回歸 |

一般模式或前置阻擋的批次不一定產生全部三份報告。`reports/report.html` 是另行使用 pytest 報表指令產生的單輪報告，不會自動合併這三個階段，也不能當作最新完整批次。

給主管或接手者查看時，請提供**同一批次**的摘要與報告，避免混用不同時間的結果。

若直接開啟 HTML 顯示不完整，在專案根目錄另開終端機執行：

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory reports
```

瀏覽器開啟 <http://localhost:8000/validation_runs/>，選擇批次目錄。結束後在該終端機按 `Ctrl+C` 關閉報告伺服器。

### 統計怎麼看

- `PASSED`：該案例通過。
- `FAILED`／`ERROR`：案例失敗或執行發生錯誤，需查看日誌。
- `SKIPPED`：因前置條件或資料不足而略過，不算實際通過；需核對原因。
- 46 項是一般回歸案例數；前後各跑同一組，操作型 2 項另計，登入／登出另列流程階段。

最近一次已回報的完整實測整體 PASS，約 4 分 8 秒：前後回歸各 **41 passed、5 skipped**，操作型 **2 passed**，登入／登出通過。五項略過與群組、LDAP、API 端點及金鑰的資料或啟用條件不足有關。這是既有環境的結果，其他電腦與測試站仍需自行首次驗證。

## 6. 常見問題

| 問題 | 優先檢查 |
|---|---|
| 找不到 Python 套件或 pytest | 是否啟用 `.venv`，並在同一環境安裝 `requirements.txt` |
| 找不到瀏覽器執行檔 | 執行 `python -m playwright install chromium` |
| 找不到「模型管理」，畫面停在登入頁 | 登入狀態可能失效；使用 `--auto-login`，或先重新儲存登入狀態 |
| 自動登入失敗 | `.env` 網址、帳密、權限與登入元件定位；不要提供密碼或登入 Token 協助排查 |
| 出現 BLOCKED | 查看摘要指出的缺檔、環境或授權問題，不可當作 PASS |
| 啟用中後回到未啟用 | 查看當輪 `manual_activation.log`、啟用事件與部署狀態；先確認服務現況再決定是否重跑 |
| 看不到操作視窗 | 核對是否有 `--auto-login`、`--manual-activation`、`--chat-send`，以及是否已被前置關卡阻擋 |
| 回歸案例數不是 46 | 確認專案是否完整、測試檔是否變更；先審核差異，不要直接放寬數量門檻 |

失敗截圖與 Trace 通常位於 `test-results/`，實際位置以該次輸出為準。找到 `trace.zip` 後，可用 `python -m playwright show-trace` 搭配實際檔案路徑開啟。

## 7. 專案主要檔案

| 路徑 | 用途 |
|---|---|
| `pages/` | 頁面物件、元件定位與操作方法 |
| `tests/test_site_access.py` | 網站連線與載入驗證 |
| `tests/test_platform_manager.py` | 平台管理一般回歸 |
| `tests/test_user_home.py` | 使用者介面一般回歸 |
| `tests/manual_model_activation.py` | 模型操作與對話驗證 |
| `tests/manual_ai_application_activation.py` | AI 應用操作驗證 |
| `scripts/run_validation.py` | 整輪驗證與摘要入口 |
| `scripts/save_login_state.py` | 登入狀態與登入／登出流程 |
| `conftest.py` | pytest 共用 fixture 與瀏覽器／環境設定；請保留其原本位置 |
| `pytest.ini` | pytest 設定 |
| `requirements.txt` | Python 套件依賴 |
| `.env.example` | 無真實帳密的設定範例 |
| `TEST_CASES.md` | 案例與實測進度 |
| `PLAYWRIGHT_NOTES.md` | 定位、等待、登入與部署問題的排查紀錄 |

## 8. Git 與交接注意事項

應交付完整原始碼、共用設定、套件清單及文件。每台電腦自行建立虛擬環境、安裝瀏覽器、設定帳密與登入狀態。

請核對 `.gitignore` 至少排除以下本機資料；下列內容是建議規則，不代表已自動修改專案設定：

```gitignore
.env
.auth/
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
reports/
test-results/
```

`.env.example` 可以提交，但不可包含真實密碼。報告、日誌、截圖、Trace 與對話證據可能包含內部網址、帳號、對話識別碼或頁面內容，分享前需檢查。

## 9. 目前驗證範圍與後續工作

目前已確認一般回歸、服務操作、對話送出、非空白回覆、歷史重開及整輪登入／登出流程可通過。歷史停用再啟用成功紀錄保留於既有測試文件；每輪實際走過的路徑仍以該批次日誌為準。

以下不列為本次已完成的實機驗證：

- 模型是否遵守「只回覆 OK」或其他回答品質判定：延後處理；目前僅要求回覆非空白。
- 啟用失敗後第二次重試是否實際觸發：已有程式與離線檢查，目前尚缺確認實機觸發的證據。
- AI 應用從未下載開始，完成下載再啟用：尚缺實機通過證據。
- 登入失敗、回覆逾時、登出失敗及 `Ctrl+C` 等異常流程：目前尚缺本次實機驗證證據。

接手順序建議：先完成安裝與一般回歸，再於允許中斷服務的環境執行完整驗證，最後保存同批次摘要與報告。
