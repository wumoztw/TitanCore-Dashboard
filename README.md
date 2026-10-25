# TitanCore 台股籌碼與技術共振儀表板

Streamlit 展示層，讀取 `titan_core_chip` 產出的盤後 CSV / Markdown，呈現雙共振（技術面 EMA＋一目 × 籌碼訊號）與全市場清單。本專案不自行抓取交易所資料，也不構成投資建議。

## 啟動

```bash
pip install -r requirements.txt
./sync_chip_report.sh
streamlit run app.py
```

`sync_chip_report.sh` 會把 `/home/wuminchin/TitanCore/titan_core_chip/reports/` 最新日期 CSV 與 `latest.md` 軟連結到 `data/latest.csv`、`data/latest.md`。也可設定 `CHIP_REPORTS_DIR`。

若未同步，儀表板會直接回退讀取 TitanCore 報告目錄中最新的 `YYYY-MM-DD.csv`。

## 畫面

- 側邊欄：日期、共振標籤、籌碼分類、技術狀態、排序、台股紅漲綠跌 / 國際配色
- KPI：掃描家數、多頭雙共振、空頭雙共振、投信買超家數
- 分頁：雙共振焦點、全市場卡片或表格、盤後 Markdown

## 測試

```bash
python3 -m unittest discover tests
```
