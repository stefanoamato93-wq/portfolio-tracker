import streamlit as st
import pandas as pd




# Example dummy data
data = {
    "Instrument": ["AAPL", "MSFT", "BTC-USD"],
    "Quantity": [10, 5, 0.01],
    "Price": [180, 320, 25000],
}
df = pd.DataFrame(data)
df["Value"] = df["Quantity"] * df["Price"]

st.title("Portfolio")
st.subheader("Portfolio Total Value")
st.metric("Total", f"${df['Value'].sum():,.2f}")
st.subheader("Holdings")
st.dataframe(df)

