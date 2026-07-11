import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Reversal Signals", layout="wide")

st.title("🔄 Potential Reversal Signals")

conn = st.connection("gsheets", type=GSheetsConnection)

def clean_num(val):
    if pd.isna(val) or val == "": return 0.0
    try:
        return float(str(val).replace(',', '').replace('%', '').strip())
    except:
        return 0.0

try:
    # 1. Read the sheet
    df = conn.read(worksheet="Sheet1", ttl=0)

    # 2. Search for the 'Symbol' cell dynamically anywhere in the top 10 rows
    # This prevents the '3 vs 6' column mismatch
    start_row, start_col = -1, -1
    for r in range(min(len(df), 10)):
        for c in range(len(df.columns)):
            if str(df.iloc[r, c]).strip() == "Symbol":
                start_row, start_col = r, c
                break
        if start_row != -1: break

    if start_row != -1:
        # 3. Slice data starting from where 'Symbol' was found
        # We take 6 columns from the start_col
        rev_df = df.iloc[start_row:, start_col : start_col + 6].copy()
        
        # 4. Set headers correctly based on the number of columns actually found
        new_headers = rev_df.iloc[0].tolist()
        rev_df.columns = new_headers
        rev_df = rev_df.iloc[1:].reset_index(drop=True)

        # 5. Filter out empty Symbol rows
        rev_df = rev_df[rev_df.iloc[:, 0].notna()]
        
        # 6. Clean numeric columns for styling
        # We look for RSI and Volume Multiple by name or position
        for col in rev_df.columns:
            if "RSI" in str(col) or "Volume" in str(col) or "Price" in str(col):
                rev_df[col] = rev_df[col].apply(clean_num)

        st.success(f"Loaded {len(rev_df)} stocks starting from column index {start_col}")
        
        # 7. Display
        st.dataframe(
            rev_df.style.background_gradient(subset=[rev_df.columns[3]], cmap='RdYlGn_r') # RSI is usually 4th col
            .format(precision=2),
            use_container_width=True
        )
    else:
        st.error("Could not find the 'Symbol' header in your Google Sheet.")
        st.info("Make sure the word 'Symbol' is typed exactly in your Reversal table.")

except Exception as e:
    st.error(f"Logic Error: {e}")
    st.info("Check if your worksheet name is 'Sheet1'.")
