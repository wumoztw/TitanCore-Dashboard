# Worker 2 規格單：UI Components & Cards 模組
目標檔案：`components.py`
權責範圍：HTML 模板、CSS 樣式、卡片生成與台股紅漲綠跌渲染

## 需求說明
1. 建立 `components.py`，負責 Streamlit 卡片與 UI 元件渲染：
   - 包含優化後的自訂深色金融儀表板 CSS（深黑背景、霓虹高亮、精緻玻璃擬態卡片）。
   - 支援台灣股市習慣配色（多頭鮮紅 #ef4444 / 空頭翠綠 #10b981，或於頂部設置切換開關）。
2. 卡片渲染器 `render_chip_card(row, modal_view=False)`：
   - **卡片頂部**：
     - 代碼與股票名稱（如 `2330 台積電`）、收盤價、漲跌幅（若有）。
     - 雙共振徽章：💎 雙共振多頭（金色/紅色強烈發光）、💀 雙共振空頭（紫色/暗黑風格）、一般籌碼分類徽章。
     - TradingView 連結：直接生成 `https://tw.tradingview.com/chart/?symbol=TWSE%3A{symbol}` 或 Yahoo 股市連結。
   - **技術面區塊**：
     - 顯示：EMA120/240 趨勢、一目均衡表趨勢、ADX 趨勢強度值、布林通道訊號、技術操作建議（做多進場/觀望/出場）。
   - **籌碼面核心區塊**：
     - 投信：今日買賣超張數、連買天數、5日累計。
     - 外資：今日買賣超張數、連買/賣天數、5日累計。
     - 融資券：5日融資變化、5日融券變化、券資比百分比。
   - **解讀摘要區**：
     - 顯示 `summary_note` 文字。
3. 頂部 KPI 卡片渲染器 `render_kpi_metrics(df)`：
   - 顯示：今日掃描家數、💎多頭雙共振數、💀空頭雙共振數、投信積極買超數。

## 驗收標準
- `python3 -c "import components; print(components)"` 語法正常。
- 產生的 HTML 結構乾淨、不崩壞，支援響應式排版。
