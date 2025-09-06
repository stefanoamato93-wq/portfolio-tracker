import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import json

st.title("Portfolio Tracker (Persistent)")

# -------------------------------
# Google Sheets setup using secrets
# -------------------------------
creds_dict = json.loads(st.secrets["GCP"]["service_account_json"])
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open your sheet (make sure it exists and is shared with the service account)
sheet = client.open("PortfolioTracker").worksheet("Holdings")

# Load data into DataFrame
try:
    df = get_as_dataframe(sheet, evaluate_formulas=True).dropna(how='all')
except:
    df = pd.DataFrame(columns=["ISIN","Quantity","Price","Date"])

# -------------------------------
# Show portfolio total and pie
# -------------------------------
if not df.empty:
    df["Value"] = df["Quantity"] * df["Price"]
    st.metric("Total Value", f"${df['Value'].sum():,.2f}")

    st.subheader("Holdings")
    st.dataframe(df)

    st.subheader("Portfolio Allocation")
    fig = px.pie(df, names="ISIN", values="Value", title="Allocation by ISIN")
    st.plotly_chart(fig)
else:
    st.info("No holdings yet.")

# -------------------------------
# Add holding form (toggle)
# -------------------------------
if "show_form" not in st.session_state:
    st.session_state.show_form = False

if st.button("+ Add Holding"):
    st.session_state.show_form = True

if st.session_state.show_form:
    st.subheader("Add a new holding")

    with st.form("add_holding_form"):
        isin = st.text_input("ISIN")
        quantity = st.number_input("Amount of shares", min_value=0.0, value=0.0, step=1.0)
        price = st.number_input("Price of purchase (per share)", min_value=0.0, value=0.0, step=0.01)
        purchase_date = st.date_input("Date of purchase", value=date.today())
        submitted = st.form_submit_button("Add to portfolio")

    # Process submission
    if submitted and isin and quantity > 0 and price > 0:
        new_row = pd.DataFrame([{
            "ISIN": isin,
            "Quantity": quantity,
            "Price": price,
            "Date": str(purchase_date)
        }])
        df = pd.concat([df, new_row], ignore_index=True)

        # Save to Google Sheets
        set_with_dataframe(sheet, df)

        st.session_state.show_form = False
        st.success("Holding added!")

    # Cancel button outside the form
    if st.button("Cancel"):
        st.session_state.show_form = False
        st.info("Form canceled")
