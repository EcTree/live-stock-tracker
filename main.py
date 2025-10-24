
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime

st.set_page_config(page_title="📈 Live Stock Tracker", layout="wide")
st.title("📊 Live Stock Tracker with Candlestick Pattern Detection")

# Input box for ticker
ticker = st.text_input("Enter a stock symbol (e.g., AAPL):", "AAPL").upper()

# Store last detected pattern in session to only show new alerts
if "last_pattern_time" not in st.session_state:
  st.session_state.last_pattern_time = None

def get_data(ticker):
  try:
      data = yf.download(ticker, period="1d", interval="1m")
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
    return patterns
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3]
    
    body = abs(last["Close"] - last["Open"])
    candle_range = last["High"] - last["Low"]
    upper_shadow = last["High"] - max(last["Close"], last["Open"])
    lower_shadow = min(last["Close"], last["Open"]) - last["Low"]
    
    # Bullish Engulfing
    if (
        last["Close"] > last["Open"]
        and prev["Close"] < prev["Open"]
        and last["Close"] > prev["Open"]
        and last["Open"] < prev["Close"]
    ):
        patterns.append(("🚀 Bullish Engulfing", "Possible Uptrend Reversal"))
    
    # Bearish Engulfing
    if (
        last["Close"] < last["Open"]
        and prev["Close"] > prev["Open"]
        and last["Open"] > prev["Close"]
        and last["Close"] < prev["Open"]
    ):
        patterns.append(("📉 Bearish Engulfing", "Possible Downtrend Reversal"))
    
    # Hammer
    if body < candle_range * 0.3 and lower_shadow > body * 2:
        patterns.append(("🔨 Hammer", "Bullish Reversal"))
    
    # Shooting Star
    if body < candle_range * 0.3 and upper_shadow > body * 2:
        patterns.append(("🌠 Shooting Star", "Bearish Reversal"))
    
    # Doji
    if body < (candle_range * 0.1):
        patterns.append(("➕ Doji", "Market Indecision"))
    
    # Morning Star
    if (
        prev2["Close"] < prev2["Open"]
        and abs(prev["Close"] - prev["Open"]) < (prev2["Open"] - prev2["Close"]) * 0.5
        and last["Close"] > prev2["Open"]
    ):
        patterns.append(("🌅 Morning Star", "Bullish Reversal"))
    
    # Evening Star
    if (
        prev2["Close"] > prev2["Open"]
        and abs(prev["Close"] - prev["Open"]) < (prev2["Close"] - prev2["Open"]) * 0.5
        and last["Close"] < prev2["Open"]
    ):
        patterns.append(("🌇 Evening Star", "Bearish Reversal"))
    
    # Three White Soldiers
    if (
        df["Close"].iloc[-3] > df["Open"].iloc[-3]
        and df["Close"].iloc[-2] > df["Open"].iloc[-2]
        and df["Close"].iloc[-1] > df["Open"].iloc[-1]
    ):
        patterns.append(("⚪ Three White Soldiers", "Strong Bullish Continuation"))
    
    # Three Black Crows
    if (
        df["Close"].iloc[-3] < df["Open"].iloc[-3]
        and df["Close"].iloc[-2] < df["Open"].iloc[-2]
        and df["Close"].iloc[-1] < df["Open"].iloc[-1]
    ):
        patterns.append(("⚫ Three Black Crows", "Strong Bearish Continuation"))
    
    # Piercing Line
    if (
        prev["Close"] < prev["Open"]
        and last["Open"] < prev["Low"]
        and last["Close"] > (prev["Close"] + (prev["Open"] - prev["Close"]) / 2)
    ):
        patterns.append(("📈 Piercing Line", "Bullish Reversal"))
    
    # Dark Cloud Cover
    if (
        prev["Close"] > prev["Open"]
        and last["Open"] > prev["High"]
        and last["Close"] < (prev["Open"] + (prev["Close"] - prev["Open"]) / 2)
    ):
        patterns.append(("☁️ Dark Cloud Cover", "Bearish Reversal"))
    
    return patterns


# Fetch and display data
if ticker:
    data = get_data(ticker)

    if data is not None and not data.empty:
        st.subheader(f"{ticker} Data (1-Minute Interval)")
        st.dataframe(data.tail())

        # Candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=data["Datetime"],
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"]
        )])
        fig.update_layout(
            title=f"{ticker} Candlestick Chart (1m)",
            xaxis_rangeslider_visible=False,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🧠 Pattern Detector Active")
        st.caption(f"Last checked: {datetime.now().strftime('%H:%M:%S')}")

        patterns = detect_patterns(data)

        if patterns:
            # Only show if new pattern
            last_time = data["Datetime"].iloc[-1]
            if st.session_state.last_pattern_time != last_time:
                st.session_state.last_pattern_time = last_time
                for pattern, meaning in patterns:
                    st.success(f"**{pattern}** — {meaning} at {last_time.strftime('%H:%M:%S')}")
            else:
                st.info("No new patterns detected.")
        else:
            st.info("No clear patterns found in the latest candles.")

        # Auto refresh every 60s
        time.sleep(60)
        st.rerun()
    else:
        st.warning("No data available for this ticker.")
