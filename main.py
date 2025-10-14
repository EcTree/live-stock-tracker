import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Live Stock Tracker", layout="wide")

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="data_refresh")

st.title("📈 Live Stock Tracker")

symbol = st.text_input("Enter a stock symbol (e.g. AAPL):")

if symbol:
    try:
        df = yf.download(
            symbol,
            interval="1m",
            period="1d",
            progress=False
        )

        if df.empty:
            st.warning("No data found. The market might be closed right now, or the symbol is invalid.")
        else:
            # Fix for multi-index columns (sometimes happens with yfinance)
            if isinstance(df.columns[0], tuple):
                df.columns = [col[1] for col in df.columns]

            st.subheader(f"{symbol.upper()} Data (1-Minute Interval)")
            st.dataframe(df.tail(10))  # Show latest 10 rows for clarity

            # Create candlestick chart
            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=df.index,
                        open=df["Open"],
                        high=df["High"],
                        low=df["Low"],
                        close=df["Close"],
                    )
                ]
            )
            fig.update_layout(
                title=f"{symbol.upper()} Candlestick Chart (1m)",
                xaxis_title="Time",
                yaxis_title="Price (USD)",
                xaxis_rangeslider_visible=False,
            )
            st.plotly_chart(fig, use_container_width=True)

            # ===============================
            # 🔎 CANDLESTICK PATTERN DETECTION
            # ===============================
            st.subheader("Candlestick Pattern Detector")

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

            detected = detect_patterns(df)
            for p in detected:
                st.write(p)

    except Exception as e:
        st.error(f"Error fetching data: {e}")

else:
   sf.info("Please enter a stock symbol above.")
