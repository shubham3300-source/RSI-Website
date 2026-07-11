import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Reversal Signals", layout="wide")

st.title("🔄 Trend Reversal Signals")
st.write("Extracting reversal candidates from the side-table in Google Sheets...")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 1. Read the full sheet (Use your actual Worksheet name if not 'Sheet1')
    df = conn.read(worksheet="Sheet1", ttl=10)

    # 2. Extract columns from S onwards (Index 18 to 23)
    # We use a try-except here specifically for the slicing
    rev_data = df.iloc[:, 17:23].copy()

    # 3. Clean the data
    # Remove rows that are completely empty
    rev_data = rev_data.dropna(how="all")

    # 4. Find the correct header
    # Sometimes the first few rows are empty or contain titles.
    # We look for the row that contains 'Symbol'
    header_found = False
    for i in range(len(rev_data)):
        if "Symbol" in rev_data.iloc[i].values:
            # Set this row as the header
            rev_data.columns = rev_data.iloc[i]
            # Keep everything AFTER this row
            rev_data = rev_data.iloc[i+1:]
            header_found = True
            break

    if header_found:
        # Remove any remaining empty rows
        rev_data = rev_data.dropna(subset=["Symbol"])
        
        st.success(f"Successfully loaded {len(rev_data)} stocks.")
        
        # Display the table
        st.dataframe(
            rev_data.style.background_gradient(subset=['RSI'], cmap='RdYlGn'),
            use_container_width=True
        )
    else:
        st.warning("Could not find the Reversal Table headers (Symbol, Price, etc.) in the expected columns (S to X).")
        st.info("Check if your 'Filtered Stocks for Reversal' table starts at Column S in Google Sheets.")

except Exception as e:
    st.error(f"Error logic: {e}")
    st.info("Debugging Info: The app found " + str(df.shape[1]) + " columns in your sheet.")
