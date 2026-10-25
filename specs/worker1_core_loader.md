# Worker 1 規格單：Core Data Loader & Adaptor 模組
目標檔案：`data_loader.py`
權責範圍：資料讀取、轉接、快取與欄位預處理

## 需求說明
1. 建立 `data_loader.py` 模組，支援讀取 `titan_core_chip` 產生的 CSV 報告與 Markdown 摘要：
   - 預設優先從 `data/latest.csv` 讀取，若不存在則嘗試從 `data/*.csv` 尋找最新日期的 CSV。
   - 若本地環境中存在 `/home/wuminchin/TitanCore/titan_core_chip/reports/`，亦可作為自動備援搜尋路徑。
   - 讀取 Markdown 摘要（例如 `data/latest.md` 或 reports 目錄下的 `latest.md`）。
2. 資料清洗與型別處理：
   - 將數值欄位轉為 float/int，缺失值以適當預設值處理（不要崩潰）。
   - 解析日期 `date`、`inst_date`、`margin_date`。
   - 計算/整理衍生標籤：
     - `is_resonance_bull`: 雙共振多頭 (`resonance == 'RESONANCE_BULL'` 或 `resonance_label` 包含多頭/💎)
     - `is_resonance_bear`: 雙共振空頭 (`resonance == 'RESONANCE_BEAR'` 或 `resonance_label` 包含空頭/💀)
     - 投信連買狀態 (`trust_streak`)、外資買賣超張數 (`foreign_net_lots`)、券資比 (`short_margin_ratio`)
3. 提供快取介面：
   - 函式 `load_chip_data(csv_path=None)` 返回 `(df, metadata)`，支援 `@st.cache_data(ttl=300)`。
   - 函式 `load_latest_summary_md()` 返回最新 Markdown 文本。
   - 函式 `get_available_dates()` 返回可用歷史報告日期清單。

## 驗收標準
- `python3 -c "import data_loader; print(data_loader)"` 無語法錯誤。
- 單元測試或讀取測試能成功解析 `/home/wuminchin/TitanCore/titan_core_chip/reports/2026-10-19.csv` 且正確提取欄位。
