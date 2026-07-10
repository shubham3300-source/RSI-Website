import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🔄 Potential Reversal Alerts")

conn = st.connection("gsheets", type=GSheetsConnection)

# Read specific columns for the Reversal table (Right side of your sheet)
reversal_df = conn.read(worksheet="Sheet1", usecols=[18,19,20,21,22,23]).dropna(how="all")

st.warning("Stocks identified as potential reversals based on Price-Volume-RSI Divergence")
st.table(reversal_df)