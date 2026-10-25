"""TitanCore Taiwan chip + technical resonance dashboard."""

from __future__ import annotations

import streamlit as st

import components
import data_loader

st.set_page_config(page_title="TitanCore 台股籌碼共振", page_icon="💎", layout="wide")

st.markdown(
    '<div class="tc-head" style="margin-bottom:8px">'
    '<div>'
    '<div class="tc-symbol" style="font-size:1.6rem">TitanCore 台股籌碼與技術共振雷達</div>'
    '<div class="tc-muted">公開籌碼 × EMA / 一目均衡表雙共振 · 不構成投資建議</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

dates = data_loader.get_available_dates()
with st.sidebar:
    st.header("篩選")
    selected_date = st.selectbox("報告日期", dates or ["（無歷史 CSV）"], disabled=not dates)
    resonance_filter = st.selectbox("共振標籤", ["全部", "💎多頭共振", "💀空頭共振"])
    frame_preview, _ = data_loader.load_chip_data(as_of=selected_date if dates else None)
    categories = ["全部"]
    if not frame_preview.empty and "chip_category" in frame_preview.columns:
        categories += sorted({c for c in frame_preview["chip_category"].astype(str) if c})
    tech_states = ["全部"]
    if not frame_preview.empty and "tech_action" in frame_preview.columns:
        tech_states += sorted({c for c in frame_preview["tech_action"].astype(str) if c})
    category = st.selectbox("籌碼分類", categories)
    tech_state = st.selectbox("技術狀態", tech_states)
    sort_by = st.selectbox("排序", ["預設（共振置頂）", "成交量", "投信買超", "外資買超"])
    palette = st.toggle("國際配色（綠漲紅跌）", value=False)
    st.caption("資料來自 titan_core_chip 報告，快取 5 分鐘。")

st.markdown(components.apply_palette("intl" if palette else "tw"), unsafe_allow_html=True)

df, meta = data_loader.load_chip_data(as_of=selected_date if dates else None)
if meta.get("as_of"):
    st.caption(f"資料日 {meta['as_of']} · 來源 `{meta.get('source')}`")

kpis = components.render_kpi_metrics(df)
c1, c2, c3, c4 = st.columns(4)
c1.metric("今日掃描", kpis["scanned"])
c2.metric("💎 多頭雙共振", kpis["bull"])
c3.metric("💀 空頭雙共振", kpis["bear"])
c4.metric("投信積極買超", kpis["trust_active"])

view = df.copy()
if not view.empty:
    if resonance_filter.startswith("💎"):
        view = view[view["is_resonance_bull"]]
    elif resonance_filter.startswith("💀"):
        view = view[view["is_resonance_bear"]]
    if category != "全部":
        view = view[view["chip_category"] == category]
    if tech_state != "全部":
        view = view[view["tech_action"] == tech_state]
    if sort_by == "成交量":
        view = view.sort_values("volume_lots", ascending=False, na_position="last")
    elif sort_by == "投信買超":
        view = view.sort_values("trust_net_lots", ascending=False, na_position="last")
    elif sort_by == "外資買超":
        view = view.sort_values("foreign_net_lots", ascending=False, na_position="last")
    else:
        view = view.assign(_rank=view["is_resonance_bull"].map(lambda v: 0 if v else 1) + view["is_resonance_bear"].map(lambda v: 0 if v else 1))
        view = view.sort_values(["_rank", "symbol"]).drop(columns="_rank")

tab_focus, tab_all, tab_md = st.tabs(["💎 雙共振焦點", "📊 全市場分析清單", "📝 最新 Markdown 盤後報告"])

with tab_focus:
    if view.empty:
        st.info("沒有符合篩選的標的。")
    else:
        focus = view[view["is_resonance_bull"] | view["is_resonance_bear"]]
        if focus.empty:
            st.warning("今日無雙共振標的。")
        else:
            focus_rows = focus.to_dict(orient="records")
            st.markdown(components.render_cards_container(focus_rows, grid_class="tc-cards-grid-2"), unsafe_allow_html=True)

with tab_all:
    mode = st.radio("檢視", ["卡片網格", "表格"], horizontal=True)
    if view.empty:
        st.info("沒有符合篩選的標的。")
    elif mode == "表格":
        show_cols = [c for c in [
            "symbol", "name", "close", "chip_category", "resonance", "tech_action",
            "ema_trend", "ichimoku_trend", "adx", "trust_net_lots", "trust_streak",
            "foreign_net_lots", "short_margin_ratio", "volume_lots", "summary_note",
        ] if c in view.columns]
        st.dataframe(view[show_cols], use_container_width=True, hide_index=True)
    else:
        all_rows = view.to_dict(orient="records")
        st.markdown(components.render_cards_container(all_rows, grid_class="tc-cards-grid"), unsafe_allow_html=True)

with tab_md:
    st.markdown(data_loader.load_latest_summary_md())
