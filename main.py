import streamlit as st
import finnhub
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Finnhub client
api_key = "YOUR_FINNHUB_API_KEY"
finnhub_client = finnhub.Client(api_key=api_key)

# Streamlit UI
st.title("📈 Live Stock Tracker")

symbol = "AAPL"  # Change this to your desired stock
st.write(f"Tracking live price for: **{symbol}**")

# Storage for previous prices
price_history = []

# Function to fetch current price
def get_current_price(symbol):
    quote = finnhub_client.quote(symbol)
    return quote['c']  # Current price

# Function to fetch historical candles
def get_candles(symbol, resolution='1', lookback_minutes=60):
    end_time = int(datetime.utcnow().timestamp())
    start_time = end_time - lookback_minutes * 60
    candles = finnhub_client.stock_candles(symbol, resolution, start_time, end_time)

    if candles and candles.get("s") == "ok":
        return candles
    else:
        return None

# Draw candlestick chart
def plot_candlestick(candles):
    fig = go.Figure(data=[
        go.Candlestick(
            x=[datetime.utcfromtimestamp(t) for t in candles['t']],
            open=candles['o'],
            high=candles['h'],
            low=candles['l'],
            close=candles['c']
        )
    ])
    fig.update_layout(title=f"Candlestick Chart for {symbol}",
                      xaxis_title="Time (UTC)",
                      yaxis_title="Price ($)",
                      height=500)
    st.plotly_chart(fig)

# Get historical candles once
candles_data = get_candles(symbol)
if candles_data:
    plot_candlestick(candles_data)
else:
    st.warning("No candle data available.")

# Live price loop
placeholder = st.empty()

while True:
    price = get_current_price(symbol)
    price_history.append(price)

    # Only keep last 30 ticks
    price_history = price_history[-30:]

    message = f"💰 Live Price: **${price:.2f}**"

    if len(price_history) >= 2:
        # Compare to price 20 seconds ago (or the oldest available)
        compare_price = price_history[0]
        pct_change = ((price - compare_price) / compare_price) * 100

        # Check thresholds
        if pct_change >= 1.0:
            message += f" 🚀 **Strong Surge (+{pct_change:.2f}%)**"
        elif pct_change >= 0.5:
            message += f" 📊 **Mild Rise (+{pct_change:.2f}%)**"
        elif pct_change <= -1.0:
            message += f" 📉 **Sharp Drop ({pct_change:.2f}%)**"
        elif pct_change <= -0.5:
            message += f" ⚠️ **Mild Drop ({pct_change:.2f}%)**"

    placeholder.markdown(message)
    time.sleep(5)
