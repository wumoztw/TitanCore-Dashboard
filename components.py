"""Streamlit card/CSS helpers for the Taiwan chip + resonance dashboard."""

from __future__ import annotations

import html
from urllib.parse import quote

DASHBOARD_CSS = """
<style>
:root {
  --tc-bg: #07080d;
  --tc-glass: rgba(18, 22, 34, 0.78);
  --tc-line: rgba(255,255,255,0.08);
  --tc-text: #e8edf7;
  --tc-muted: #93a0b8;
  --tc-bull: #ef4444;
  --tc-bear: #10b981;
  --tc-gold: #f5c16c;
}
html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 600px at 10% -10%, #1a1430 0%, var(--tc-bg) 45%);
  color: var(--tc-text);
}
.tc-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  align-items: stretch;
  margin-top: 8px;
  margin-bottom: 24px;
}
.tc-cards-grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 16px;
  align-items: stretch;
  margin-top: 8px;
  margin-bottom: 24px;
}
.tc-card {
  background: var(--tc-glass);
  border: 1px solid var(--tc-line);
  border-radius: 16px;
  padding: 16px 18px 14px;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 30px rgba(0,0,0,.28);
}
.tc-card.bull { box-shadow: 0 0 0 1px rgba(239,68,68,.45), 0 0 24px rgba(239,68,68,.25); }
.tc-card.bear { box-shadow: 0 0 0 1px rgba(88,28,135,.7), 0 0 22px rgba(76,29,149,.35); }
.tc-head { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.tc-symbol { font-size: 1.15rem; font-weight: 700; letter-spacing: .02em; }
.tc-price { font-variant-numeric: tabular-nums; font-weight: 650; margin-top: 2px; }
.tc-up { color: var(--tc-bull); }
.tc-down { color: var(--tc-bear); }
.tc-muted { color: var(--tc-muted); font-size: .86rem; }
.tc-badge {
  display: inline-block; margin: 6px 6px 0 0; padding: 3px 8px; border-radius: 999px;
  font-size: .78rem; border: 1px solid var(--tc-line); background: rgba(255,255,255,.04);
}
.tc-badge.bull { color: #fff; background: linear-gradient(90deg, #b91c1c, #f59e0b); border: 0; }
.tc-badge.bear { color: #f5e9ff; background: #2e1064; border-color: #6d28d9; }
.tc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 14px; margin-top: 12px; }
.tc-note {
  margin-top: auto;
  padding-top: 12px;
  font-size: .88rem;
  line-height: 1.45;
  color: #d5dced;
  border-top: 1px solid rgba(255,255,255,0.05);
}
a.tc-link { color: #93c5fd; text-decoration: none; }
@media (max-width: 720px) {
  .tc-cards-grid, .tc-cards-grid-2 { grid-template-columns: 1fr; }
  .tc-grid { grid-template-columns: 1fr; }
}

[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--tc-glass);
  border: 1px solid var(--tc-line) !important;
  border-radius: 16px !important;
  padding: 8px 12px !important;
  margin-bottom: 16px !important;
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 30px rgba(0,0,0,.28);
}
.stMarkdown table {
  width: 100% !important;
  border-collapse: collapse !important;
  margin: 12px 0 !important;
  font-size: 0.88rem !important;
}
.stMarkdown th {
  background: rgba(255,255,255,0.06) !important;
  color: var(--tc-text) !important;
  font-weight: 600 !important;
  padding: 8px 10px !important;
  border: 1px solid var(--tc-line) !important;
}
.stMarkdown td {
  padding: 8px 10px !important;
  border: 1px solid var(--tc-line) !important;
  color: #d5dced !important;
}
.stMarkdown tr:hover td {
  background: rgba(255,255,255,0.03) !important;
}
</style>
"""


def tradingview_url(symbol: str) -> str:
    code = quote(str(symbol).strip(), safe="")
    return f"https://tw.tradingview.com/chart/?symbol=TWSE%3A{code}"


def yahoo_url(symbol: str) -> str:
    return f"https://tw.stock.yahoo.com/quote/{quote(str(symbol).strip(), safe='')}.TW"


def apply_palette(mode: str) -> str:
    """Taiwan default: up red / down green. International flips the pair."""
    if mode == "intl":
        return DASHBOARD_CSS.replace("--tc-bull: #ef4444;", "--tc-bull: #10b981;").replace(
            "--tc-bear: #10b981;", "--tc-bear: #ef4444;")
    return DASHBOARD_CSS


def _fmt_num(value, signed=False, digits=1, suffix="") -> str:
    if value is None:
        return "—"
    try:
        if value != value:  # NaN
            return "—"
        number = float(value)
    except (TypeError, ValueError):
        return "—"
    text = f"{number:+,.{digits}f}" if signed else f"{number:,.{digits}f}"
    return text + suffix


def _get(row, key, default=""):
    if hasattr(row, "get"):
        value = row.get(key, default)
    else:
        value = getattr(row, key, default)
    return default if value is None else value


def _truthy_flag(row, key) -> bool:
    value = _get(row, key, False)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return bool(value)


def render_chip_card(row, modal_view: bool = False) -> str:
    symbol = html.escape(str(_get(row, "symbol", "")))
    name = html.escape(str(_get(row, "name", "")))
    close = _fmt_num(_get(row, "close", None), digits=2)
    change = _get(row, "change_pct", None)
    change_html = ""
    if change == change and change not in ("", None):
        try:
            number = float(change)
            klass = "tc-up" if number > 0 else "tc-down" if number < 0 else "tc-muted"
            change_html = f'<div class="{klass}">{number:+.2f}%</div>'
        except (TypeError, ValueError):
            change_html = ""
    bull = _truthy_flag(row, "is_resonance_bull") or str(_get(row, "resonance", "")).upper() == "RESONANCE_BULL"
    bear = _truthy_flag(row, "is_resonance_bear") or str(_get(row, "resonance", "")).upper() == "RESONANCE_BEAR"
    klass = "bull" if bull else "bear" if bear else ""
    if bull:
        badge = '<span class="tc-badge bull">💎 雙共振多頭</span>'
    elif bear:
        badge = '<span class="tc-badge bear">💀 雙共振空頭</span>'
    else:
        cat = html.escape(str(_get(row, "chip_category") or _get(row, "category") or "NEUTRAL"))
        badge = f'<span class="tc-badge">{cat}</span>'
    note = _esc(_get(row, "summary_note", ""))
    tv = tradingview_url(str(_get(row, "symbol", "")))
    yh = yahoo_url(str(_get(row, "symbol", "")))
    extra = ""
    if modal_view:
        extra = f'<div class="tc-muted">訊號 {_esc(_get(row, "signals", ""))} · 資料日 {_esc(_get(row, "date", ""))}</div>'
    card_html = (
        f'<article class="tc-card {klass}">'
        f'<div class="tc-head">'
        f'<div>'
        f'<div class="tc-symbol">{symbol} {name}</div>'
        f'<div class="tc-price">{close}</div>'
        f'{change_html}'
        f'{badge}'
        f'</div>'
        f'<div class="tc-muted">'
        f'<a class="tc-link" href="{tv}" target="_blank" rel="noopener">TradingView</a><br>'
        f'<a class="tc-link" href="{yh}" target="_blank" rel="noopener">Yahoo</a>'
        f'</div>'
        f'</div>'
        f'<div class="tc-grid">'
        f'<div><div class="tc-muted">技術面</div>'
        f'EMA {_esc(_get(row, "ema_trend", "—"))} · 一目 {_esc(_get(row, "ichimoku_trend", "—"))}<br>'
        f'ADX {_fmt_num(_get(row, "adx", None), digits=1)} · 布林 {_esc(_get(row, "bollinger_signal", "—"))}<br>'
        f'建議 {_esc(_get(row, "tech_action", "—"))}'
        f'</div>'
        f'<div><div class="tc-muted">籌碼</div>'
        f'投信 {_fmt_num(_get(row, "trust_net_lots", None), signed=True)} 張 / 連{_fmt_num(_get(row, "trust_streak", None), digits=0)} / 5日 {_fmt_num(_get(row, "trust_5d_lots", None), signed=True)}<br>'
        f'外資 {_fmt_num(_get(row, "foreign_net_lots", None), signed=True)} 張 / 連{_fmt_num(_get(row, "foreign_streak", None), digits=0)} / 5日 {_fmt_num(_get(row, "foreign_5d_lots", None), signed=True)}<br>'
        f'融資5日 {_fmt_num(_get(row, "margin_diff_5d", None), signed=True)} · 融券5日 {_fmt_num(_get(row, "short_diff_5d", None), signed=True)} · 券資比 {_fmt_num(_get(row, "short_margin_ratio", None), digits=2, suffix="%")}'
        f'</div>'
        f'</div>'
        f'<div class="tc-note">{note}</div>'
        f'{extra}'
        f'</article>'
    )
    return card_html


def _esc(value) -> str:
    if value is None or value != value or str(value).strip() == "":
        return "—"
    return html.escape(str(value))


def render_kpi_metrics(df) -> dict:
    rows = 0 if df is None else len(df)
    if rows == 0:
        return {"scanned": 0, "bull": 0, "bear": 0, "trust_active": 0}
    bull = int(df["is_resonance_bull"].sum()) if "is_resonance_bull" in df.columns else 0
    bear = int(df["is_resonance_bear"].sum()) if "is_resonance_bear" in df.columns else 0
    trust = df["trust_net_lots"] if "trust_net_lots" in df.columns else None
    trust_active = int((trust.fillna(0) > 0).sum()) if trust is not None else 0
    return {"scanned": int(rows), "bull": bull, "bear": bear, "trust_active": trust_active}


def render_cards_container(rows, grid_class: str = "tc-cards-grid") -> str:
    """Render a list of row dicts into a unified CSS Grid container."""
    cards_html = "".join(render_chip_card(r) for r in rows)
    return f'<div class="{grid_class}">{cards_html}</div>'
