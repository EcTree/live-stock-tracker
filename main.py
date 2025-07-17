import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Live Stock Tracker", layout="wide")
st.title("📈 Live Stock Tracker")

symbol = st.text_input("Enter a stock symbol (e.g. AAPL):")

if symbol:
    try:
        # Fetch data
        df = yf.download(
        tickers=symbol,
        interval="1m",
        period="1d",
        progress=False
        )

        if df.empty:
            st.warning("No data found. The market might be closed right now, or the symbol is invalid.")
        else:
            
            # Fix for multi-index or duplicate columns
if isinstance(df.columns[0], tuple):
    df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]
elif df.columns.duplicated().any():
    df = df.loc[:, ~df.columns.duplicated()]

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
            )
            st.plotly_chart(fig, use_container_width=True)

            # 💰 Current price
            current_price = df["Close"].iloc[-1]
            st.markdown(f"### 💰 Current Price: ${current_price:.2f}")

            # 📊 Compare to price 5 ticks ago (5 minutes ago)
            if len(df) >= 6:
                past_price = df["Close"].iloc[-6]
                pct_change = ((current_price - past_price) / past_price) * 100

                # Emoji alert system
                def get_emoji(change):
                    if change >= 1.0:
                        return "🚀 Strong Surge"
                    elif change >= 0.5:
                        return "📊 Mild Rise"
                    elif change <= -1.0:
                        return "📉 Sharp Drop"
                    elif change <= -0.5:
                        return "⚠️ Mild Drop"
                    return ""

                emoji_alert = get_emoji(pct_change)
                if emoji_alert:
                    st.markdown(f"### {pct_change:.2f}% {emoji_alert}")

    except Exception as e:
        st.error(f"Error fetching data: {e}")
else:
    st.info("Please enter a stock symbol above.")
