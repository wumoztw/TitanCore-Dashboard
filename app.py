"""Taiwan chip + technical resonance dashboard."""

from __future__ import annotations

import importlib
from pathlib import Path

import streamlit as st

import components
import data_loader

# Streamlit may re-run app.py without reloading submodules; force fresh versions.
importlib.reload(components)
importlib.reload(data_loader)

st.set_page_config(page_title="台股籌碼雷達盤後報告", page_icon="💎", layout="wide")

st.markdown(
    '<div class="tc-head" style="margin-bottom:12px">'
    '<div>'
    '<div class="tc-symbol" style="font-size:1.65rem">台股籌碼雷達盤後報告</div>'
    '<div class="tc-muted">公開籌碼 × EMA / 一目均衡表雙共振 · 不構成投資建議</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

dates = data_loader.get_available_dates()
with st.sidebar:
    st.header("設定")
    if st.session_state.get("report_date") not in dates:
        st.session_state.pop("report_date", None)
    selected_date = st.selectbox(
        "報告日期", dates or ["（無歷史 CSV）"], key="report_date", disabled=not dates)
    palette = st.toggle("國際配色（綠漲紅跌）", value=False)
    st.caption("資料來自 titan_core_chip 盤後雷達，快取 5 分鐘。")

st.markdown(components.apply_palette("intl" if palette else "tw"), unsafe_allow_html=True)

df, meta = data_loader.load_chip_data(as_of=selected_date if dates else None)
if meta.get("as_of"):
    src_name = Path(meta.get("source", "")).name
    tag = "最新盤後雷達" if src_name == "latest.csv" else "歷史紀錄"
    st.caption(f"資料日：{meta['as_of']}（{tag}）")

kpis = components.render_kpi_metrics(df)
if hasattr(components, "render_kpi_cards"):
    st.markdown(components.render_kpi_cards(kpis), unsafe_allow_html=True)
else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("今日掃描", kpis["scanned"])
    c2.metric("💎 多頭雙共振", kpis["bull"])
    c3.metric("💀 空頭雙共振", kpis["bear"])
    c4.metric("投信積極買超", kpis["trust_active"])

st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:16px 0 20px 0;'>", unsafe_allow_html=True)

md_content = data_loader.load_latest_summary_md()
if not md_content or not md_content.strip():
    st.info("目前沒有盤後 Markdown 報告。")
else:
    lines = md_content.splitlines()
    i = 0
    current_text = []
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('|') and i + 1 < len(lines) and '---' in lines[i + 1]:
            if current_text:
                st.markdown("\n".join(current_text))
                current_text = []
            table_lines = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            cards_html = components.render_report_table_as_cards(table_lines)
            if cards_html:
                st.markdown(cards_html, unsafe_allow_html=True)
        else:
            current_text.append(lines[i])
            i += 1
    if current_text:
        st.markdown("\n".join(current_text))
