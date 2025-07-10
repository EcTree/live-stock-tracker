import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Live Stock Tracker")

st.title("📈 Live Stock Tracker")

symbol = st.text_input("Enter a stock symbol (e.g. AAPL):")

if symbol:
    try:
        df = yf.download(
            tickers=symbol,
            interval="5m",
            period="5d",
            progress=False,
        )

        if not df.empty:
            fig = go.Figure(data=go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"]
            ))

            fig.update_layout(
                title=f"{symbol.upper()} - 1m Candlestick Chart",
                xaxis_rangeslider_visible=False
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found. The market might be closed, or the symbol is invalid.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
else:
   st.info("Enter a stock symbol to view the chart.")
