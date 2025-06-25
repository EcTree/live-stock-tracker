import streamlit as st
import plotly.graph_objects as go
import datetime
import time
import finnhub

# ⚠️ Replace this with your actual API key
finnhub_key = "d0qc4k1r01qt60onfn00d0qc4k1r01qt60onfn0g"
finnhub_client = finnhub.Client(api_key=finnhub_key)

# Get stock data (candles)
def   get_candlestick_data(symbol, resolution='1', count=30):
      now = int(time.time())
      past = now - count * 60 # 60 minutes back if resolution is 1 minute
      candles = finnhub_client.stock_candles(symbol, resolution, past, now)
      return candles

# Streamlit app
st.title("📉 Live Candlestick Chart")

symbol = st.text_input("Enter stock symbol (e.g. AAPL, TSLA)", value="AAPL").upper()

if symbol:
data = get_candlestick_data(symbol)

if data and data['s'] == 'ok':
# Convert timestamps to datetime
timestamps = [datetime.datetime.fromtimestamp(ts) for ts in data['t']]

fig = go.Figure(data=[go.Candlestick(
x=timestamps,
open=data['o'],
high=data['h'],
low=data['l'],
close=data['c']
)])

fig.update_layout(
title=f"{symbol} - Candlestick Chart",
xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)
else:
st.error("Failed to fetch data. Try a different stock symbol.")
