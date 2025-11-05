import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(page_title="📈 Live Stock Tracker", layout="wide")
st.title("📈 Live Stock Tracker")

# Input box for ticker
ticker = st.text_input("Enter a stock symbol (e.g., AAPL):", "AAPL").upper()

def get_data(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m")
        data = data.reset_index()

        # Flatten multi-index columns if they exist
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Candlestick pattern detector (25 patterns)
def detect_patterns(df):
    patterns = []

    if len(df) < 3:
        return ["Not enough data to detect patterns."]

    last = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3]

    body = abs(last["Close"] - last["Open"])
    candle_range = last["High"] - last["Low"]
    lower_shadow = min(last["Open"], last["Close"]) - last["Low"]
    upper_shadow = last["High"] - max(last["Open"], last["Close"])

    # ======================
    # 1-CANDLE PATTERNS
    # ======================
    if body < (candle_range * 0.1):
        patterns.append("➕ Doji — Market indecision ⚪")

    if body < candle_range * 0.3 and lower_shadow > body * 2:
        patterns.append("🔨 Hammer — Possible bullish reversal 🚀")

    if body < candle_range * 0.3 and upper_shadow > body * 2:
        patterns.append("🌠 Shooting Star — Possible bearish reversal 📉")

    if body > candle_range * 0.6 and last["Close"] > last["Open"]:
        patterns.append("🟢 Marubozu (Bullish) — Strong uptrend 🚀")

    if body > candle_range * 0.6 and last["Close"] < last["Open"]:
        patterns.append("🔴 Marubozu (Bearish) — Strong downtrend 📉")

    if lower_shadow > upper_shadow * 2 and body < candle_range * 0.3:
        patterns.append("🕯 Hanging Man — Bearish reversal risk 📉")

    if upper_shadow > lower_shadow * 2 and body < candle_range * 0.3:
        patterns.append("🎯 Inverted Hammer — Bullish reversal potential 🚀")

    # ======================
    # 2-CANDLE PATTERNS
    # ======================
    if (
        last["Close"] > last["Open"]
        and prev["Close"] < prev["Open"]
        and last["Close"] > prev["Open"]
        and last["Open"] < prev["Close"]
    ):
        patterns.append("🚀 Bullish Engulfing — Likely rise")

    if (
        last["Close"] < last["Open"]
        and prev["Close"] > prev["Open"]
        and last["Open"] > prev["Close"]
        and last["Close"] < prev["Open"]
    ):
        patterns.append("📉 Bearish Engulfing — Likely fall")

    if last["Close"] > prev["Close"] and last["Open"] > prev["Open"]:
        patterns.append("📊 Rising Candle Pair — Mild upward trend 🚀")

    if last["Close"] < prev["Close"] and last["Open"] < prev["Open"]:
        patterns.append("⚠️ Falling Candle Pair — Mild downward trend 📉")

    # Piercing Line
    if (
        prev["Close"] < prev["Open"]
        and last["Open"] < prev["Low"]
        and last["Close"] > (prev["Open"] + prev["Close"]) / 2
    ):
        patterns.append("📈 Piercing Line — Bullish reversal 🚀")

    # Dark Cloud Cover
    if (
        prev["Close"] > prev["Open"]
        and last["Open"] > prev["High"]
        and last["Close"] < (prev["Open"] + prev["Close"]) / 2
    ):
        patterns.append("☁️ Dark Cloud Cover — Bearish reversal 📉")

    # ======================
    # 3-CANDLE PATTERNS
    # ======================
    if (
        prev2["Close"] < prev2["Open"]
        and prev["Close"] < prev["Open"]
        and last["Close"] > last["Open"]
        and last["Close"] > prev["Open"]
    ):
        patterns.append("🌅 Morning Star — Strong bullish reversal 🚀")

    if (
        prev2["Close"] > prev2["Open"]
        and prev["Close"] > prev["Open"]
        and last["Close"] < last["Open"]
        and last["Close"] < prev["Open"]
    ):
        patterns.append("🌇 Evening Star — Strong bearish reversal 📉")

    # Three White Soldiers
    if (
        last["Close"] > last["Open"]
        and prev["Close"] > prev["Open"]
        and prev2["Close"] > prev2["Open"]
        and last["Close"] > prev["Close"] > prev2["Close"]
    ):
        patterns.append("⚪ Three White Soldiers — Bullish continuation 🚀")

    # Three Black Crows
    if (
        last["Close"] < last["Open"]
        and prev["Close"] < prev["Open"]
        and prev2["Close"] < prev2["Open"]
        and last["Close"] < prev["Close"] < prev2["Close"]
    ):
        patterns.append("⚫ Three Black Crows — Bearish continuation 📉")

    # Rising Three Methods
    if (
        prev2["Close"] < prev2["Open"]
        and prev["Close"] > prev["Open"]
        and last["Close"] > prev2["Close"]
    ):
        patterns.append("📈 Rising Three — Bullish continuation 🚀")

    # Falling Three Methods
    if (
        prev2["Close"] > prev2["Open"]
        and prev["Close"] < prev["Open"]
        and last["Close"] < prev2["Close"]
    ):
        patterns.append("📉 Falling Three — Bearish continuation 📉")

    if not patterns:
        patterns.append("No clear patterns found in the latest candles.")

    return patterns

# Fetch and display
if ticker:
    data = get_data(ticker)

    if data is not None and not data.empty:
        st.subheader(f"{ticker} Data (1-Minute Interval)")
        st.dataframe(data.tail())

        st.subheader(f"{ticker} Candlestick Chart (1m)")
        fig = go.Figure(data=[go.Candlestick(
            x=data["Datetime"],
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"]
        )])
        fig.update_layout(xaxis_rangeslider_visible=False, height=500, width=900)
        st.plotly_chart(fig, use_container_width=True)

        # Pattern detection
        st.subheader("🔎 Candlestick Pattern Detector")
        detected = detect_patterns(data)
        for p in detected:
            st.write(p)

        # Refresh section
        if st.button("🔄 Refresh Now"):
            st.rerun()

        time.sleep(60)
        st.rerun()
    else:
        st.warning("No data available for this ticker.")
