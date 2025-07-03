import streamlit as st
from datetime import datetime
from data_fetcher import fetch_ohlc_data
from pattern_detector import detect_patterns
from chart_plotter import plot_chart
from ai_advisor import generate_trade_advice
from logger import log_trade

st.set_page_config(page_title="BTC Buddy 💹", layout="wide", initial_sidebar_state="expanded")

# Sidebar
st.sidebar.title("⚙️ BTC Buddy Settings")
sl_percent = st.sidebar.number_input("🔧 Stop Loss %", min_value=0.1, max_value=10.0, value=1.5, step=0.1)
tp_percent = st.sidebar.number_input("🎯 Take Profit %", min_value=0.1, max_value=10.0, value=3.0, step=0.1)
confidence_threshold = st.sidebar.slider("🧠 Confidence Threshold", 50, 100, 70)
tone = st.sidebar.radio("🎭 Tone", ["Meme 🤡", "Chad 💪", "Pro 📊"])

# Manual refresh button
if st.button("🔄 Refresh Now"):
    st.experimental_rerun()

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Main app
st.title("🚀 BTC Buddy – Your Pattern-Powered Crypto Pal")

with st.spinner("Fetching BTC data..."):
    ohlc_df = fetch_ohlc_data()
    if ohlc_df is not None:
        st.subheader("📈 Latest BTC Chart")
        st.plotly_chart(plot_chart(ohlc_df), use_container_width=True)

        pattern_info = detect_patterns(ohlc_df)

        if pattern_info and pattern_info['confidence'] >= confidence_threshold:
            st.success(f"📉 Pattern Detected: {pattern_info['name']} with {pattern_info['confidence']}% confidence!")

            entry = pattern_info['entry']
            sl = round(entry * (1 - sl_percent / 100), 2)
            tp = round(entry * (1 + tp_percent / 100), 2)

            # Log the trade to CSV here
            log_trade(pattern_info, sl, tp)

            advice = generate_trade_advice(pattern_info, sl_percent, tp_percent, tone)
            st.subheader("🤖 Trade Suggestion")
            st.markdown(advice)
        else:
            st.warning("📡 No strong patterns detected right now. Try again later!")
    else:
        st.error("❌ Failed to fetch BTC data.")
