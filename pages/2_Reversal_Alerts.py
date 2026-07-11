import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide")
st.title("🔄 Trend Reversal Signals")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Read sheet
    df = conn.read(worksheet="Sheet1", ttl=10)

    # In your sheet, the Filtered Stocks table starts at Column S (Index 18)
    # and ends at Column X (Index 23)
    rev_df = df.iloc[:, 18:24].copy()
    
    # We find the row where the headers actually start
    # Based on your data, it says "Symbol" in the 1st column of this slice
    rev_df.columns = ["Symbol", "Price", "Volume", "RSI", "Vol_Mult", "Industry"]
    
    # Remove empty rows and the header row itself
    rev_df = rev_df.dropna(subset=["Symbol"])
    rev_df = rev_df[rev_df["Symbol"] != "Symbol"]

    st.write("### Filtered Reversal Stocks")
    st.table(rev_df)

except Exception as e:
    st.error(f"Could not find Reversal Table: {e}")
