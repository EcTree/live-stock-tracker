import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import numpy as np

st.title("📈 Live Stock Tracker (Advanced Edition)")

# Candle interval selector (major improvement)
interval = st.selectbox(
    "Select Candle Interval:",
    ["1m", "2m", "5m", "15m", "30m", "60m"],
    index=2  # default = 5m
)

ticker = st.text_input("Enter a stock symbol (e.g., AAPL):", "AAPL").upper()

def get_data(ticker):
    try:
        data = yf.download(ticker, period="1d", interval=interval)
        data = data.reset_index()

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# RSI function
def calc_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# MACD function
def calc_macd(close):
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def detect_patterns(df):
    patterns = []
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ==== Candlestick Patterns ====

    # Bullish engulfing
    if (last["Close"] > last["Open"] and prev["Close"] < prev["Open"]
        and last["Close"] > prev["Open"] and last["Open"] < prev["Close"]):
        patterns.append(("🚀 Bullish Engulfing", "UP"))

    # Bearish engulfing
    if (last["Close"] < last["Open"] and prev["Close"] > prev["Open"]
        and last["Open"] > prev["Close"] and last["Close"] < prev["Open"]):
        patterns.append(("📉 Bearish Engulfing", "DOWN"))

    # Hammer
    body = abs(last["Close"] - last["Open"])
    range_ = last["High"] - last["Low"]
    lower_shadow = min(last["Open"], last["Close"]) - last["Low"]

    if body < range_ * 0.3 and lower_shadow > body * 2:
        patterns.append(("🔨 Hammer", "UP"))

    # Shooting star
    upper_shadow = last["High"] - max(last["Open"], last["Close"])
    if body < range_ * 0.3 and upper_shadow > body * 2:
        patterns.append(("🌠 Shooting Star", "DOWN"))

    # Doji
    if body < range_ * 0.1:
        patterns.append(("➕ Doji", "NEUTRAL"))

    if not patterns:
        return [("No patterns detected", "NEUTRAL")]

    return patterns


# Fetch + Process Data
if ticker:
    df = get_data(ticker)

    if df is not None and not df.empty:

        # Add indicators
        df["RSI"] = calc_rsi(df["Close"])
        df["MACD"], df["Signal"] = calc_macd(df["Close"])

        st.subheader(f"{ticker} Data ({interval} interval)")
        st.dataframe(df.tail())

        # Chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['Datetime'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])
        fig.update_layout(xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

        # 🔎 Pattern Detection
        st.subheader("Pattern Detection & Signal Strength")

        found = detect_patterns(df)
        last = df.iloc[-1]

        for name, direction in found:
            rsi = last["RSI"]
            macd = last["MACD"]
            signal = last["Signal"]

            strength = 50

            # RSI influence
            if direction == "UP" and rsi > 50:
                strength += 20
            if direction == "DOWN" and rsi < 50:
                strength += 20

            # MACD influence
            if direction == "UP" and macd > signal:
                strength += 20
            if direction == "DOWN" and macd < signal:
                strength += 20

            # Clamp 0–100
            strength = max(0, min(100, strength))

            st.write(f"**{name}** → Direction: **{direction}** → Strength: **{strength}%**")

        # Manual refresh
        if st.button("🔄 Refresh Now"):
            st.rerun()

        # Auto refresh
        time.sleep(60)
        st.rerun()
