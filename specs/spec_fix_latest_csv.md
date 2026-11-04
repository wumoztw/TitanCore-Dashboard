# Spec: Dashboard 支援載入最新資料 latest.csv 與歷史日期切換

## 目標 (Goal)
目前 `TitanCore-Dashboard` 顯示固定在 `2026-10-22`，原因是 `app.py` 與 `data_loader.py` 只辨識 `YYYY-MM-DD.csv`，側邊欄日期選單只抓到單一歷史檔，導致從未載入由 CI 自動更新的 `data/latest.csv`。
需要修改 `TitanCore-Dashboard`，讓預設載入最新的 `data/latest.csv`，且側邊欄選單支援「最新 (latest)」與歷史日期切換。

## 工作目錄
`/home/wuminchin/文件/TitanCore-Dashboard`

## 具體規格要求 (Detailed Requirements)
1. **data_loader.py**:
   - `get_available_dates()`:
     - 檢查是否存在 `latest.csv`。如果存在，從 `latest.csv` 中取得其最新日期（例如 `2026-11-03`），並在回傳清單中最前方提供選項 `"最新 (Latest)"`。
     - 後方接續所有歷史 CSV 日期（排序由新到舊），例如 `["最新 (Latest)", "2026-10-22", "2026-10-19"]`。
   - `resolve_csv_path(csv_path=None, as_of=None)`:
     - 當 `as_of is None` 或 `as_of == "最新 (Latest)"` 或 `as_of == "latest"` 時，優先解析為 `DATA_DIR / "latest.csv"`（若存在）。
     - 當 `as_of` 為指定具體日期（如 `"2026-10-22"`）時，解析為對應的歷史 CSV。
   - 確保 `load_chip_data(as_of=...)` 能正確解析並回傳對應的 DataFrame 與 metadata。

2. **app.py**:
   - 側邊欄選單預設選中第一筆（即 `"最新 (Latest)"`）。
   - 確保頁面副標題顯示實際資料日（`meta['as_of']`），當讀取 `latest.csv` 時顯示其實際日期（如 `2026-11-03`），不再寫死。

3. **測試與驗證 (tests/test_chip_dashboard.py)**:
   - 補充測試案例：
     - 驗證 `resolve_csv_path(as_of="最新 (Latest)")` 回傳 `latest.csv`。
     - 驗證 `get_available_dates()` 包含 `"最新 (Latest)"` 且置頂。
   - 執行 `pytest` 確保所有測試 100% 通過。

4. **Git 與上傳 (Push)**:
   - 測試確認無誤後，git add 相關檔案並 commit（遵照 Conventional Commits，如 `fix: default to latest.csv and add latest option to date selector`）。
   - 執行 `git push origin main` 將程式碼推送到遠端倉庫。
   - 確保工作區乾淨。
