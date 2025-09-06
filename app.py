import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.title("Portfolio Tracker")

# Initialize portfolio and form visibility in session state
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

if "show_form" not in st.session_state:
    st.session_state.show_form = False

# -----------------------
# Add button to show form
# -----------------------
if st.button("+ Add Holding"):
    st.session_state.show_form = True

# -----------------------
# User input form (conditionally shown)
# -----------------------
if st.session_state.show_form:
    st.subheader("Add a new holding")
    
    # Add a container for the form
    with st.form("add_holding_form"):
        isin = st.text_input("ISIN")
        quantity = st.number_input("Amount of shares", min_value=0.0, value=0.0, step=1.0)
        price = st.number_input("Price of purchase (per share)", min_value=0.0, value=0.0, step=0.01)
        purchase_date = st.date_input("Date of purchase", value=date.today())
        
        submitted = st.form_submit_button("Add to portfolio")
    
    # Cancel button outside the form
    if st.button("Cancel"):
        st.session_state.show_form = False
        st.info("Form canceled")
    
    # Process submission
    if submitted and isin and quantity > 0 and price > 0:
        st.session_state.portfolio.append({
            "ISIN": isin,
            "Quantity": quantity,
            "Price": price,
            "Date": purchase_date
        })
        st.session_state.show_form = False

# -----------------------
# Build DataFrame and display
# -----------------------
if st.session_state.portfolio:
    df = pd.DataFrame(st.session_state.portfolio)
    df["Value"] = df["Quantity"] * df["Price"]

    # Show total portfolio value
    st.metric("Total Value", f"${df['Value'].sum():,.2f}")

    # Show holdings table
    st.subheader("Holdings")
    st.dataframe(df)

    # Pie chart
    st.subheader("Portfolio Allocation")
    fig = px.pie(df, names="ISIN", values="Value", title="Allocation by ISIN")
    st.plotly_chart(fig)
else:
    st.info("Add holdings above to see your portfolio.")
