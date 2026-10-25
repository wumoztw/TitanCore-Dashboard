# Worker 4 規格單：主入口整合、設定與文件更新
目標檔案：`app.py`, `README.md`, `sync_chip_report.sh`
權責範圍：Streamlit 主入口改造、排程同步腳本、文件更新

## 需求說明
1. 重構 `app.py`：
   - 整合 `data_loader.py` 與 `components.py`。
   - 版面佈局設計：
     - **標頭 Header**：TitanCore 台股籌碼與技術共振雷達。
     - **側邊欄 Sidebar**：
       - 日期選擇器（若有多日資料）。
       - 篩選條件：共振標籤（全部 / 💎多頭共振 / 💀空頭共振）、籌碼分類、技術狀態。
       - 排序方式：依成交量、投信買超、外資買超排序。
       - 配色模式開關（台股傳統紅漲綠跌 vs 國際綠漲紅跌）。
     - **頂部 KPI 統計看板**。
     - **三大主分頁 (Tabs)**：
       - Tab 1: 💎 雙共振焦點（將置頂雙共振標的以卡片大尺寸優先展示，無則提示今日無共振）。
       - Tab 2: 📊 全市場分析清單（支援卡片網格與 `st.dataframe` 互動表格檢視）。
       - Tab 3: 📝 最新 Markdown 盤後報告（完整渲染盤後摘要）。
2. 提供 `sync_chip_report.sh`：
   - 一鍵將 `/home/wuminchin/TitanCore/titan_core_chip/reports/` 內的最新 CSV 與 Markdown 同步或軟連結至本專案 `data/latest.csv` 與 `data/latest.md`。
3. 更新 `README.md`：
   - 更新專案標題為「TitanCore 台股籌碼與技術共振儀表板」。
   - 說明如何啟動 (`streamlit run app.py`) 以及與 `titan_core_chip` 串接方式。

## 驗收標準
- `python3 -m py_compile app.py` 檢查無語法錯誤。
- `README.md` 與 `sync_chip_report.sh` 就緒並有執行權限。
