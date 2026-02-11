# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import json
from datetime import datetime
import pytz

# Page config
st.set_page_config(
    page_title="一目均衡表訊號儀表板",
    page_icon="📊",
    layout="wide"
)

# Constants
DATA_FILE = 'data/analysis_results.json'
taipei_tz = pytz.timezone('Asia/Taipei')


def get_chart_url(symbol, source):
    """Generate TradingView chart URL."""
    if source == 'Forex':
        # Remove / from EUR/USD -> EURUSD
        tv_symbol = symbol.replace('/', '')
        return f"https://www.tradingview.com/chart/?symbol=FX:{tv_symbol}"
    else:
        # BTC-USDT -> BTCUSDT
        tv_symbol = symbol.replace('-', '')
        return f"https://www.tradingview.com/chart/?symbol=OKX:{tv_symbol}"


def load_data():
    """Load analysis results from JSON file."""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Ensure chart_url exists for all results
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


def get_recommendation_emoji(rec):
    """Get emoji for recommendation."""
    emoji_map = {
        '強力做多': '🟢✨',
        '強力做空': '🔴✨',
        '偏多操作': '📈',
        '偏空操作': '📉',
        '短多試單': '🟡📈',
        '短空試單': '🟠📉',
        '觀望等待': '⏸️',
        '觀望': '⏸️',
        '觀望偏多': '⏸️📈',
        '觀望偏空': '⏸️📉',
    }
    return emoji_map.get(rec, '❓')


def get_trend_emoji(trend):
    """Get emoji for trend."""
    emoji_map = {
        '強勢上升趨勢': '💪🔥',
        '強勢下降趨勢': '💪❄️',
        '盤整區間': '↔️',
        '趨勢不明確': '❓',
        '資料不足': '⚠️',
    }
    return emoji_map.get(trend, '')


def format_signals(signals):
    """Format signal list to string."""
    if not signals:
        return "無訊號"
    return " / ".join(signals)


def render_symbol_card(result):
    """Render a detailed card for a symbol."""
    symbol = result['symbol']
    source = result['source']
    rec = result['combined_recommendation']
    exp = result['combined_explanation']
    
    # Card header color based on recommendation
    if '做多' in rec or '偏多' in rec:
        header_color = "#1a472a"  # Dark green
    elif '做空' in rec or '偏空' in rec:
        header_color = "#4a1a1a"  # Dark red
    else:
        header_color = "#3d3d3d"  # Gray
    
    source_badge = "💱 外匯" if source == 'Forex' else "🪙 加密貨幣"
    
    with st.container():
        chart_url = result.get('chart_url', '#')
        st.markdown(f"""
        <div style="background-color: {header_color}; padding: 10px; border-radius: 10px 10px 0 0;">
            <h3 style="margin: 0; color: white;">
                {get_recommendation_emoji(rec)} {symbol}
                <a href="{chart_url}" target="_blank" style="color: white; text-decoration: none; font-size: 0.7em;" title="查看 K 線圖">🔗</a>
            </h3>
            <small style="color: #ccc;">{source_badge}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Combined recommendation
        st.markdown(f"**🎯 綜合建議：{rec}**")
        st.markdown(f"💡 {exp}")
        
        # ===== AI 建議區塊（新增）=====
        if result.get('ai_advice'):
            st.markdown("---")
            ai_provider = result.get('ai_provider', 'AI')
            ai_model = result.get('ai_model', '')
            
            # 顯示 AI 建議
            st.markdown(f"##### 🤖 AI 分析建議")
            st.markdown(f"<small style='color: #888;'>由 {ai_provider} ({ai_model}) 生成</small>", unsafe_allow_html=True)
            
            # 使用 info box 顯示 AI 建議
            st.info(result['ai_advice'])
        
        st.markdown("---")
        
        # Two columns for Daily and 4H
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 日線 (1D)")
            if result['daily']:
                d = result['daily']
                st.markdown(f"**訊號：** {format_signals(d['signals'])}")
                st.markdown(f"**趨勢：** {d['trend']} {get_trend_emoji(d['trend'])}")
                st.markdown(f"**建議：** {d['recommendation']}")
                st.markdown(f"💹 價格：`{d['price']:.4f}`")
                st.markdown(f"📈 轉換線：`{d['tenkan_sen']:.4f}`")
                st.markdown(f"📊 基準線：`{d['kijun_sen']:.4f}`")
                st.markdown(f"☁️ 雲層：`{d['cloud_bottom']:.4f}` ~ `{d['cloud_top']:.4f}`")
            else:
                st.markdown("*資料不足*")
        
        with col2:
            st.markdown("##### ⏰ 4小時線 (4H)")
            if result['h4']:
                h = result['h4']
                st.markdown(f"**訊號：** {format_signals(h['signals'])}")
                st.markdown(f"**趨勢：** {h['trend']} {get_trend_emoji(h['trend'])}")
                st.markdown(f"**建議：** {h['recommendation']}")
                st.markdown(f"💹 價格：`{h['price']:.4f}`")
                st.markdown(f"📈 轉換線：`{h['tenkan_sen']:.4f}`")
                st.markdown(f"📊 基準線：`{h['kijun_sen']:.4f}`")
                st.markdown(f"☁️ 雲層：`{h['cloud_bottom']:.4f}` ~ `{h['cloud_top']:.4f}`")
            else:
                st.markdown("*資料不足*")
        
        st.markdown("---")


def main():
    # Title
    st.title("📊 一目均衡表訊號儀表板")
    st.markdown("Ichimoku Kinko Hyo Signal Dashboard")
    
    # Load data
    data = load_data()
    
    if data is None:
        st.warning("⚠️ 尚無分析資料，請等待下次排程執行或手動執行分析程式。")
        st.stop()
    
    # Show last update time
    generated_at = data.get('generated_at', 'Unknown')
    try:
        dt = datetime.fromisoformat(generated_at)
        time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        time_str = generated_at
    
    st.markdown(f"🕐 最後更新：**{time_str}** (UTC+8)")
    
    results = data.get('results', [])
    
    if not results:
        st.warning("沒有分析結果")
        st.stop()
    

    # Sidebar filters
    st.sidebar.header("🔍 篩選條件")
    
    # Source filter
    source_options = ['全部', '加密貨幣', '外匯']
    source_filter = st.sidebar.selectbox("資料來源", source_options)
    
    # Recommendation filter
    rec_options = ['全部', '強力訊號', '做多方向', '做空方向', '觀望']
    rec_filter = st.sidebar.selectbox("建議方向", rec_options)
    
    # Has signal filter
    signal_filter = st.sidebar.checkbox("只顯示有訊號的標的", value=True)
    
    # AI advice filter (新增)
    ai_filter = st.sidebar.checkbox("只顯示有 AI 建議的標的", value=False)
    
    # Apply filters
    filtered = results.copy()
    
    if source_filter == '加密貨幣':
        filtered = [r for r in filtered if r['source'] == 'Crypto']
    elif source_filter == '外匯':
        filtered = [r for r in filtered if r['source'] == 'Forex']
    
    if rec_filter == '強力訊號':
        filtered = [r for r in filtered if '強力' in r['combined_recommendation']]
    elif rec_filter == '做多方向':
        filtered = [r for r in filtered if '多' in r['combined_recommendation']]
    elif rec_filter == '做空方向':
        filtered = [r for r in filtered if '空' in r['combined_recommendation']]
    elif rec_filter == '觀望':
        filtered = [r for r in filtered if '觀望' in r['combined_recommendation']]
    
    if signal_filter:
        filtered = [r for r in filtered if r['has_signal']]
    
    if ai_filter:
        filtered = [r for r in filtered if r.get('ai_advice')]
    
    # Summary stats
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_signals = len([r for r in results if r['has_signal']])
    strong_bull = len([r for r in results if r['combined_recommendation'] == '強力做多'])
    strong_bear = len([r for r in results if r['combined_recommendation'] == '強力做空'])
    ai_generated = len([r for r in results if r.get('ai_advice')])
    
    col1.metric("📊 分析標的數", len(results))
    col2.metric("🔔 有訊號標的", total_signals)
    col3.metric("🟢 強力做多", strong_bull)
    col4.metric("🔴 強力做空", strong_bear)
    col5.metric("🤖 AI 建議數", ai_generated)
    
    st.markdown("---")
    
    # Results table
    st.subheader(f"📋 分析結果 ({len(filtered)} 個標的)")
    
    if not filtered:
        st.info("沒有符合篩選條件的結果")
    else:
        # Create summary table
        table_data = []
        for r in filtered:
            daily_sig = format_signals(r['daily']['signals']) if r['daily'] else '-'
            h4_sig = format_signals(r['h4']['signals']) if r['h4'] else '-'
            daily_trend = r['daily']['trend'] if r['daily'] else '-'
            h4_trend = r['h4']['trend'] if r['h4'] else '-'
            price = r['daily']['price'] if r['daily'] else (r['h4']['price'] if r['h4'] else '-')
            has_ai = '✅' if r.get('ai_advice') else '❌'
            
            table_data.append({
                '標的': r['symbol'],
                '來源': '💱' if r['source'] == 'Forex' else '🪙',
                '綜合建議': f"{get_recommendation_emoji(r['combined_recommendation'])} {r['combined_recommendation']}",
                '日線訊號': daily_sig,
                '4H訊號': h4_sig,
                '日線趨勢': daily_trend,
                '4H趨勢': h4_trend,
                '價格': f"{price:.4f}" if isinstance(price, float) else price,
                'AI': has_ai,
                'K線圖': r.get('chart_url', ''),
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "K線圖": st.column_config.LinkColumn("K線圖", display_text="🔗 查看")
            }
        )
        
        st.markdown("---")
        
        # Detailed cards
        st.subheader("📇 詳細分析")
        
        # Sort by recommendation priority
        priority = {
            '強力做多': 0, '強力做空': 1,
            '偏多操作': 2, '偏空操作': 3,
            '短多試單': 4, '短空試單': 5,
            '觀望等待': 6, '觀望': 7,
        }
        filtered.sort(key=lambda x: priority.get(x['combined_recommendation'], 99))
        
        # Display in 2-column grid
        for i in range(0, len(filtered), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(filtered):
                    with col:
                        render_symbol_card(filtered[i + j])
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        ⚠️ <b>免責聲明</b>：本系統僅提供技術分析參考，不構成投資建議。AI 建議由第三方模型生成，僅供參考。交易有風險，請謹慎評估自身風險承受能力。
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
