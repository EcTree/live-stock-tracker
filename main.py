import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pytz

st.title("📈 Live Stock Tracker")

symbol = st.text_input("Enter a stock symbol (e.g. AAPL):")

if symbol:
    # Check if market is open
    eastern = pytz.timezone("US/Eastern")
    now_est = https://linkprotect.cudasvc.com/url?a=https%3a%2f%2fdatetime.now&c=E,1,FN16rZiQy_NRl9eg0-ii8HD52q5aj1C2Fuv2fzdH8NfO3mHNpAYbU-llXILMRYN_5YaeAB4zSNqJTIlS33dhMHSkfR32n0C7ygZaI1i8U2CoG-DVb-E,&typo=1(eastern)
    market_open = now_est.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_est.replace(hour=16, minute=0, second=0, microsecond=0)

    if market_open <= now_est <= market_close:
        interval = "1m"
        period = "1d"
    else:
        interval = "1d"
        period = "1mo"

    try:
        df = yf.download(
            tickers=symbol,
            interval=interval,
            period=period,
            progress=False,
        )

        st.write(df)  # Show the data

        if not df.empty:
            fig = go.Figure(
                data=go.Candlestick(
                    x=df.index,
                    open=df["Open"],
                    high=df["High"],
                    low=df["Low"],
                    close=df["Close"]
                )
            )

            fig.update_layout(
                title=f"{symbol.upper()} Candlestick Chart ({interval})",
                xaxis_rangeslider_visible=False
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning(
                f"No data found for {symbol.upper()}. "
                f"The market might be closed or the symbol is invalid."
            )
    except Exception as e:
        st.error(f"Error fetching data: {e}")
