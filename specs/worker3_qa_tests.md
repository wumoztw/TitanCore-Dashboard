# Worker 3 規格單：QA & 測試套件
目標檔案：`tests/test_chip_dashboard.py`
權責範圍：單元測試、資料完整性驗證與 mock 測試

## 需求說明
1. 建立 `tests/test_chip_dashboard.py`：
   - 測試 `data_loader.py` 的解析能力，使用 `tests/mock_chip.csv` 或真實 sample CSV 驗證。
   - 驗證欄位計算：包含 `is_resonance_bull`、`is_resonance_bear`、連買天數處理、NaN 處理。
   - 測試 `components.py` 的 HTML 生成，確保標的卡片輸出不為空，包含股票代碼與關鍵指標。
   - 測試 TradingView URL 產生邏輯。
2. 建立 `tests/mock_chip.csv`：
   - 包含多頭雙共振（如 2409 友達/聯發科等範例）、空頭雙共振、中立等各種邊界資料。
3. 執行測試：
   - 使用 `pytest` 或 `python3 -m unittest` 執行所有測試並確保 100% 通過。

## 驗收標準
- 執行 `pytest tests/` 或 `python3 -m unittest discover tests` 全數 PASS。
