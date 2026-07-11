import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import matplotlib
import plotly.express as px

# FIX for Segmentation Fault: Force Matplotlib to use a non-interactive backend
matplotlib.use('Agg')

st.set_page_config(page_title="RSI Alpha Terminal", layout="wide")

st.title("📈 RSI Sector Intelligence")

# --- CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Load Data
    df = conn.read(worksheet="Sheet1", ttl=60)
    
    # Slice Main Data (A:H)
    main_df = df.iloc[:, 0:8].copy()
    main_df.columns = ["Symbol", "RSI", "Vol_Mult", "Price", "Volume", "Avg_Vol", "Industry", "Change"]
    main_df = main_df.dropna(subset=["Symbol"])
    
    # Cleaning Numeric Data (Prevents crashes during styling)
    for col in ["RSI", "Vol_Mult"]:
        main_df[col] = pd.to_numeric(main_df[col].astype(str).str.replace(',', ''), errors='coerce')

    # UPDATED: Use width="stretch" instead of use_container_width=True
    st.dataframe(
        main_df.style.background_gradient(subset=['RSI'], cmap='RdYlGn_r'),
        width="stretch" 
    )

except Exception as e:
    st.error(f"Error: {e}")
