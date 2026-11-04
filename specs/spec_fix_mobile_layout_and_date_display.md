# Spec: 優化手機版資訊卡片排列與來源路徑顯示

## 目標 (Goal)
1. **來源路徑與日期顯示**：
   - 目前副標題顯示：`資料日 2026-10-22 · 來源 /mount/src/titancore-dashboard/data/2026-10-22.csv`
   - 對使用者而言，顯示 server 內部容器絕對路徑（`/mount/src/...`）既冗長又不美觀，且在手機版會造成醜陋的折行。
   - 將副標題精簡為：
     - 若為最新資料：`資料日：YYYY-MM-DD（最新盤後）`（或 `資料日：2026-11-03 · 檔案：latest.csv`，不再顯示內部絕對路徑，只顯示檔名或乾淨標籤）。
     - 若為歷史日期：`資料日：YYYY-MM-DD`。
   - 確保 Streamlit 伺服器快取過期或重新整理後，正確顯示最新日期（例如 2026-11-03）。
2. **手機版頂部 KPI 數據資訊排版異常修復**：
   - 目前頂部的 4 個 KPI 數據（今日掃描、多頭雙共振、空頭雙共振、投信積極買超）使用 `st.columns(4)` + `st.metric()`。在手機螢幕（直式窄螢幕）下，Streamlit 會自動將欄位強制垂直堆疊成一長串（每行一個，且佔據整面螢幕高度），非常突兀且排版鬆散。
   - 需求：改寫頂部 KPI 指標排版，以現代化的 2x2 CSS Grid（手機直螢幕）或自適應 4 欄（平板與桌機寬螢幕）展示。
   - 設計一組精美的 KPI 數據卡片（例如 `.tc-kpi-grid`），在寬螢幕為 4 欄橫排（1fr 1fr 1fr 1fr），在手機窄螢幕（max-width: 640px）自動轉為 2x2（1fr 1fr）網格，確保 4 個指標在手機上一眼即可完整瀏覽，不會直向拉伸 4 大行。

## 工作目錄
`/home/wuminchin/文件/TitanCore-Dashboard`

## 具體規格要求 (Detailed Requirements)
1. **components.py**:
   - 在 `DASHBOARD_CSS` 內新增 `.tc-kpi-grid` 與 `.tc-kpi-card` 樣式：
     - `.tc-kpi-grid`：`display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;`
     - `@media (max-width: 640px)`：`.tc-kpi-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }`
     - `.tc-kpi-card`：採用既有 glassmorphism 風格（`background: var(--tc-glass); border: 1px solid var(--tc-line); border-radius: 12px; padding: 12px 14px; text-align: center;`），並呈現乾淨的 label（小字體、次要文字顏色）與 value（大字體、加粗、數字等寬 font-variant-numeric: tabular-nums）。
   - 新增函式 `render_kpi_cards(kpis: dict) -> str`：
     - 傳入 `kpis` 字典（含有 `scanned`, `bull`, `bear`, `trust_active`）。
     - 回傳渲染後的 HTML 字串。
   - 保持既有函式相容性。

2. **app.py**:
   - 替換原有的 `st.caption(f"資料日 {meta['as_of']} · 來源 {src}")`：
     - 只取檔名 `Path(src).name`，不顯示伺服器內部絕對路徑；
     - 若 `src` 為 `latest.csv`，顯示：`資料日：{meta['as_of']}（最新盤後雷達）`；
     - 若為指定日期，顯示：`資料日：{meta['as_of']}（歷史紀錄）`。
   - 替換原有的 `c1, c2, c3, c4 = st.columns(4)` + `metric`：
     - 改用 `components.render_kpi_cards(kpis)` 透過 `st.markdown(..., unsafe_allow_html=True)` 輸出自適應 KPI 卡片。

3. **測試與驗證 (tests/test_chip_dashboard.py)**:
   - 針對新增的 `components.render_kpi_cards` 撰寫測試，驗證 4 個指標數值皆正確渲染在 HTML 輸出中。
   - 執行 `pytest` 確保 100% 通過。

4. **Git 與上傳 (Push)**:
   - 測試確認無誤後，git add 相關檔案並 commit（遵照 Conventional Commits，如 `feat: optimize mobile kpi grid layout and sanitize data source caption`）。
   - 執行 `git push origin main` 將程式碼推送到遠端倉庫。
   - 確保工作區乾淨。
