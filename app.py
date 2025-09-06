import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import gspread
from google.oauth2.service_account import Credentials
import json

st.title("Portfolio Tracker")

# ---------------------------
# Load Google Sheets credentials
# ---------------------------
try:
    creds_dict = st.secrets["GCP_SERVICE_ACCOUNT_JSON"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"❌ Could not load Google credentials. Error: {e}")
    st.stop()

# ---------------------------
# Google Sheet settings
# ---------------------------
SHEET_NAME = "Portfolio"  # Name of your Google Sheet
try:
    sheet = client.open(SHEET_NAME).sheet1
except Exception as e:
    st.error(f"❌ Could not open Google Sheet. Check:\n"
             f"- The sheet is shared with your service account email (Editor access)\n"
             f"- The spreadsheet title matches exactly\n"
             f"Error details: {e}")
    st.stop()

# ---------------------------
# Load portfolio from sheet
# ---------------------------
try:
    data = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(columns=["ISIN", "Quantity", "Price", "Date"])
except Exception as e:
    st.error(f"❌ Could not read data from Google Sheet: {e}")
    df = pd.DataFrame(columns=["ISIN", "Quantity", "Price", "Date"])

# ---------------------------
# Session state for showing form
# ---------------------------
if "show_form" not in st.session_state:
    st.session_state.show_form = False

# ---------------------------
# Add holding button
# ---------------------------
if st.button("+ Add Holding"):
    st.session_state.show_form = True

# ---------------------------
# Input form (conditionally shown)
# ---------------------------
if st.session_state.show_form:
    st.subheader("Add a new holding")
    with st.form("add_holding_form"):
        isin = st.text_input("ISIN")
        quantity = st.number_input("Amount of shares", min_value=0.0, value=0.0, step=1.0)
        price = st.number_input("Price of purchase (per share)", min_value=0.0, value=0.0, step=0.01)
        purchase_date = st.date_input("Date of purchase", value=date.today())
        submitted = st.form_submit_button("Add to portfolio")
        cancel = st.form_submit_button("Cancel")

        if submitted and isin and quantity > 0 and price > 0:
            # Append to Google Sheet
            try:
                sheet.append_row([isin, quantity, price, str(purchase_date)])
                st.success(f"Holding {isin} added successfully!")
                st.session_state.show_form = False
            except Exception as e:
                st.error(f"❌ Could not write to Google Sheet: {e}")

        if cancel:
            st.session_state.show_form = False
            st.info("Form canceled")

# ---------------------------
# Display portfolio
# ---------------------------
if not df.empty:
    df["Value"] = df["Quantity"] * df["Price"]

    st.metric("Total Portfolio Value", f"${df['Value'].sum():,.2f}")
    st.subheader("Holdings")
    st.dataframe(df)

    st.subheader("Portfolio Allocation")
    fig = px.pie(df, names="ISIN", values="Value", title="Allocation by ISIN")
    st.plotly_chart(fig)
else:
    st.info("Add holdings above to see your portfolio.")
