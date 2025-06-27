import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import finnhub

# Your Finnhub API key
api_key = "d0qc4k1r01qt60onfn00d0qc4k1r01qt60onfn0g"  # ← replace this with your real key

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key=api_key)

# Function to get candlestick data
def get_candles(symbol, resolution='5', lookback_minutes=30):
    try:
        end_time = int(datetime.utcnow().timestamp())
        start_time = end_time - lookback_minutes * 60

        candles = finnhub_client.stock_candles(
            symbol,
            resolution,
            start_time,
            end_time
        )

        if candles and candles.get("s") == "ok":
            return candles
        else:
            st.error(f"Finnhub returned error: {candles}")
            return None

    except Exception as e:
        st.error(f"Exception from Finnhub: {e}")
        return None

# Streamlit App
st.title("📈 Live Stock Tracker")

symbol = st.text_input("Enter a stock symbol:", value="AAPL")

if symbol:
    candles_data = get_candles(symbol)

    if candles_data:
        # Prepare data for candlestick chart
        times = [datetime.fromtimestamp(ts) for ts in candles_data["t"]]

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=times,
                    open=candles_data["o"],
                    high=candles_data["h"],
                    low=candles_data["l"],
                    close=candles_data["c"]
                )
            ]
        )
        fig.update_layout(
            title=f"{symbol.upper()} - Candlestick Chart",
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(...)
        
