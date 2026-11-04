# Spec: 清理工作區未追蹤檔案與規範管理

## 目標
將工作區的未追蹤檔案妥善歸類與處理：
1. `specs/spec_fix_hot_reload_and_sidebar_cache.md`：此為修復規格單，追蹤至 git，與先前的規格單保持一致。
2. `data/titan_core_ema_stats.json`：此為本機舊的統計快照或快取，如果不需要追蹤，可在 `.gitignore` 忽略 `data/*stats.json` 或直接納入管理/清理，使 `git status` 呈現乾淨狀態（working tree clean）。

## 步驟
1. 檢視 `data/titan_core_ema_stats.json`，若為歷史成果且其餘 json 如 `analysis_results.json` 均有追蹤，可直接追蹤或在 `.gitignore` 設定。在此建議將規格檔與此檔案加入追蹤，或者將未追蹤檔案納入 git 管理。
2. 執行 commit，格式：`chore: track hot-reload spec and cleanup untracked workspace files`。
3. push 到 origin main。
4. 驗證 `git status` 工作目錄乾淨。
