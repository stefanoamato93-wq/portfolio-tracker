import streamlit as st
import pandas as pd
from datetime import date
from google.oauth2 import service_account
import gspread

st.set_page_config(page_title="Portfolio Tracker", layout="wide")

# -----------------------
# Google Sheets connection
# -----------------------
# Secrets must contain a JSON service account (in .streamlit/secrets.toml)
creds_dict = st.secrets["GCP_SERVICE_ACCOUNT_JSON"]

# ✅ Add Sheets + Drive scopes
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = service_account.Credentials.from_service_account_info(
    creds_dict,
    scopes=scopes
)
client = gspread.authorize(credentials)

# ⚠️ Use the exact Spreadsheet title (or better: replace with the Spreadsheet ID)
SPREADSHEET_TITLE = "PortfolioData"   # Change this to your Google Sheet title
TAB_NAME = "Sheet1"

try:
    sheet = client.open(SPREADSHEET_TITLE).worksheet(TAB_NAME)
except Exception as e:
    st.error("❌ Could not open Google Sheet. Check:\n"
             "- The sheet is shared with your service account email (Editor access)\n"
             "- The spreadsheet title matches exactly\n"
             f"Error details: {e}")
    st.stop()

# -----------------------
# Load portfolio data
# -----------------------
def load_portfolio():
    data = sheet.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["ISIN", "Quantity", "Price", "Date"])

def save_portfolio(df):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

if "portfolio" not in st.session_state:
    st.session_state.portfolio = load_portfolio()

# -----------------------
# UI: Add Holding button
# -----------------------
st.title("📊 Portfolio Tracker")

if "show_form" not in st.session_state:
    st.session_state.show_form = False

if not st.session_state.show_form:
    if st.button("➕ Add Holding"):
        st.session_state.show_form = True
else:
    st.subheader("Add a new holding")
    with st.form("add_holding_form"):
        isin = st.text_input("ISIN")
        quantity = st.number_input("Amount of shares", min_value=0.0, value=0.0, step=1.0)
        price = st.number_input("Price of purchase (per share)", min_value=0.0, value=0.0, step=0.01)
        purchase_date = st.date_input("Date of purchase", value=date.today())

        col1, col2 = st.columns(2)
        submitted = col1.form_submit_button("✅ Save")
        cancelled = col2.form_submit_button("❌ Cancel")

        if submitted and isin and quantity > 0 and price > 0:
            st.session_state.portfolio = pd.concat([
                st.session_state.portfolio,
                pd.DataFrame([{
                    "ISIN": isin,
                    "Quantity": quantity,
                    "Price": price,
                    "Date": str(purchase_date)
                }])
            ], ignore_index=True)

            save_portfolio(st.session_state.portfolio)
            st.success("✅ Holding added")
            st.session_state.show_form = False
            st.experimental_rerun()

        if cancelled:
            st.session_state.show_form = False
            st.experimental_rerun()

# -----------------------
# Display portfolio
# -----------------------
if not st.session_state.portfolio.empty:
    st.subheader("📑 Current Portfolio")
    st.dataframe(st.session_state.portfolio)

    # Example pie chart by ISIN
    st.subheader("📈 Portfolio Breakdown")
    fig = st.session_state.portfolio.groupby("ISIN")["Quantity"].sum().plot.pie(autopct="%1.1f%%").get_figure()
    st.pyplot(fig)
else:
    st.info("No holdings yet. Click ➕ Add Holding to start.")
