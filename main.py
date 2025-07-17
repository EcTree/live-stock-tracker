import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(page_title="📊 Stock Tracker", layout="wide")

st.title("📈 Live Stock Tracker")

ticker_symbol = st.text_input("Enter Stock Symbol (e.g. AAPL):", "AAPL").upper()

interval = "1m"  # One-minute interval
lookback_minutes = 5  # Total minutes of data to keep in memory
fetch_interval = 5  # Seconds between fetches

# Store price history
price_history = []

# Emoji thresholds
def get_movement_emoji(pct_change):
    if pct_change >= 1.0:
        return "🚀 Strong Surge"
    elif pct_change >= 0.5:
        return "📊 Mild Rise"
    elif pct_change <= -1.0:
        return "📉 Sharp Drop"
    elif pct_change <= -0.5:
        return "⚠️ Mild Drop"
    else:
        return ""

# Fetch latest price
def fetch_latest_price(ticker):
    try:
        df = yf.download(tickers=tickers, period="1d", interval=interval, progress=False)
        df = df.reset_index()
        df = df.rename(columns=lambda x: x.strip())
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Plot candlestick chart
def plot_candles(df):
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

# Main loop
placeholder = st.empty()
chart_placeholder = st.empty()

while True:
    data = fetch_latest_price(ticker_symbol)
    if data is not None and not data.empty:
        latest_row = data.iloc[-1]
        current_price = latest_row["Close"]
        current_time = latest_row["Datetime"]

        price_history.append((current_time, current_price))
        if len(price_history) > 30:
            price_history.pop(0)

        # Calculate change from earlier prices
        display_lines = []
        for i in range(1, min(5, len(price_history)) + 1):
            past_time, past_price = price_history[-i - 1]
            pct_change = ((current_price - past_price) / past_price) * 100
            emoji = get_movement_emoji(pct_change)
            if emoji:
                line = f"{past_time.strftime('%H:%M:%S')} → {current_time.strftime('%H:%M:%S')} | {pct_change:.2f}% {emoji}"
                display_lines.append(line)

        with placeholder.container():
            st.markdown(f"### 💰 {ticker_symbol} Current Price: **${current_price:.2f}**")
            if display_lines:
                st.markdown("#### Significant Movement:")
                for line in display_lines:
                    st.markdown(line)

        with chart_placeholder.container():
            st.plotly_chart(plot_candles(data), use_container_width=True)

    time.sleep(fetch_interval)
