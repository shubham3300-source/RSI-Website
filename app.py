import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="RSI Alpha Terminal", layout="wide", page_icon="📈")

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    </style>
    """, unsafe_allow_html=True)

st.title("🦅 RSI Sector Alpha Terminal")
st.markdown(f"**Market Scan Status:** <span style='color:green'>● Live Data</span>", unsafe_allow_html=True)

# --- DATA LOADING ---
# TTL=60 means it will refresh from Google Sheets every 60 seconds
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Read the whole sheet
    full_df = conn.read(worksheet="Sheet1", ttl=60)

    # 1. Extract Main Table (Cols A to H)
    main_df = full_df.iloc[:, 0:8].dropna(how="all")
    main_df.columns = ["Symbol", "RSI", "Vol_Mult", "Price", "Volume", "Avg_Vol", "Industry", "1D_Change"]

    # 2. Extract Industry Stats (Cols L to P - Adjust based on your sheet)
    ind_stats = full_df.iloc[:, 11:16].dropna(how="all")
    ind_stats.columns = ["Industry", "Stocks", "Avg_RSI", "RSI_60_Plus", "Avg_Vol_Mult"]

    # --- TOP METRICS BAR ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Stocks Scanned", len(main_df))
    m2.metric("Avg RSI", f"{main_df['RSI'].mean():.1f}")
    m3.metric("High Volume (2x+)", len(main_df[main_df['Vol_Mult'] > 2]))
    m4.metric("Bullish Industry", ind_stats.sort_values("Avg_RSI", ascending=False).iloc[0,0])

    # --- TABS FOR ORGANIZATION ---
    tab1, tab2 = st.tabs(["📊 Sector Heatmap", "🏭 Industry Performance"])

    with tab1:
        st.subheader("Real-time Sector Scan")
        
        # Search and Filter in columns
        c1, c2 = st.columns([1, 2])
        search = c1.text_input("🔍 Search Symbol")
        if search:
            main_df = main_df[main_df['Symbol'].str.contains(search.upper())]

        # Professional Styled Table
        def style_rsi(val):
            color = 'red' if val > 70 else ('green' if val < 30 else 'black')
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            main_df.style.applymap(style_rsi, subset=['RSI'])
            .background_gradient(subset=['Vol_Mult'], cmap='BuGn')
            .format({"Price": "{:.2f}", "Vol_Mult": "{:.2x}"}),
            use_container_width=True,
            height=500
        )

    with tab2:
        st.subheader("Industry Strength Index")
        st.dataframe(ind_stats, use_container_width=True)

except Exception as e:
    st.error("Error loading data. Check if your Sheet Column names match the code.")
    st.info("Ensure your Google Sheet structure matches the layout in the CSV you provided.")
