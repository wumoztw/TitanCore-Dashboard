# Spec: 解決 Streamlit 模組熱重載快取不一致與自適應指標穩定性

## 問題分析 (Root Cause)
1. **熱重載快取問題 (AttributeError)**:
   - Streamlit 運行時，若修改自訂模組（如 `components.py`），Streamlit 的 module watcher 有時只重新執行 `app.py`，而 `components` 模組留在 `sys.modules` 的舊記憶體中，導致 `app.py` 呼叫 `components.render_kpi_cards` 時噴出 `AttributeError: module 'components' has no attribute 'render_kpi_cards'`。
   - 同時，即便函式不存在，程式應該要有安全降級（fallback）處理，例如 `getattr(components, "render_kpi_cards", None)`，以確保即使遇上模組快取不同步也不會 crash。
2. **側邊欄選擇器與最新日期問題**:
   - 截圖中顯示依然停留在 `資料日：2026-10-22（歷史紀錄）`，這是因為使用者的瀏覽器 Session State 還保留著上次選取的歷史日期，或者下拉選單因快取尚未更新預設值。
   - 需要確保：若使用者沒有刻意切換或需要查看最新盤後時，側邊欄預設第一項明確為最新，並且安全地與快取同步。

## 具體規格要求 (Detailed Requirements)
1. **components.py**:
   - 確保 `render_kpi_cards(kpis: dict) -> str` 穩定定義，並加上防護避免輸入為 None。
   - 提供 `__all__` 明確匯出：`["render_kpi_cards", "render_kpi_metrics", "render_report_table_as_cards", ...]`。

2. **app.py**:
   - 解決 Streamlit 熱重載未重載 submodules 的問題：
     - 在 `app.py` 開頭加入安全重載檢查：
       ```python
       import importlib
       import components
       import data_loader
       importlib.reload(components)
       importlib.reload(data_loader)
       ```
       這樣可以確保 Streamlit 伺服器在 `app.py` 觸發執行時，`components` 與 `data_loader` 一定會重新載入最新的記憶體版本，徹底消滅 `AttributeError: module 'components' has no attribute '...'` 的熱重載不同步問題！
     - 另外加入安全呼叫防護：
       ```python
       if hasattr(components, "render_kpi_cards"):
           st.markdown(components.render_kpi_cards(kpis), unsafe_allow_html=True)
       else:
           c1, c2, c3, c4 = st.columns(4)
           c1.metric("今日掃描", kpis["scanned"])
           c2.metric("💎 多頭雙共振", kpis["bull"])
           c3.metric("💀 空頭雙共振", kpis["bear"])
           c4.metric("投信積極買超", kpis["trust_active"])
       ```
     - 確保日期選單：若 session 中沒有選擇或選擇的值不在 dates 清單內，預設選取清單第一項（最新）。

3. **測試與驗證**:
   - 執行 `pytest` 確保所有測試 100% 通過。

4. **Git 與上傳 (Push)**:
   - 測試確認無誤後，git add 並 commit（遵照 Conventional Commits，如 `fix(hot-reload): reload submodules and add fallback for render_kpi_cards`）。
   - 執行 `git push origin main` 將程式碼推送到遠端倉庫。
   - 確保工作區乾淨。
