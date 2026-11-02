此自動化測試為 Python＋Playwright 自動化驗證流程，執行一條指令就會：

自動輸入帳密登入。 網址：https://202.5.254.27/platform-manager

執行 46 項一般回歸，確認管理頁與使用者介面正常。

依服務狀態執行模型、AI 應用啟停，驗證啟用後可使用。

送出一則模型對話，確認有回覆、建立歷史紀錄且能重新開啟。

再跑一次回歸，最後登出並確認管理頁重新要求登入。

最近完整實測 PASS，約 4 分 8 秒：前後回歸各 41 通過、5 略過，操作型測試 2 項通過。略過原因是環境缺少資料或功能未啟用。

一般回歸在背景執行；登入、啟停、對話與登出顯示瀏覽器，操作間隔設為 1 秒，方便 Demo，並產出摘要與 HTML 報告。

---
第一次執行，先安裝 Python 和設定環境：

cd ai_hub-playwright-test
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium

再建立 .env、填入設定，就能執行完整指令。帳號需要具備相應的模型與 AI 應用操作權限。
