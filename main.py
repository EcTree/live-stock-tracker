import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

st.title("📈 Live Stock Tracker")

# Input box for ticker
ticker = st.text_input("Enter a stock symbol (e.g., AAPL):", "AAPL").upper()

def get_data(ticker):
    try:
        data = yf.download (ticker, period="1d", interval="1m")
        data = data.reset_index()

        # ✅ Flatten multi-index columns if they exist
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Function to detect candlestick patterns
def detect_patterns(df):
    patterns = []

    if len(df) < 3:
        return ["Not enough data to detect patterns."]

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Bullish Engulfing
    if (
        last["Close"] > last["Open"]
        and prev["Close"] < prev["Open"]
        and last["Close"] > prev["Open"]
        and last["Open"] < prev["Close"]
    ):
        patterns.append("🚀 Bullish Engulfing - Possible Uptrend Reversal")

    # Bearish Engulfing
    elif (
        last["Close"] < last["Open"]
        and prev["Close"] > prev["Open"]
        and last["Open"] > prev["Close"]
        and last["Close"] < prev["Open"]
    ):
        patterns.append("📉 Bearish Engulfing - Possible Downtrend Reversal")

    # Hammer
    body = abs(last["Close"] - last["Open"])
    candle_range = last["High"] - last["Low"]
    lower_shadow = (
        last["Open"] - last["Low"]
        if last["Close"] > last["Open"]
        else last["Close"] - last["Low"]
    )

    if body < candle_range * 0.3 and lower_shadow > body * 2:
        patterns.append("🔨 Hammer - Possible Bullish Reversal")

    # Shooting Star
    upper_shadow = (
        last["High"] - last["Close"]
        if last["Close"] < last["Open"]
        else last["High"] - last["Open"]
    )
    if body < candle_range * 0.3 and upper_shadow > body * 2:
        patterns.append("🌠 Shooting Star - Possible Bearish Reversal")

    # Doji
    if body < (candle_range * 0.1):
        patterns.append("➕ Doji - Market Indecision")

    if not patterns:
        patterns.append("No clear patterns found in the latest candle.")

    return patterns

# Fetch data
if ticker:
    data = get_data(ticker)

    if data is not None and not data.empty:
        st.subheader(f"{ticker} Data (1-Minute Interval)")
        st.dataframe(data.tail())

        # ✅ Candlestick chart
        st.subheader(f"{ticker} Candlestick Chart (1m)")
        fig = go.Figure(data=[go.Candlestick(
            x=data['Datetime'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        )])
        fig.update_layout(xaxis_rangeslider_visible=False, height=500, width=900)
        st.plotly_chart(fig, use_container_width=True)

        # ✅ Pattern detection
        st.subheader("Candlestick Pattern Detector")
        detected = detect_patterns(data)
        for p in detected:
            st.write(p)

        # ✅ Refresh button
        if st.button("🔄 Refresh Now"):
            st.rerun()

        # ✅ Auto refresh every 60 seconds
        time.sleep(60)
        st.rerun()
    else:
        st.warning("No data available for this ticker.")
