import streamlit as st
import time
import finnhub
from collections import deque

# Finnhub client
finnhub_client = finnhub.Client(api_key="d0qc4k1r01qt60onfn00d0qc4k1r01qt60onfn0g")

# Streamlit setup
st.set_page_config(layout="wide")
st.title(" Live Stock Tracker")

# Settings
symbol = "AAPL"
update_interval = 5  # seconds
history_limit = 30

# History queue
price_history = deque(maxlen=history_limit)

# Main loop
placeholder = st.empty()

while True:
    quote = finnhub_client.quote(symbol)
    price = quote["c"]
    price_history.append(price)

    with placeholder.container():
        st.markdown(f"💰 **{price:.2f} USD**")
        if len(price_history) >= 2:
            change = ((price_history[-1] - price_history[0]) / price_history[0]) * 100
            emoji = "🚀" if change >= 1 else "📊" if change >= 0.5 else "⚠️" if change <= -0.5 else "📉" if change <= -1 else ""
            st.markdown(f"**{emoji} {change:+.2f}% over last {len(price_history)} ticks**")
        st.line_chart(list(price_history))

    time.sleep(update_interval)
