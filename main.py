import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="datarefresh")

# Streamlit page config
st.set_page_config(page_title="Live Stock Tracker", layout="wide")
st.title("📈 Live Stock Tracker")

# User input for stock symbol
symbol = st.text_input("Enter a stock symbol (e.g. AAPL):")

if symbol:
    try:
        # Download 1-minute interval data for today
        df = yf.download(
            tickers=symbol,
            interval="1m",
            period="1d",
            progress=False
        )

        if df.empty:
            st.warning("No data found. The market might be closed right now, or the symbol is invalid.")
        else:
            # 🧹 Clean up possible multi-index or duplicate column names
            if isinstance(df.columns[0], tuple):
                df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]
            if df.columns.duplicated().any():
                df = df.loc[:, ~df.columns.duplicated()]

            # Show the data table
            st.subheader(f"{symbol.upper()} Data (1-Minute Interval)")
            st.dataframe(df)

            # Plot candlestick chart
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
                yaxis=dict(fixedrange=False, autorange=True),  # Ensure candles are visible
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
else:
    st.info("Please enter a stock symbol above.")
