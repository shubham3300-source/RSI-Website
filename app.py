import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Stock RSI Dashboard", layout="wide")
st.title("📈 Market Intelligence Dashboard")

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Read Main Stock Table (Assuming columns A to I)
df = conn.read(worksheet="Sheet1", usecols=[0,1,2,3,4,5,6,7,8]).dropna(how="all")

# Top Row Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Stocks", len(df))
col2.metric("Avg RSI", round(df['RSI'].mean(), 2))
col3.metric("High Volume Stocks", len(df[df['Volume Multiple'] > 2]))
col4.metric("Bullish Stocks (RSI >60)", len(df[df['RSI'] >= 60]))

st.markdown("---")
st.subheader("Top Stocks by Volume Multiple")
st.dataframe(df.sort_values('Volume Multiple', ascending=False).head(10), use_container_width=True)
