import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(page_title="📊 Live Stock Tracker", layout="wide")

st.title("📈 Live Stock Tracker")

ticker_symbol = st.text_input("Enter Stock Symbol (e.g. AAPL):", "AAPL").upper()

interval = "1m"  # 1-minute interval
lookback_limit = 30  # How many ticks (price points) to remember
fetch_interval = 5  # Seconds between updates

price_history = []

# Emoji rules
def get_movement_emoji(pct_change):
    if pct_change >= 1.0:
        return "🚀 Strong Surge"
    elif pct_change >= 0.5:
        return "📊 Mild Rise"
    elif pct_change <= -1.0:
        return "📉 Sharp Drop"
    elif pct_change <= -0.5:
        return "⚠️ Mild Drop"
    return ""

# Fetch data
def fetch_data(symbol):
    try:
        df = yf.download(tickers=tickers, period="1d", interval=interval, progress=False)
        df = df.reset_index()
        df = df.rename(columns=lambda x: x.strip())
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Candlestick chart
def plot_candlestick(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df["Datetime"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"]
    )])
    fig.update_layout(
        title="Candlestick Chart",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False
    )
    return fig

# Live UI
price_placeholder = st.empty()
alerts_placeholder = st.empty()
chart_placeholder = st.empty()

while True:
    df = fetch_data(ticker_symbol)
    if df is not None and not df.empty:
        latest = df.iloc[-1]
        current_price = latest["Close"]
        current_time = latest["Datetime"]

        price_history.append((current_time, current_price))
        if len(price_history) > lookback_limit:
            price_history.pop(0)

        price_placeholder.markdown(f"### 💰 {ticker_symbol} Current Price: **${current_price:.2f}**")

        # Check movement
        movements = []
        for i in range(1, min(5, len(price_history))):
            past_time, past_price = price_history[-i - 1]
            pct_change = ((current_price - past_price) / past_price) * 100
            emoji = get_movement_emoji(pct_change)
            if emoji:
                movements.append(f"{past_time.strftime('%H:%M:%S')} → {current_time.strftime('%H:%M:%S')} | {pct_change:.2f}% {emoji}")

        if movements:
            alerts_placeholder.markdown("#### Significant Movement:")
            for m in movements:
                alerts_placeholder.markdown(m)

        chart_placeholder.plotly_chart(plot_candlestick(df), use_container_width=True)

    time.sleep(fetch_interval)
