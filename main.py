import streamlit as st
import plotly.graph_objects as go
import finnhub
from datetime import datetime
import time

# Finnhub API setup
api_key = 'd0qc4k1r01qt60onfn00d0qc4k1r01qt60onfn0g'  # replace with your actual key
finnhub_client = finnhub.Client(api_key=api_key)

# Get stock data (candles)
def get_candlestick_data(symbol, resolution='1', count=30):
    now = int(time.time())
    past = now - count * 60  # 30 minutes back if resolution is 1-minute
    candles = finnhub_client.stock_candles(symbol, resolution, past, now)
    return candles

# Streamlit app
st.title("📊 Live Candlestick Chart")

symbol = st.text_input("Enter stock symbol (e.g. AAPL)", value="AAPL")

if st.button("Load Candlestick Chart"):
    data = get_candlestick_data(symbol.upper())
import plotly.graph_objects as go

...

fig = go.Figure(data=[go.Candlestick(
    x=df['time'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close']
)])
st.plotly_chart(fig)

    if data and data['s'] == 'ok':
        fig = go.Figure(data=[go.Candlestick(
            x=[datetime.fromtimestamp(ts) for ts in data['t']],
            open=data['o'],
            high=data['h'],
            low=data['l'],
            close=data['c']
        )])
        fig.update_layout(title=f'{symbol.upper()} - Candlestick Chart', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Failed to fetch data. Try a different stock symbol.")
