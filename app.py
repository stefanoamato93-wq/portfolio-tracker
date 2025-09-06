import streamlit as st
import pandas as pd
from datetime import date
from google.oauth2 import service_account
import gspread

st.set_page_config(page_title="Portfolio Tracker", layout="wide")

# -----------------------
# Google Sheets connection
# -----------------------
creds_dict = st.secrets["GCP_SERVICE_ACCOUNT_JSON"]
credentials = service_account.Credentials.from_service_account_info(creds_dict)
client = gspread.authorize(credentials)

# ⚠️ Change this to the actual Google Spreadsheet name (file title in Drive)
SPREADSHEET_TITLE = "PortfolioData"  
TAB_NAME = "Sheet1"

try:
    sheet = client.open(SPREADSHEET_TITLE).worksheet(TAB_NAME)
except Exception as e:
    st.error("❌ Could not open Google Sheet. Check:\n"
             "- The sheet is shared with your service account email\n"
             "- The spreadsheet title matches exactly\n"
             f"Error details: {e}")
    st.stop()

# -----------------------
# Load portfolio data
# -----------------------
@st.cache_data
def load_data():
    records = sheet.get_all_records()
    return pd.DataFrame(records)

if "portfolio" not in st.session_state:
    st.session_state.portfolio = load_data()

st.title("📊 Portfolio Tracker (Persistent)")

# -----------------------
# Show current portfolio
# -----------------------
st.subheader("Current Holdings")
st.dataframe(st.session_state.portfolio)

# -----------------------
# Add a new holding (with toggle)
# -----------------------
if "show_form" not in st.session_state:
    st.session_state.show_form = False

if not st.session_state.show_form:
    if st.button("➕ Add Holding"):
        st.session_state.show_form = True
else:
    with st.form("add_holding_form"):
        isin = st.text_input("ISIN")
        quantity = st.number_input("Amount of shares", min_value=0.0, value=0.0, step=1.0)
        price = st.number_input("Price of purchase (per share)", min_value=0.0, value=0.0, step=0.01)
        purchase_date = st.date_input("Date of purchase", value=date.today())

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("✅ Save")
        with col2:
            cancelled = st.form_submit_button("❌ Cancel")

        if submitted and isin and quantity > 0 and price > 0:
            new_entry = {
                "ISIN": isin,
                "Quantity": quantity,
                "Price": price,
                "Date": str(purchase_date)
            }
            st.session_state.portfolio = pd.concat(
                [st.session_state.portfolio, pd.DataFrame([new_entry])],
                ignore_index=True
            )
            # Save to Google Sheets
            sheet.append_row(list(new_entry.values()))
            st.success("Added new holding!")
            st.session_state.show_form = False

        if cancelled:
            st.session_state.show_form = False

# -----------------------
# Pie chart of allocations
# -----------------------
if not st.session_state.portfolio.empty:
    st.subheader("Portfolio Allocation")
    chart_data = st.session_state.portfolio.groupby("ISIN")["Quantity"].sum()
    st.plotly_chart(
        {
            "data": [{"labels": chart_data.index, "values": chart_data.values, "type": "pie"}],
            "layout": {"title": "Holdings Distribution"},
        }
    )
