import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Reversal Signals", layout="wide")

st.title("🔄 Trend Reversal Signals")
st.markdown("---")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 1. Read the sheet
    df = conn.read(worksheet="Sheet1", ttl=10)

    # 2. Slice Column R to Column W (Index 17 to 23)
    # R=17, S=18, T=19, U=20, V=21, W=22. 
    # Slicing 17:23 gives us exactly these 6 columns.
    rev_data = df.iloc[:, 17:23].copy()

    # 3. Clean empty rows
    rev_data = rev_data.dropna(how="all")

    # 4. Find the Header Row (searching for "Symbol")
    header_found = False
    for i in range(len(rev_data)):
        # Look at the first column of our slice (Column R) for the word "Symbol"
        if "Symbol" in str(rev_data.iloc[i, 0]):
            rev_data.columns = rev_data.iloc[i] # Set the found row as headers
            rev_data = rev_data.iloc[i+1:]      # Keep data below it
            header_found = True
            break

    if header_found:
        # Remove any empty rows based on Symbol column
        rev_data = rev_data.dropna(subset=["Symbol"])
        
        # Convert numeric columns so colors/sorting work correctly
        # We target RSI and Volume Multiple
        for col in ["RSI", "Volume Multiple"]:
            if col in rev_data.columns:
                rev_data[col] = pd.to_numeric(rev_data[col], errors='coerce')

        st.success(f"✅ Found {len(rev_data)} Potential Reversal Stocks")
        
        # Display the professional table
        st.dataframe(
            rev_data.style.background_gradient(subset=['RSI'], cmap='RdYlGn_r')
            .format(precision=2),
            use_container_width=True,
            height=600
        )
    else:
        st.warning("⚠️ Could not find the Reversal Table headers.")
        st.info("Check if Column R in your Google Sheet contains the word 'Symbol'.")

except Exception as e:
    st.error(f"❌ Error: {e}")
    st.write("Check if the Worksheet name is exactly 'Sheet1'.")
