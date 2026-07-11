import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Sector Map Terminal", layout="wide")

st.title("📈 Sector Map Dashboard")

# Create connection
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_numbers(df, columns):
    """Helper to remove commas and convert to numbers"""
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.replace('%', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

try:
    # 1. Load the raw data
    # Change "Sheet1" to the exact name of your tab in Google Sheets
    raw_df = conn.read(worksheet="Sheet1", ttl=10)

    # 2. Extract the Main Table (First 8 columns)
    # We use .dropna(subset=['Symbol']) to ignore empty rows
    main_df = raw_df.iloc[:, 0:8].copy()
    main_df.columns = ["Symbol", "RSI", "Vol_Mult", "Price", "Volume", "Avg_Vol", "Industry", "Change"]
    main_df = main_df.dropna(subset=["Symbol"])
    
    # Clean numeric data
    main_df = clean_numbers(main_df, ["RSI", "Vol_Mult", "Price", "Volume"])

    # --- UI DISPLAY ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Stocks Scanned", len(main_df))
    col2.metric("Avg RSI", f"{main_df['RSI'].mean():.2f}")
    col3.metric("Max Volume Mult", f"{main_df['Vol_Mult'].max():.2f}x")

    st.subheader("Market Overview")
    st.dataframe(
        main_df.style.background_gradient(subset=['RSI'], cmap='RdYlGn_r')
        .background_gradient(subset=['Vol_Mult'], cmap='Blues'),
        use_container_width=True
    )

    # --- DEBUG SECTION (Optional - Remove later) ---
    with st.expander("🛠 Debugging: See Raw Data from Google Sheets"):
        st.write("If the table above is empty, look at the Raw Data below to see which columns are being pulled.")
        st.write(raw_df.head(10))

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Check if your Google Sheet Tab is named 'Sheet1'. If not, change 'Sheet1' in the code to your actual Tab name.")
