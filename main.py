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
        data = yf.download( ticker, period="1d", interval="1m")
        data = data.reset_index()
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Fetch data
if ticker:
    data = get_data(ticker)

    if data is not None and not data.empty:
        st.subheader(f"{ticker} Data (1-Minute Interval)")
        st.dataframe(data.tail())

        # Candlestick chart
        st.subheader(f"{ticker} Candlestick Chart (1m)")
        fig = go.Figure(data=[go.Candlestick(
            x=data['Datetime'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        )])
        fig.update_layout(xaxis_rangeslider_visible=False, height=500, width=900)
        st.plotly_chart(fig)

        # Refresh button
        if st.button("🔄 Refresh Now"):
            st.experimental_rerun()

        # Auto refresh every 60 seconds
        time.sleep(60)
        st.experimental_rerun()
    else:
        st.warning("No data available for this ticker.")
