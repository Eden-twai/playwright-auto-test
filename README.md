# ai_hub-playwright-test

AI Hub 的 Playwright + Python 瀏覽器自動化測試專案。

主要涵蓋 Platform Manager 與使用者首頁的**唯讀／低風險回歸測試**，包括網站連線、登入後載入、側欄與頁面導航、表格與操作選單，以及依環境狀態顯示的 AI 應用入口。

- **最新同批次驗證 PASS（2026-10-29 11:45:21–11:56:07，台灣時間）**：批次 `20261029T034521_440063Z_8770`，啟用前 **40 passed／6 skipped**、模型與 AI 應用操作 **2 passed**、啟用後 **41 passed／5 skipped in 55.32s**；全部 0 failed／errors。基礎 Git Commit `2cbbbe4e`，當時**有未提交修改**；完整版本以同批次 JSON 的來源 SHA256 追溯。入口由啟用前略過轉為啟用後通過。這個 PASS 不單獨證明本輪兩者都有停用，也不證明重試第二次點擊已觸發。
- **本輪使用者端驗證範圍**：模型達 enabled、Chat 可選模型與輸入；AFS MyAgent 約 29.9 秒啟用後點「開始使用」，確認畫面／網址／分頁切換。均未送出訊息；實際模型回覆、首次下載與第二次重試實機觸發仍未確認。10/28 完整停用循環的歷史 PASS 與歷史 FAIL 保留在下方及 [TEST_CASES.md](TEST_CASES.md)。
- **Chat 首頁等待策略**：一般 UI 回歸的 `UserHomePage.expect_loaded()` 預設最多等待 **20 秒**；已獲授權的模型完整啟停，在重新啟用後驗證 Chat 首頁時指定 **100 秒**。失敗時另記錄去除 URL 查詢參數的頁面位置、標題與載入狀態。較早的一次模型雖已啟用，但 Chat 首頁驗證遭登入導向／白畫面干擾而 FAIL；本輪通過不等於已確認唯一根因。
- **2026-10-28 新增固定驗證入口**：`python scripts/run_validation.py`。這會檢查語法、核對 46 項收集範圍、執行一般回歸並留下獨立報表；具破壞性的完整啟停需另外明確授權。
- **2026-10-28 Mac 較早一般模式批次（歷史）PASS**：收集及執行 46 項，`41 passed, 5 skipped, 0 failed`；14:11–14:12（台灣時間），該輪執行器整體 `PASS`，當時 Git Commit 為 `5c91ddf`，但工作區有未提交修改。該批次沒有執行啟停及後驗回歸，不能與最上方的新批次混為同一輪。
- **2026-10-28 Mac 離線驗證已實測 PASS**：`selfcheck_validation.py` 5 項，以及新版 `verify_flow_offline.py` 18 項，兩者都不需登入 AI Hub；18 項包含 6 種原有狀態、10 種重試分支、授權檢查及失敗紀錄保留。
- **先前交付副本的歷史限制**：當時只取得部分修正版與文件 ZIP，因缺少三支一般回歸 `test_*.py`，在交付副本執行曾回報 `BLOCKED`。**這不代表你 Mac 的正式專案仍被阻擋**；後續已取得上述 10/28 Mac 完整回歸 PASS。
- 2026-10-21 的完整成功回歸為歷史紀錄：`41 passed, 5 skipped, 0 failed in 53.14s`（另有更早 44.85 秒批次）。
- 五項 Skip 因群組、LDAP、API 端點／金鑰的測試資料或啟用條件不足；不是失敗。
- AFS MyAgent 的下載／啟用等**會呼叫後端的操作型測試**另行手動觸發，不納入上述 46 項一般回歸。
- 維護歷史結果與測試案例請見 [TEST_CASES.md](TEST_CASES.md)，詳細排查紀錄請見 [PLAYWRIGHT_NOTES.md](PLAYWRIGHT_NOTES.md)。

## 0. 固定驗證入口與交付門檻（2026-10-28 新增）

將此交付包的 `scripts/run_validation.py`、`scripts/selfcheck_validation.py` 與修正版檔案合併回**完整專案根目錄**（保留你的 `conftest.py`、`pytest.ini`、`requirements.txt`、`.env` 與 `.auth`；不要以交付 ZIP 整包覆蓋完整專案）。

### 在 Mac 的 iTerm 執行：登入狀態確認 → 測試

**iTerm 是執行 Python 測試指令的 Terminal，不負責登入網站。** Playwright 會使用本機保存的登入狀態；**不必每次測試前重新登入**，但登入狀態不存在或過期時，必須先更新。

1. 開啟 iTerm，進入專案資料夾並啟用虛擬環境：

   ```bash
   cd ai_hub-playwright-test
   source .venv/bin/activate
   ```

2. 確認 `.env` 的 `BASE_URL` 是本次要測的 AI Hub 網址，且 `.auth/user.json` 已存在。**檔案存在不代表登入一定有效**。
3. 第一次測試、切換網站，或測試被導向登入頁時，在 iTerm 執行：

   ```bash
   python scripts/save_login_state.py
   ```

   腳本開啟 Chromium 後，**在瀏覽器手動登入並確認進入 Platform Manager**，再回 iTerm 按 Enter，更新 `.auth/user.json`。不要在 Chat、Git 或報告中貼出此檔案。
4. 登入有效後，執行一般回歸：

   ```bash
   python scripts/run_validation.py
   ```

5. 查看 `reports/validation_summary.md`，核對收集 46 項、Pass／Fail／Skip、Skip 原因與 Git 工作區狀態；只有通過且另外獲得服務中斷授權，才考慮 `--manual-activation`。

**純離線檢查不需要登入、瀏覽器或 AI Hub 連線**，可直接執行：

```bash
python -m unittest scripts/selfcheck_validation.py -v
python verify_flow_offline.py
```

**一般模式（預設唯讀／低風險；不會執行 `manual_*.py`）：**

```bash
python scripts/run_validation.py
```

**修改特定功能後，先跑指定案例再跑 46 項：**

```bash
python scripts/run_validation.py \
  --target tests/test_platform_manager.py::test_platform_manager_is_loaded
```

**完整啟停模式（會中斷模型與 AI 應用服務；僅限允許操作的測試環境）：**

```bash
MODEL_TEST_WRITE=I_UNDERSTAND \
MODEL_TEST_ALLOW_DISABLE=YES \
AI_APP_TEST_WRITE=I_UNDERSTAND \
AI_APP_TEST_ALLOW_DISABLE=YES \
python scripts/run_validation.py --manual-activation
```

**啟停並開啟兩者各自最多一次重試（環境已允許啟停與重試時）：**

```bash
MODEL_TEST_WRITE=I_UNDERSTAND \
MODEL_TEST_ALLOW_DISABLE=YES \
MODEL_TEST_ALLOW_RETRY=YES \
AI_APP_TEST_WRITE=I_UNDERSTAND \
AI_APP_TEST_ALLOW_DISABLE=YES \
AI_APP_TEST_ALLOW_RETRY=YES \
python scripts/run_validation.py --manual-activation
```

重試預設關閉；上面兩個重試旗標必須明確加入才開啟。第一次成功就不會點第二次。執行器不會自動授予下載權限。起始為已下載未啟用時直接啟用；起始已啟用且有停用授權時，才執行停用再啟用，不能只看模式名稱判定操作路徑。

一般回歸預設不主動顯示瀏覽器；操作型階段會加入 `--headed --slowmo 300`。前置關卡未通過時不會進入操作型階段，因此不會看到該階段的瀏覽器。

| 固定關卡 | 一般模式 | 完整啟停模式 |
|---|---|---|
| 1. Python 靜態語法 | 必跑 | 必跑 |
| 2. pytest 收集數與清單核對 | 三支 `test_*.py`，應收集 **46 項** | 同左 |
| 3. 指定單項測試 | 有提供 `--target` 才執行 | 有提供才執行 |
| 4. 一般完整回歸 | 必跑，0 FAILED／0 ERROR | 啟停前必跑 |
| 5. 模型＋AI 應用完整啟停 | **不執行** | 四項明確授權後執行 |
| 6. 啟停後再次回歸 | **不適用** | 必跑；即使啟停失敗也保留後驗結果 |

- 一般回歸必須收集及實際執行 **46 項**，每項 Skip 必須有原因；其他略過預設最多 **5 項**。`regression_before` 對指定入口案例 `test_ai_apps_can_be_opened_and_returned` 且原因為「使用者介面沒有 AI 應用入口」，另外允許最多 **1 項**；仍保留實際 6 skipped 與原因，不改成 Pass。這是依測試名稱與原因判定，入口缺少是否符合環境狀態仍須核對。
- `regression_after` 要求 AI 應用入口案例實際通過；略過、失敗或缺少皆 FAIL，即使提高 `--max-regression-skips` 也不能繞過。其他五項的數量上限不是案例白名單，仍要人工核對原因。新增／刪除案例時先審核，再調整 `--expected-regression-count`；不需為正常的啟用前空狀態改成 `--max-regression-skips 6`。
- 靜態、單項、收集數或前置回歸失敗會阻止後續啟停；`--target` 限定既有一般測試檔，無法藉此插入操作型測試。缺少必要測試檔就回報 `BLOCKED`，不當成 PASS。
- 每輪自動保存 `reports/validation_summary.json`、`reports/validation_summary.md`，及 `reports/validation_runs/<執行批次>/` 中的日誌、JUnit XML、可能的 HTML 報告與歷史摘要；記錄時間（台灣時區）、Git Commit、工作區狀態、來源檔 SHA256、Skip 原因。
- 一般回歸 PASS **不代表**服務啟停 PASS；操作型測試 PASS 也**不代表**修改後 46 項回歸 PASS。只有本輪必要關卡都完成，摘要才標示整體 `PASS`。
- 如執行器回傳非零：`1` 表示測試失敗，`2` 表示環境或授權阻擋，`130` 表示中止；不得據此更新為「已驗證通過」。報表、截圖、Trace 可能包含敏感資訊，切勿直接提交公開 Git。

執行器自身的離線驗證（不連 AI Hub）：

```bash
python -m unittest scripts/selfcheck_validation.py -v
```

## 1. 建立 Python 環境

macOS Terminal：

```bash
cd ai_hub-playwright-test
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

之後每次重新開 Terminal，只需要：

```bash
cd ai_hub-playwright-test
source .venv/bin/activate
```

## 2. 設定測試網址

複製環境設定範例：

```bash
cp .env.example .env
```

目前文件記錄的測試站是 `https://202.5.254.27/`。若網址變更，請修改 `.env` 內的 `BASE_URL`；專案 `conftest.py` 會讀取這個設定。**通常不需要同時在指令加上 `--base-url`**，避免不同來源的設定混淆。

## 3. 先執行不需登入的 Smoke Test

```bash
pytest tests/test_site_access.py -v
```

這支測試會開啟 `/platform-manager`，確認網站有回應、畫面可顯示，且沒有 5xx 錯誤。因為系統可能把未登入使用者導回登入頁，所以它不要求一定停留在 Platform Manager。

## 4. 首次登入或登入過期時，儲存登入狀態

```bash
python scripts/save_login_state.py
```

程式會開啟 Chromium：

1. 請在瀏覽器中手動完成登入。
2. 確認已經進入 Platform Manager。
3. 回到 Terminal 按 Enter。

登入狀態會儲存在 `.auth/user.json`。這個檔案可能包含敏感的登入資訊，已加入 `.gitignore`，請勿 commit 或傳給其他人。

如果登入狀態仍有效，可以直接在 iTerm 執行驗證指令，**不需每次重新產生 `.auth/user.json`**。若頁面被導向 `openid-connect/auth` 或登入頁，先更新登入狀態，再重新執行受影響的測試。

## 5. 直接使用 pytest 與 HTML 報告（保留作診斷；正式驗證優先用統一執行器）

先確認 `.env` 的測試網址，以及 `.auth/user.json` 的登入狀態。以下是原本直接使用 pytest 的替代指令；正式回歸與統一摘要請優先使用 `python scripts/run_validation.py`：

```bash
mkdir -p reports

python -m pytest -v -rs \
  --screenshot only-on-failure \
  --tracing retain-on-failure \
  --html=reports/report.html \
  --self-contained-html
```

- `-v`：逐項列出測試結果；`-rs`：顯示略過原因。
- `--html=reports/report.html --self-contained-html`：產生單一 HTML 報告。
- `--screenshot only-on-failure`：測試失敗時保留截圖；`--tracing retain-on-failure`：只保留失敗測試的 Trace。
- 這些是**執行參數**，沒有增加測試案例，也不代表已設定 GitHub Actions 或 CI。

測試完成後，用 macOS 開啟報告：

```bash
open reports/report.html
```

正常快速執行而不產出 HTML／失敗證據，也可以使用 `python -m pytest -v`。想看瀏覽器實際操作，可加上 `--headed`。只執行 Smoke Test 可用 `python -m pytest -v -m smoke`。

**報告成功產生不等於所有案例 Pass；請以該次 Terminal 的 `passed / skipped / failed` 結果為準。** 一般回歸不會自動收集 `tests/manual_*.py` 這類需授權的操作型測試。

## 5.1 模型 + AI 應用的獨立操作測試（2026-10-28 更新）

以下兩支 `manual_*.py` **不列入一般 46 項回歸**。兩項會依當下狀態執行：已下載未啟用時自動啟用；已啟用時，一般模式只驗證使用者端，只有明確授權停用的完整循環模式才會先停用再啟用。未下載時不會自動下載（除非 AI 應用另有專門下載授權；模型目前不自動下載）。

**唯讀預檢（不啟用、不停用）：**

```bash
python -m pytest \
  tests/manual_model_activation.py::test_model_activation_preflight \
  tests/manual_ai_application_activation.py::test_ai_app_preflight \
  -v -s --headed
```

**一般啟用與使用者端驗證（不主動停用）：**

```bash
MODEL_TEST_WRITE=I_UNDERSTAND \
AI_APP_TEST_WRITE=I_UNDERSTAND \
python -m pytest \
  tests/manual_model_activation.py::test_model_activation_and_chat \
  tests/manual_ai_application_activation.py::test_ai_app_activation \
  -v -s --headed --slowmo 300 \
  --screenshot only-on-failure --tracing retain-on-failure -x
```

**完整循環（會中斷已啟用服務，須先確認測試環境允許）：**

```bash
MODEL_TEST_WRITE=I_UNDERSTAND \
MODEL_TEST_ALLOW_DISABLE=YES \
AI_APP_TEST_WRITE=I_UNDERSTAND \
AI_APP_TEST_ALLOW_DISABLE=YES \
python -m pytest \
  tests/manual_model_activation.py::test_model_activation_and_chat \
  tests/manual_ai_application_activation.py::test_ai_app_activation \
  -v -s --headed --slowmo 300 \
  --screenshot only-on-failure --tracing retain-on-failure -x
```

### 操作型測試結果（最新與歷史分開；不加入 46 項回歸）

| 日期／模式 | 模型 | AFS MyAgent | 當次 pytest 統計 |
|---|---|---|---|
| **2026-10-29 11:45 同批次驗證** | 最終 enabled；Chat 模型可選與輸入，未送訊息；所附截圖未完整呈現起始路徑 | downloaded_disabled → 啟用（約 29.9 秒）→ 開始使用，未送訊息；未執行先停用 | **2 passed**；前驗 40／6、後驗 41／5，整體 PASS；重試第二次點擊尚未確認 |
| **2026-10-28 15:39 歷史統一完整驗證** | 停用 → 重新啟用 → Chat UI 驗證 PASS（最長等待 100 秒） | 停用 → 重新啟用 →「開始使用」PASS | **`2 passed in 155.52s`**；同批次前／後一般回歸均 PASS |
| 2026-10-28 一般啟用 | 已啟用 → Chat 驗證 PASS | 已下載未啟用 → 啟用 → 開始使用 PASS（約 26.2 秒啟用） | `2 passed in 36.57s` |
| 2026-10-28 **先前成功的完整循環** | 停用 → 重新啟用 → Chat PASS | 停用 → 重新啟用（約 26.1 秒）→ 開始使用 PASS | `2 passed in 139.70s` |
| 2026-10-28 15:06 完整驗證（歷史失敗） | 模型恢復 `enabled`，但 Chat 首頁驗證在登入導向／白畫面時 FAIL | 停用 → 重新啟用 →「開始使用」PASS | `1 failed, 1 passed in 139.87s`（操作型階段）；當輪後驗回歸仍 PASS、整體 FAIL |
| 2026-10-28 前一輪完整循環（歷史） | 停用 → 重新啟用 → Chat PASS | 停用後重新啟用逾時，最後為 `downloaded_disabled`，FAILED | `1 passed, 1 failed in 406.08s` |

前一輪失敗時，AFS MyAgent 的「啟用」選項已被點擊，也觀察到 `enabling` 與部署提示；約 2.1 秒後回到 `downloaded_disabled`，直到 300 秒上限仍未達 `enabled`。**當時程式在等待期間沒有重複點擊啟用。** 若未來再度發生類似逾時，應先唯讀確認狀態並檢查部署日誌，不要直接重跑整個停用循環。2026-10-21 曾有成功的完整啟停紀錄（34.87 秒），此歷史紀錄同樣保留。

**歷史進度補充：** 上述 AI 應用啟用逾時後，曾另一次取得 `2 passed in 139.70s`。AFS MyAgent 重新啟用約 26.1 秒後 `enabled`，並成功點「開始使用」。**10/28 當時的同批次完整驗證為 `2 passed in 155.52s`，前後兩輪一般回歸均 PASS；最新 10/29 啟用與回歸結果見上表。** 目前沒有提供實機自動重試觸發紀錄，因此仍只能標記完整循環 PASS、重試分支尚待實機驗證。後端偶發回退原因仍待查，不能因新 PASS 就刪除歷史 FAILED。

### 目前的單次重試與等待提示

| 對象 | 開關 | 首輪持續未啟用時 | 第二次點擊前 | 等待上限 |
|---|---|---|---|---|
| 模型 | `MODEL_TEST_ALLOW_RETRY=YES` | 連續 `downloaded_disabled` 20 秒後記錄異常 | 另外連續確認 10 秒；再核對寫入授權、模型狀態及其他運作中模型 | 每輪最多 600 秒；連續未啟用可提前結束 |
| AI 應用 | `AI_APP_TEST_ALLOW_RETRY=YES` | 連續 `downloaded_disabled` 30 秒後記錄異常，不要求一定捕捉到短暫 `enabling` | 另外連續確認 10 秒；Page Object 點擊前再次核對寫入授權與狀態 | 每輪最多 300 秒；快速重試模式下第二輪同樣適用 30 秒未啟用判定 |

- 最多只重試一次，**不是固定點兩次**。第一次成功就繼續使用者端驗證；仍在 `enabling` 時不再次點擊。確認期間若已成功則直接繼續；若轉為其他處理中或不允許狀態，就停止本次重試。
- 等待過程每約 **10 秒**印出目前狀態及等待進度；上限不是固定睡滿的時間，觀察到成功即返回。
- 模型紀錄保存在 `reports/model_activation/enable_attempts.log`，事件包含 `attempt_1_fallback`／`attempt_1_timeout`、`attempt_2_clicked` 與第二次結果。
- AI 應用紀錄保存在 `reports/ai_application_activation/enable_attempts.log`，新版持續未啟用事件為 `attempt_1_disabled_30s`；真正等滿 300 秒才是 `attempt_1_timeout_300s`。舊的 `attempt_1_enabling_reverted_30s` 屬歷史版本命名，不應再當成新版唯一搜尋條件。
- 首次異常保留在 Terminal／日誌，第二次成功不會抹除。這兩個事件日誌採追加方式，判讀時須對照本輪時間與 `manual_activation.log`，不能把舊事件算入本輪。
- 兩個重試開關預設關閉。舊 `AI_APP_TEST_RETRY_ON_TIMEOUT=YES` 仍只允許等滿 300 秒後重試一次；它不會啟用 30 秒的快速判定。寫入、停用、下載授權仍各自獨立。
- 開發環境以模擬時間執行 **20 個離線情境通過**，涵蓋首輪成功、回退後第二次成功／失敗、未開啟重試、仍在啟用中、未知狀態、確認期間狀態變更及事件落盤。這是本次程式修正的離線證據，**不是 Mac 的 `verify_flow_offline.py` 新增 20 項，也不加入 46 項實機統計**。

### 本輪報告與展示

本輪證據目錄：`reports/validation_runs/20261029T034521_440063Z_8770/`。每次執行都會新增批次；根目錄的摘要代表最近一次執行，交付時應使用對應批次的摘要與報告。

| 報告 | 用途 |
|---|---|
| `validation_summary.md` | 同批次各階段結果與分階段 Skip 原因 |
| `regression_before.html` | 操作前一般回歸；本輪 40 passed／6 skipped |
| `manual_activation.html` | 模型與 AI 應用兩項操作型測試；細節依實際起始狀態與日誌判讀 |
| `regression_after.html` | 操作後一般回歸；本輪 41 passed／5 skipped |
| `reports/report.html` | 另行使用直接 pytest 指令產生的單輪報告，不會自動合併上述三個階段 |

若直接開啟 HTML 顯示不完整，在專案根目錄開另一個 iTerm 分頁：

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory reports
```

瀏覽器開啟 `http://localhost:8000/validation_runs/`，選擇對應批次。結束展示後在伺服器分頁按 `Control+C`；這只關閉報告伺服器，不涉及 AI Hub 服務。

## 6. 查看失敗截圖與 Playwright Trace

發生失敗後，通常可在 `test-results/` 下找到測試結果資料夾及 `trace.zip`（實際檔名與位置依 pytest-playwright 版本和設定而異）。先找檔案：

```bash
find test-results -type f -name 'trace.zip'
find test-results -type f -name '*.png'
```

直接開啟第一個找到的 Trace（不必把範例文字當檔案路徑貼上）：

```bash
TRACE=$(find test-results -type f -name 'trace.zip' -print -quit)
if [ -n "$TRACE" ]; then
  python -m playwright show-trace "$TRACE"
else
  echo '找不到 trace.zip；請確認本次執行有啟用 --tracing retain-on-failure，且確實有失敗測試'
fi
```

在 Trace Viewer 依序看 **Actions → Before／After → Network → Console**，核對導航是否完成、所在網址、請求是否被取消或回應異常、前端 JavaScript 有無例外。不應只根據 Console 單一訊息就認定後端或登入故障。

若想在**沒有失敗**時確認 Trace Viewer 能開啟，可以單獨執行已知安全的測試，暫時改為 `--tracing on --screenshot on`：

```bash
python -m pytest \
  tests/test_platform_manager.py::test_platform_manager_is_loaded \
  -v --headed --tracing on --screenshot on
```

> ⚠️ `.auth/user.json`、`reports/`、`test-results/`、截圖及 Trace 可能包含帳號資料、Token、頁面資訊或內部網址。分享前先檢查與去識別化；請勿直接提交至公開儲存庫，並確認 `.gitignore` 已排除不該版本控管的檔案。

## 測試結果怎麼看

```text
PASSED   測試通過
FAILED   測試失敗
SKIPPED  因登入狀態、測試資料或其他前置條件而略過，不等於測試失敗
```

## 常見問題快速排查

- 多項依賴登入的測試從一開始連續 FAILED：優先確認 `.auth/user.json` 是否過期，必要時執行 `python scripts/save_login_state.py`，先跑單項登入 Smoke Test，再跑完整回歸。
- 第一次載入 `/platform-manager` 的 URL 驗證逾時，但後續測試正常：先查 Trace 的 Actions、Network、Console，再單獨重跑；不要立即調整 Locator 或加入固定 `sleep()`。
- Console 出現 `Keycloak ready, isLoggedIn: false` 或 `Parameter "key" is required and cannot be empty`：代表前端登入／初始化有可追查線索，**不是單憑這兩行就能確認根因**；詳見筆記的 2026-10-21 偶發錯誤紀錄。
- `chrome-error://chromewebdata/`：網站或網路連線失敗。
- 網址包含 `openid-connect/auth`：可能正在重新導向到登入流程；若無法返回管理頁，確認登入狀態並重新執行 `python scripts/save_login_state.py`。
- `strict mode violation`：Locator 同時符合兩個以上的元件，需要縮小範圍或使用精確比對。
- `expected to be visible`：元件沒有顯示；先確認目前頁面與網址是否正確，再檢查 Locator。
- `檔名.py:行號`：錯誤實際發生的位置，可在 VS Code 使用 `Command + P` 跳至該行。

完整的 pytest／Playwright 錯誤判讀方式請參考 [PLAYWRIGHT_NOTES.md](PLAYWRIGHT_NOTES.md)。

## 專案結構

```text
ai_hub-playwright-test/
├── pages/
│   ├── platform_manager_page.py
│   └── user_home_page.py
├── scripts/
│   ├── save_login_state.py
│   ├── run_validation.py       # 新增：固定驗證／報表入口
│   └── selfcheck_validation.py # 新增：執行器自身的離線檢查
├── tests/
│   ├── test_site_access.py
│   ├── test_platform_manager.py
│   ├── test_user_home.py
│   ├── manual_model_activation.py
│   └── manual_ai_application_activation.py
├── .auth/                   # 本機登入狀態，不提交 Git
├── reports/                 # HTML 測試報告等輸出
├── test-results/            # 測試附件／Trace（執行時產生）
├── .env.example
├── pytest.ini
├── requirements.txt
├── TEST_CASES.md
├── PLAYWRIGHT_NOTES.md
└── README.md
```


## Gherkin 登入與登出

從專案根目錄執行。先啟用專案的 Python 虛擬環境，並在本機 `.env` 設定 `BASE_URL`、`TEST_USERNAME`、`TEST_PASSWORD`。測試帳號需能進入平台管理頁。

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m pytest tests/bdd/auth_steps.py -v -s
```

`tests/bdd/auth.feature` 描述使用者情境。`pytest-bdd` 依序執行 `auth_steps.py` 對應的步驟，Playwright 會開啟可見的 Chromium，登入、登出並以同一工作階段回訪管理頁。回訪時顯示登入表單才算通過。

情境使用獨立的瀏覽器工作階段，帳密取自本機 `.env`，執行過程不寫入登入狀態檔。此情境由上述指令單獨執行，原本的 46 項回歸仍由既有指令執行。

## Gherkin 完整驗證

在專案根目錄啟用 `.venv`，確認本機 `.env` 已設定測試網址與測試帳密，再執行：

```bash
source .venv/bin/activate

PYTEST_ADDOPTS="" \
MODEL_TEST_WRITE=I_UNDERSTAND \
MODEL_TEST_ALLOW_RETRY=YES \
AI_APP_TEST_WRITE=I_UNDERSTAND \
AI_APP_TEST_ALLOW_RETRY=YES \
python scripts/run_validation.py --auto-login --manual-activation --chat-send --gherkin
```

順序為自動登入一次、46 項 Gherkin 前回歸、模型啟用與對話、MyAgent 啟用與入口、46 項 Gherkin 後回歸，最後用原登入視窗登出並回訪管理頁。前後回歸在背景執行。操作情境會顯示瀏覽器並即時列印步驟。整輪結果看 iTerm 的 `[overall]`，詳細結果見 `reports/validation_summary.md`。

模型和 MyAgent 已啟用時會直接驗證使用流程。已下載但未啟用時會先啟用，符合條件時最多重試一次。模型情境會建立一則測試對話。

| 單跑項目 | 在專案根目錄執行 |
|---|---|
| 登入與登出 | `python -m pytest tests/bdd/auth_steps.py -s --gherkin-terminal-reporter -vv` |
| 模型與對話 | `MODEL_TEST_WRITE=I_UNDERSTAND MODEL_TEST_ALLOW_RETRY=YES MODEL_TEST_CHAT_SEND=YES python -m pytest tests/bdd/model_chat_steps.py -s --gherkin-terminal-reporter -vv` |
| MyAgent | `AI_APP_TEST_WRITE=I_UNDERSTAND AI_APP_TEST_ALLOW_RETRY=YES python -m pytest tests/bdd/ai_app_steps.py -s --gherkin-terminal-reporter -vv` |
| Gherkin 回歸 | `python -m pytest tests/bdd/*_regression_steps.py --gherkin-terminal-reporter -vv`（沿用本機有效的 `.auth/user.json`） |

詳細案例對照與實測進度見 [TEST_CASES.md](TEST_CASES.md)。
