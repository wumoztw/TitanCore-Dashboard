# 一目均衡表訊號儀表板

📊 **TitanCore Dashboard** — Ichimoku Kinko Hyo Multi-Timeframe Signal Analysis

> 即時顯示加密貨幣與外匯的一目均衡表分析結果，支援日線 + 4H 多週期共振判斷與 AI 操作建議。

---

## 功能

- **多市場支援**：加密貨幣（OKX + Bybit）與外匯（Forex）同步分析
- **多週期共振**：日線（1D）＋ 4小時線（4H）雙週期綜合判斷
- **AI 分析建議**：由 Groq / LLaMA 4 生成進場、停損、目標價建議
- **篩選功能**：按來源、建議方向、有無訊號、有無 AI 建議篩選
- **自動更新**：每 4 小時由 TitanCore 後端自動執行分析並更新資料
- **TradingView 連結**：每個標的直接連結至對應 K 線圖（依交易所自動切換 OKX / Bybit / FX_IDC）

---

## 訊號類型

| 訊號 | 說明 | 方向 |
|------|------|------|
| 三役好轉 | 轉換線>基準線 + 價格>26日前 + 價格>雲層 | 🟢 強力做多 |
| 三役逆轉 | 轉換線<基準線 + 價格<26日前 + 價格<雲層 | 🔴 強力做空 |
| 黃金交叉 | 轉換線向上突破基準線 | 📈 做多 |
| 死亡交叉 | 轉換線向下跌破基準線 | 📉 做空 |
| 突破雲層 | 價格向上突破雲層上緣 | 📈 做多 |
| 跌破雲層 | 價格向下跌破雲層下緣 | 📉 做空 |
| 雲層阻力回落 | 價格觸雲層後反彈向下 | 📉 做空 |
| 遲行線逆轉 | 遲行線跌破 26 日前價格 | 📉 做空 |

---

## 架構

```
TitanCore 後端（分析引擎 + Groq AI）
    ↓ 每 4 小時寫入
data/analysis_results.json
    ↓ load_data()（快取 5 分鐘）
Streamlit Dashboard (app.py)
    ↓ HTTP
使用者瀏覽器
```

本 repo 為純展示層，不執行任何 Ichimoku 計算，資料由 TitanCore 主體產生。

---

## 本地執行

```bash
pip install streamlit pandas pytz
streamlit run app.py
```

---

## 更新紀錄

### v4.0 — 2026-05-23 · 雙策略整合 (IKH & EMA/BB)

- **雙策略切換**：在側邊欄最上方新增「策略模式」選擇器，可自由切換展示「一目均衡表 (IKH)」或「三均線 + 布林通道 (EMA/BB)」策略。
- **資料自動載入與映射**：支援動態載入 `titan_core_ema_results.json` 檔案。並在載入時，將 EMA 特徵映射為 Dashboard 原生之綜合建議格式，使舊有篩選條件完美向下相容。
- **EMA 專屬總覽表格**：切換為 EMA 策略後，總覽表格自動展示日線排列、4H排列與 4H布林帶寬 %B 等策略關鍵數值。
- **EMA 專屬卡片與 Modal 詳情**：新設計 EMA-BB 卡片 HTML。支援動態呈現均線（EMA 21/55/144）數值、布林通道上下軌、寬度與 Squeeze 蓄能 / Expanding 擴張等即時狀態。

### v3.0 — 2026-05-09 · 響應式重構 & 跨瀏覽器相容

- **全面響應式**：支援桌面（5 欄）、平板（3 欄）、手機（2 欄）Metrics 自動切換

- **手機卡片優化**：日線/4H 區域 ≤480px 自動堆疊為單欄，數據項目全寬顯示
- **iOS Safari 修正**：`dvh` 單位、`safe-area-inset` 安全區、`-webkit-overflow-scrolling: touch`
- **Firefox 相容**：`background-clip: text` 搭配 `color` fallback
- **CSS Custom Properties**：統一色彩系統（`--tc-accent`、`--tc-glass`等），便於維護
- **交易所 Badge**：卡片標頭顯示 OKX / Bybit 交易所標識
- **觸控優化**：Modal 關閉鈕放大至 40px、sig-pill 增加 padding
- **Hero 省電**：手機禁用旋轉光環動畫、縮減 padding 和字體
- **Footer 版本號**：顯示 `TitanCore Dashboard v3.0`

### v2.1 — 2026-05-09 · 多交易所 TradingView 連結修正

- **修正 VVV (Venice Token) TradingView 連結**：`get_chart_url()` 新增 `exchange` 參數，根據標的所屬交易所自動切換 TradingView 前綴
  - Bybit 標的 → `BYBIT:VVVUSDT`（修正前誤用 `OKX:VVVUSDT` 導致連結失效）
  - OKX 標的 → `OKX:BTCUSDT`（不變）
  - 外匯標的 → `FX_IDC:EURUSD`（不變）
- **向下相容**：舊版 JSON 資料（無 `exchange` 欄位）預設走 OKX 路徑

### v2.0 — 2026-04-15 · UI 全面美化

- **設計語言**：深藍漸層背景、Inter 字型、毛玻璃 Sidebar
- **Hero 標頭**：旋轉光環 CSS 動畫、等寬字體更新時間膠囊
- **指標卡**：五色頂部光條（藍/青/綠/紅/紫）+ hover 浮起動畫
- **分析卡**：改用 `st.components.v1.html()` 渲染，修復巢狀 HTML 顯示問題
  - 做多 → 深綠標頭、做空 → 深紅標頭、觀望 → 深藍標頭
  - 訊號 Pill 標籤色標（多頭綠、空頭紅）
  - 趨勢徽章（強勢上升/下降/盤整/不明確各色）
- **AI 建議**：紫色漸層框 + 閃爍頂部光條動畫
- **效能**：加入 `@st.cache_data(ttl=300)` 快取資料讀取
- **Bug 修正**：Forex TradingView URL 從 `FX:` 修正為 `FX_IDC:`

### v1.0 — 初始版本

- 基礎 Streamlit 儀表板
- 日線 + 4H 雙週期分析展示
- AI 建議區塊（Groq / LLaMA）
- 篩選功能與摘要統計

---

## 免責聲明

⚠️ 本系統僅提供技術分析參考，不構成投資建議。AI 建議由第三方模型生成，僅供參考。交易有風險，請謹慎評估自身風險承受能力。
