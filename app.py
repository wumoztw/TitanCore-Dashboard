# -*- coding: utf-8 -*-
import re
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from datetime import datetime
import pytz

# Page config
st.set_page_config(
    page_title="TitanCore · 一目均衡表儀表板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = 'data/analysis_results.json'
taipei_tz = pytz.timezone('Asia/Taipei')

# ══════════════════════════════════════════════════════════
# CSS — injected once into Streamlit host page
# ══════════════════════════════════════════════════════════
GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #060b18 0%, #0d1b2e 40%, #0a1628 70%, #060e1c 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(12,22,52,0.97) 0%, rgba(8,16,40,0.99) 100%) !important;
    border-right: 1px solid rgba(100,160,255,0.12);
}
[data-testid="stSidebar"] label {
    color: #90b8ff !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(20,40,100,0.5) !important;
    border: 1px solid rgba(80,140,255,0.25) !important;
    border-radius: 10px !important;
    color: #d8eaff !important;
}
[data-testid="stSidebar"] .stCheckbox label span { color: #b0d0ff !important; }

/* Hero */
.hero-header {
    background: linear-gradient(135deg, rgba(18,38,100,0.75), rgba(10,28,78,0.85));
    border: 1px solid rgba(80,140,255,0.18);
    border-radius: 20px;
    padding: 30px 40px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(20px);
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -60%; left: -60%;
    width: 220%; height: 220%;
    background: conic-gradient(from 0deg, transparent 0deg, rgba(60,130,255,0.05) 60deg,
        transparent 120deg, rgba(80,220,160,0.04) 180deg,
        transparent 240deg, rgba(160,80,255,0.04) 300deg, transparent 360deg);
    animation: heroSpin 25s linear infinite;
    pointer-events: none;
}
@keyframes heroSpin { to { transform: rotate(360deg); } }
.hero-title {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, #60b4ff 0%, #40e8c0 55%, #a060ff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin: 0 0 6px; letter-spacing: -0.02em;
}
.hero-subtitle {
    color: rgba(150,190,255,0.7);
    font-size: 0.88rem; letter-spacing: 0.1em; text-transform: uppercase;
}
.hero-timestamp {
    display: inline-flex; align-items: center; gap: 8px;
    margin-top: 14px; padding: 6px 16px;
    background: rgba(50,110,255,0.12);
    border: 1px solid rgba(60,120,255,0.22);
    border-radius: 50px; color: #70a8ff;
    font-size: 0.8rem; font-family: 'JetBrains Mono', monospace;
}

/* Metrics */
.metric-grid {
    display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin: 20px 0 28px;
}
.metric-card {
    background: linear-gradient(145deg, rgba(18,33,80,0.85), rgba(12,26,65,0.9));
    border-radius: 16px; padding: 20px 16px; text-align: center;
    border: 1px solid rgba(60,110,220,0.18);
    position: relative; overflow: hidden;
    transition: transform 0.3s cubic-bezier(.34,1.56,.64,1), box-shadow 0.3s;
}
.metric-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 2px; border-radius: 16px 16px 0 0;
}
.mc-blue::after   { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.mc-cyan::after   { background: linear-gradient(90deg, #06b6d4, #67e8f9); }
.mc-green::after  { background: linear-gradient(90deg, #10b981, #6ee7b7); }
.mc-red::after    { background: linear-gradient(90deg, #ef4444, #fca5a5); }
.mc-purple::after { background: linear-gradient(90deg, #8b5cf6, #c4b5fd); }
.metric-card:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow: 0 18px 40px rgba(0,0,0,0.4), 0 0 20px rgba(60,130,255,0.12);
}
.metric-icon  { font-size: 1.5rem; margin-bottom: 6px; display: block; }
.metric-value { font-size: 2.1rem; font-weight: 800; color: #e8f0ff; line-height: 1; font-family: 'JetBrains Mono', monospace; }
.metric-label { font-size: 0.72rem; color: rgba(150,190,255,0.6); margin-top: 5px; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; }

/* Section */
.section-header { display: flex; align-items: center; gap: 12px; margin: 28px 0 14px; }
.section-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 13px; background: rgba(40,90,255,0.15);
    border: 1px solid rgba(70,130,255,0.28); border-radius: 50px;
    color: #88b8ff; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.04em;
}
.section-title { font-size: 1.2rem; font-weight: 700; color: #cce0ff; }

/* Divider */
.fancy-divider {
    height: 1px; border: none; margin: 22px 0;
    background: linear-gradient(90deg, transparent, rgba(70,130,255,0.3), rgba(70,200,150,0.28), rgba(130,70,255,0.28), transparent);
}

/* Footer */
.footer-text {
    text-align: center; padding: 18px;
    color: rgba(110,145,200,0.45); font-size: 0.76rem;
    border-top: 1px solid rgba(50,90,200,0.12); margin-top: 14px;
}

/* Streamlit overrides */
h1, h2, h3 { color: #d8eaff !important; }
.stAlert { border-radius: 12px !important; }
#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none; }
"""

# ══════════════════════════════════════════════════════════
# CSS embedded inside each card component (self-contained)
# ══════════════════════════════════════════════════════════
CARD_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: transparent; font-family: 'Inter', 'PingFang TC', sans-serif; }

.symbol-card {
    background: linear-gradient(160deg, rgba(18,32,78,0.92) 0%, rgba(12,24,62,0.95) 100%);
    border-radius: 16px; overflow: hidden;
    border: 1px solid rgba(60,110,220,0.22);
    box-shadow: 0 4px 24px rgba(0,0,0,0.35);
    transition: transform .35s cubic-bezier(.34,1.4,.64,1), box-shadow .35s;
}
.symbol-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 28px rgba(60,130,255,0.1);
}

/* Card header */
.card-header {
    padding: 14px 18px 12px; position: relative; overflow: hidden;
}
.card-header.bull {
    background: linear-gradient(135deg, rgba(14,58,38,0.96), rgba(8,44,28,0.98));
    border-bottom: 1px solid rgba(36,190,110,0.22);
}
.card-header.bear {
    background: linear-gradient(135deg, rgba(60,14,18,0.96), rgba(44,8,12,0.98));
    border-bottom: 1px solid rgba(210,50,70,0.22);
}
.card-header.neutral {
    background: linear-gradient(135deg, rgba(28,34,68,0.96), rgba(20,28,60,0.98));
    border-bottom: 1px solid rgba(90,110,210,0.18);
}
.card-header::after {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 110px; height: 110px; border-radius: 50%; opacity: 0.07;
}
.card-header.bull::after  { background: #40e098; }
.card-header.bear::after  { background: #ff4060; }
.card-header.neutral::after { background: #7090ff; }

.card-symbol {
    font-size: 1.25rem; font-weight: 700; color: #fff;
    display: flex; align-items: center; gap: 8px;
}
.card-symbol a {
    color: rgba(180,210,255,0.55); text-decoration: none;
    font-size: 0.85rem; font-weight: 400;
    transition: color .2s;
}
.card-symbol a:hover { color: #70b8ff; }
.source-badge {
    display: inline-flex; align-items: center; gap: 4px;
    margin-top: 6px; padding: 3px 10px; border-radius: 50px;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em;
}
.badge-crypto { background: rgba(60,140,255,0.15); border: 1px solid rgba(60,140,255,0.28); color: #72b8ff; }
.badge-forex  { background: rgba(255,175,40,0.13); border: 1px solid rgba(255,175,40,0.28); color: #ffc855; }

/* Card body */
.card-body { padding: 14px 18px 18px; }

.rec-pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 5px 13px; border-radius: 50px;
    font-size: 0.8rem; font-weight: 700; letter-spacing: 0.03em; margin-bottom: 7px;
}
.rec-bull    { background: rgba(24,170,90,0.18); border: 1px solid rgba(24,170,90,0.38); color: #46d888; }
.rec-bear    { background: rgba(200,36,55,0.18); border: 1px solid rgba(200,36,55,0.38); color: #f86080; }
.rec-neutral { background: rgba(90,110,220,0.18); border: 1px solid rgba(90,110,220,0.32); color: #9ab2ff; }

.rec-exp { font-size: 0.8rem; color: rgba(170,195,240,0.65); margin-bottom: 12px; }

/* TF grid */
.tf-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.tf-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(70,110,220,0.14);
    border-radius: 10px; padding: 12px 14px;
}
.tf-label {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.09em;
    text-transform: uppercase; margin-bottom: 8px;
    display: flex; align-items: center; gap: 5px;
}
.tf-label.daily { color: #5a9aff; }
.tf-label.h4    { color: #38c8a0; }

.signal-row { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 6px; }
.sig-pill { padding: 2px 9px; border-radius: 50px; font-size: 0.68rem; font-weight: 600; }
.sig-bull { background: rgba(24,170,90,0.16); border: 1px solid rgba(24,170,90,0.32); color: #46d880; }
.sig-bear { background: rgba(200,40,60,0.16); border: 1px solid rgba(200,40,60,0.32); color: #f86078; }
.sig-none { background: rgba(90,110,180,0.1); border: 1px solid rgba(90,110,180,0.18); color: rgba(150,170,210,0.45); font-style: italic; }

.trend-badge {
    display: inline-flex; align-items: center; gap: 3px;
    padding: 2px 8px; border-radius: 50px; font-size: 0.68rem; font-weight: 600;
    margin-bottom: 8px;
}
.t-up   { background: rgba(24,190,100,0.14); border: 1px solid rgba(24,190,100,0.28); color: #46d880; }
.t-down { background: rgba(200,40,60,0.14);  border: 1px solid rgba(200,40,60,0.28);  color: #f86078; }
.t-range{ background: rgba(190,150,30,0.14); border: 1px solid rgba(190,150,30,0.28); color: #ffc840; }
.t-unk  { background: rgba(90,110,180,0.12); border: 1px solid rgba(90,110,180,0.22); color: rgba(140,160,210,0.7); }

.data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }
.data-item { background: rgba(255,255,255,0.035); border-radius: 7px; padding: 6px 9px; }
.data-key  { font-size: 0.65rem; color: rgba(130,160,215,0.55); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 2px; }
.data-val  { font-size: 0.83rem; font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #c8deff; }
.data-val.price { color: #ffd055; }
.data-val.cloud { font-size: 0.72rem; }

/* AI block */
.ai-block {
    margin-top: 12px;
    background: linear-gradient(135deg, rgba(70,30,150,0.16), rgba(40,18,110,0.2));
    border: 1px solid rgba(130,70,255,0.22);
    border-radius: 10px; padding: 12px 14px; position: relative; overflow: hidden;
}
.ai-block::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #7030ff, #c070ff, #7030ff);
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
}
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
.ai-header { display: flex; align-items: center; gap: 7px; margin-bottom: 7px; }
.ai-title  { font-size: 0.76rem; font-weight: 700; color: #bb78ff; letter-spacing: 0.05em; text-transform: uppercase; }
.ai-model  { font-size: 0.65rem; color: rgba(170,130,255,0.5); font-family: 'JetBrains Mono', monospace; }
.ai-body   { font-size: 0.78rem; color: rgba(195,178,240,0.8); line-height: 1.65; }
.ai-body strong { color: #cc99ff; }
.ai-body h2, .ai-body h3 { color: #bb88ff; font-size: 0.8rem; margin: 7px 0 3px; }
"""


def inject_css():
    st.markdown(f"<style>{GLOBAL_CSS}</style>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data and 'results' in data:
            for r in data['results']:
                if not r.get('chart_url'):
                    r['chart_url'] = get_chart_url(r['symbol'], r['source'])
        return data
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"載入資料錯誤: {e}")
        return None


def get_chart_url(symbol, source):
    if source == 'Forex':
        return f"https://www.tradingview.com/chart/?symbol=FX_IDC:{symbol.replace('/','')}"
    return f"https://www.tradingview.com/chart/?symbol=OKX:{symbol.replace('-','')}"


# ══════════════════════════════════════════════════════════
# HTML helpers
# ══════════════════════════════════════════════════════════
def rec_class(rec):
    if '做多' in rec or '偏多' in rec: return 'bull'
    if '做空' in rec or '偏空' in rec: return 'bear'
    return 'neutral'

def rec_pill_cls(rec):
    if '做多' in rec or '偏多' in rec: return 'rec-bull'
    if '做空' in rec or '偏空' in rec: return 'rec-bear'
    return 'rec-neutral'

def rec_emoji(rec):
    return {'強力做多':'🟢✨','強力做空':'🔴✨','偏多操作':'📈','偏空操作':'📉',
            '短多試單':'🟡📈','短空試單':'🟠📉','觀望等待':'⏸️','觀望':'⏸️',
            '觀望偏多':'⏸️📈','觀望偏空':'⏸️📉'}.get(rec,'❓')

def trend_html(trend):
    m = {'強勢上升趨勢':('t-up','🔥'),'強勢下降趨勢':('t-down','❄️'),
         '盤整區間':('t-range','↔️'),'趨勢不明確':('t-unk','❓'),'資料不足':('t-unk','⚠️')}
    cls, icon = m.get(trend, ('t-unk',''))
    return f'<span class="trend-badge {cls}">{icon} {trend}</span>'

BULL_SIGS = {'三役好轉','黃金交叉','突破雲層','遲行線好轉'}
def signals_html(sigs):
    if not sigs:
        return '<span class="sig-pill sig-none">無訊號</span>'
    return ''.join(f'<span class="sig-pill {"sig-bull" if s in BULL_SIGS else "sig-bear"}">{s}</span>' for s in sigs)

def fmt_price(v):
    if not isinstance(v, float): return str(v)
    if v >= 1000: return f"{v:,.2f}"
    if v >= 1:    return f"{v:.4f}"
    return f"{v:.6f}"

def tf_block_html(d, label, lbl_cls):
    if not d:
        return f'<div class="tf-section"><div class="tf-label {lbl_cls}">{label}</div><span style="color:rgba(160,180,220,0.35);font-size:0.78rem">資料不足</span></div>'
    price  = fmt_price(d.get('price', 0))
    tenkan = fmt_price(d.get('tenkan_sen', 0))
    kijun  = fmt_price(d.get('kijun_sen', 0))
    cb     = fmt_price(d.get('cloud_bottom', 0))
    ct     = fmt_price(d.get('cloud_top', 0))
    return f"""
<div class="tf-section">
  <div class="tf-label {lbl_cls}">{label}</div>
  <div class="signal-row">{signals_html(d.get('signals',[]))}</div>
  {trend_html(d.get('trend',''))}
  <div class="data-grid">
    <div class="data-item"><div class="data-key">現價</div><div class="data-val price">{price}</div></div>
    <div class="data-item"><div class="data-key">轉換線</div><div class="data-val">{tenkan}</div></div>
    <div class="data-item"><div class="data-key">基準線</div><div class="data-val">{kijun}</div></div>
    <div class="data-item"><div class="data-key">雲層</div><div class="data-val cloud">{cb}~{ct}</div></div>
  </div>
</div>"""

def ai_block_html(result):
    if not result.get('ai_advice'):
        return ''
    provider = result.get('ai_provider', 'AI')
    model    = result.get('ai_model', '')
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', result['ai_advice'])
    body = body.replace('\n', '<br>')
    return f"""
<div class="ai-block">
  <div class="ai-header">
    <span style="font-size:1rem">🤖</span>
    <span class="ai-title">AI 分析建議</span>
    <span class="ai-model">· {provider} / {model}</span>
  </div>
  <div class="ai-body">{body}</div>
</div>"""

# ══════════════════════════════════════════════════════════
# Card renderer — uses components.html to avoid Streamlit's
# HTML sanitiser stripping nested tags
# ══════════════════════════════════════════════════════════
def render_symbol_card(result):
    rec       = result['combined_recommendation']
    symbol    = result['symbol']
    source    = result['source']
    exp       = result['combined_explanation']
    chart_url = result.get('chart_url', '#')

    hdr_cls  = rec_class(rec)
    src_cls  = 'badge-crypto' if source == 'Crypto' else 'badge-forex'
    src_label= '🪙 加密貨幣' if source == 'Crypto' else '💱 外匯'

    daily_html = tf_block_html(result.get('daily'), '📊 日線 (1D)', 'daily')
    h4_html    = tf_block_html(result.get('h4'),    '⏱ 4小時 (4H)', 'h4')
    ai_html    = ai_block_html(result)

    # Estimate height: base 260 + AI if present + extra for many signals
    has_ai     = bool(result.get('ai_advice'))
    ai_lines   = result['ai_advice'].count('\n') if has_ai else 0
    est_height = 300 + (ai_lines * 18 if has_ai else 0) + 60

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>{CARD_CSS}</style>
</head><body>
<div class="symbol-card">
  <div class="card-header {hdr_cls}">
    <div class="card-symbol">
      {rec_emoji(rec)}&nbsp;{symbol}
      <a href="{chart_url}" target="_blank" title="TradingView K線圖">&nearr;</a>
    </div>
    <div style="margin-top:5px"><span class="source-badge {src_cls}">{src_label}</span></div>
  </div>
  <div class="card-body">
    <div><span class="rec-pill {rec_pill_cls(rec)}">{rec_emoji(rec)} {rec}</span></div>
    <div class="rec-exp">💡 {exp}</div>
    <div class="tf-grid">
      {daily_html}
      {h4_html}
    </div>
    {ai_html}
  </div>
</div>
</body></html>"""

    components.html(html, height=est_height, scrolling=False)


# ══════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════
def main():
    inject_css()

    data = load_data()

    # Hero header
    if data:
        try:
            dt = datetime.fromisoformat(data.get('generated_at', ''))
            time_str = dt.strftime('%Y-%m-%d %H:%M')
        except Exception:
            time_str = data.get('generated_at', '')
        ts = f'<div class="hero-timestamp">🕐 最後更新 &nbsp;{time_str} (UTC+8)</div>'
    else:
        ts = ''

    st.markdown(f"""
    <div class="hero-header">
      <div class="hero-title">📊 TitanCore Dashboard</div>
      <div class="hero-subtitle">Ichimoku Kinko Hyo &nbsp;·&nbsp; Multi-Timeframe Signal Analysis</div>
      {ts}
    </div>""", unsafe_allow_html=True)

    if data is None:
        st.warning("⚠️ 尚無分析資料，請等待下次排程執行或手動執行分析程式。")
        st.stop()

    results = data.get('results', [])
    if not results:
        st.warning("沒有分析結果")
        st.stop()

    # ── Sidebar ──────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔍 篩選條件")
        st.divider()
        source_filter = st.selectbox(
            "資料來源", ['全部', '加密貨幣', '外匯'],
            format_func=lambda x: {'全部':'🌐 全部','加密貨幣':'🪙 加密貨幣','外匯':'💱 外匯'}[x])
        rec_filter = st.selectbox(
            "建議方向", ['全部', '強力訊號', '做多方向', '做空方向', '觀望'],
            format_func=lambda x: {'全部':'📊 全部','強力訊號':'✨ 強力訊號',
                '做多方向':'📈 做多方向','做空方向':'📉 做空方向','觀望':'⏸️ 觀望'}[x])
        signal_filter = st.checkbox("只顯示有訊號的標的", value=True)
        ai_filter     = st.checkbox("只顯示有 AI 建議的標的", value=False)
        st.divider()
        st.markdown("""<div style="font-size:.7rem;color:rgba(130,160,215,.45);line-height:1.8">
        ⚠️ 本系統僅供技術分析參考，<br>不構成投資建議。<br>交易有風險，請謹慎評估。
        </div>""", unsafe_allow_html=True)

    # ── Apply filters ─────────────────────────────────────
    filtered = results.copy()
    if source_filter == '加密貨幣': filtered = [r for r in filtered if r['source'] == 'Crypto']
    elif source_filter == '外匯':   filtered = [r for r in filtered if r['source'] == 'Forex']
    if rec_filter == '強力訊號':    filtered = [r for r in filtered if '強力' in r['combined_recommendation']]
    elif rec_filter == '做多方向':  filtered = [r for r in filtered if '多' in r['combined_recommendation']]
    elif rec_filter == '做空方向':  filtered = [r for r in filtered if '空' in r['combined_recommendation']]
    elif rec_filter == '觀望':      filtered = [r for r in filtered if '觀望' in r['combined_recommendation']]
    if signal_filter: filtered = [r for r in filtered if r['has_signal']]
    if ai_filter:     filtered = [r for r in filtered if r.get('ai_advice')]

    # ── Metric cards ──────────────────────────────────────
    total_signals = len([r for r in results if r['has_signal']])
    strong_bull   = len([r for r in results if r['combined_recommendation'] == '強力做多'])
    strong_bear   = len([r for r in results if r['combined_recommendation'] == '強力做空'])
    ai_generated  = len([r for r in results if r.get('ai_advice')])

    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-card mc-blue"><span class="metric-icon">📊</span>
        <div class="metric-value">{len(results)}</div><div class="metric-label">分析標的</div></div>
      <div class="metric-card mc-cyan"><span class="metric-icon">🔔</span>
        <div class="metric-value">{total_signals}</div><div class="metric-label">有訊號標的</div></div>
      <div class="metric-card mc-green"><span class="metric-icon">🟢</span>
        <div class="metric-value">{strong_bull}</div><div class="metric-label">強力做多</div></div>
      <div class="metric-card mc-red"><span class="metric-icon">🔴</span>
        <div class="metric-value">{strong_bear}</div><div class="metric-label">強力做空</div></div>
      <div class="metric-card mc-purple"><span class="metric-icon">🤖</span>
        <div class="metric-value">{ai_generated}</div><div class="metric-label">AI 建議</div></div>
    </div>""", unsafe_allow_html=True)

    # ── Summary table ─────────────────────────────────────
    st.markdown(f"""
    <div class="section-header">
      <span class="section-badge">📋 總覽</span>
      <span class="section-title">分析結果 · {len(filtered)} 個標的</span>
    </div>""", unsafe_allow_html=True)

    if not filtered:
        st.info("🔍 沒有符合篩選條件的結果")
        return

    table_data = []
    for r in filtered:
        d = r.get('daily'); h = r.get('h4')
        price = d['price'] if d else (h['price'] if h else '-')
        table_data.append({
            '標的': r['symbol'],
            '來源': '💱' if r['source'] == 'Forex' else '🪙',
            '綜合建議': f"{rec_emoji(r['combined_recommendation'])} {r['combined_recommendation']}",
            '日線訊號': ' / '.join(d['signals']) if d and d['signals'] else '無訊號',
            '4H訊號':   ' / '.join(h['signals']) if h and h['signals'] else '無訊號',
            '日線趨勢': d['trend'] if d else '-',
            '4H趨勢':   h['trend'] if h else '-',
            '價格': fmt_price(price),
            'AI': '✅' if r.get('ai_advice') else '❌',
            'K線圖': r.get('chart_url', ''),
        })

    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True,
                 column_config={"K線圖": st.column_config.LinkColumn("K線圖", display_text="🔗 查看")})

    # ── Detailed cards ────────────────────────────────────
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    priority = {'強力做多':0,'強力做空':1,'偏多操作':2,'偏空操作':3,
                '短多試單':4,'短空試單':5,'觀望等待':6,'觀望':7}
    filtered.sort(key=lambda x: priority.get(x['combined_recommendation'], 99))

    st.markdown("""
    <div class="section-header">
      <span class="section-badge">📇 詳細</span>
      <span class="section-title">個別標的分析卡</span>
    </div>""", unsafe_allow_html=True)

    for i in range(0, len(filtered), 2):
        cols = st.columns(2, gap="medium")
        for j, col in enumerate(cols):
            if i + j < len(filtered):
                with col:
                    render_symbol_card(filtered[i + j])

    # ── Footer ────────────────────────────────────────────
    st.markdown("""
    <div class="footer-text">
      ⚠️ <b>免責聲明</b>：本系統僅提供技術分析參考，不構成投資建議。
      AI 建議由第三方模型生成，僅供參考。交易有風險，請謹慎評估自身風險承受能力。
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
