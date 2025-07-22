import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Live Stock Tracker", layout="wide")
st.title("📈 Live Stock Tracker")

symbol = st.text_input("Enter a stock symbol (e.g. AAPL):")

if symbol:
    try:
        df = yf.download(
            tickers=symbol,
            period="1d",
            interval="1m",
            progress=False
        )

        if df.empty:
            st.warning("No data found. The market might be closed right now, or the symbol is invalid.")
        else:
            # ✅ FIX: If data is nested under the ticker name (e.g. df["AAPL"]), extract it
            if symbol.upper() in df.columns.get_level_values(0):
                df = df[symbol.upper()]  # unnest the dataframe

            # ✅ Remove duplicate columns if any remain
            df = df.loc[:, ~df.columns.duplicated()]

            st.subheader(f"{symbol.upper()} Data (1-Minute Interval)")
            st.dataframe(df)

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

    except Exception as e:
        st.error(f"Error fetching data: {e}")
else:
   st.info("Please enter a stock symbol above.")
