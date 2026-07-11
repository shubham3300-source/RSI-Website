import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Reversal Signals", layout="wide")

st.title("🔄 Potential Reversal Signals")
st.info("Data source: Google Sheet (Range R2:W)")

# --- CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_val(val):
    """Cleans commas and percentage signs from strings and converts to float"""
    if pd.isna(val): return 0.0
    try:
        # Remove commas, spaces, and % signs
        clean = str(val).replace(',', '').replace('%', '').strip()
        return float(clean)
    except:
        return 0.0

try:
    # 1. Read the sheet
    # Using ttl=0 for testing to ensure it doesn't use old cache
    df = conn.read(worksheet="Sheet1", ttl=0)

    # 2. Slice R:W (Index 17 to 23)
    # Since Symbol is at R2, we take everything from that row downwards
    # Row 1 in Sheet is index 0 in Python. So Row 2 (Header) is Index 0 or 1.
    # To be safe, we hunt for 'Symbol' in Column R
    rev_df = df.iloc[:, 17:23].copy()
    
    # 3. Find the header row where 'Symbol' exists
    # We look through the first 5 rows to find the word 'Symbol'
    found_idx = -1
    for i in range(min(len(rev_df), 5)):
        if "Symbol" in str(rev_df.iloc[i, 0]):
            found_idx = i
            break
    
    if found_idx != -1:
        # Set the found row as header
        rev_df.columns = rev_df.iloc[found_idx]
        # Keep everything below the header
        rev_df = rev_df.iloc[found_idx + 1:].reset_index(drop=True)
    else:
        # Fallback: manually name them if 'Symbol' isn't found exactly
        rev_df.columns = ["Symbol", "Price", "Volume", "RSI", "Volume Multiple", "Industry"]

    # 4. Filter empty rows
    rev_df = rev_df.dropna(subset=["Symbol"])
    rev_df = rev_df[rev_df["Symbol"] != ""]

    # 5. CRITICAL: Clean numeric columns so they don't crash the table
    # We clean RSI and Volume Multiple for the colors
    if "RSI" in rev_df.columns:
        rev_df["RSI"] = rev_df["RSI"].apply(clean_val)
    if "Volume Multiple" in rev_df.columns:
        rev_df["Volume Multiple"] = rev_df["Volume Multiple"].apply(clean_val)

    # 6. Display Table
    if not rev_df.empty:
        st.success(f"Found {len(rev_df)} stocks in the Reversal list.")
        
        # Applying professional styling
        st.dataframe(
            rev_df.style.background_gradient(subset=['RSI'], cmap='RdYlGn_r')
            .background_gradient(subset=['Volume Multiple'], cmap='Blues')
            .format(precision=2),
            use_container_width=True,
            height=600
        )
    else:
        st.warning("Reversal list is currently empty in the Google Sheet.")

except Exception as e:
    st.error(f"Logic Error: {e}")
    st.write("Please check if the tab name is 'Sheet1' and Column R contains 'Symbol'.")
