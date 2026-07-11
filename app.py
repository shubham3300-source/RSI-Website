import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="RSI Alpha Terminal", layout="wide", page_icon="📈")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; color: #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    df = conn.read(worksheet="Sheet1", ttl=60)
    # Main Table Slicing (A:H)
    main = df.iloc[:, 0:8].copy()
    main.columns = ["Symbol", "RSI", "Vol_Mult", "Price", "Volume", "Avg_Vol", "Industry", "Change"]
    main = main.dropna(subset=["Symbol"])
    # Clean numeric data
    for col in ["RSI", "Vol_Mult", "Price", "Volume"]:
        main[col] = pd.to_numeric(main[col].astype(str).str.replace(',', '').replace('%', ''), errors='coerce')
    return main

try:
    df = load_data()

    # --- SIDEBAR FILTERS ---
    st.sidebar.title("📊 Filter Terminal")
    search_symbol = st.sidebar.text_input("Search Symbol (e.g. RELIANCE)")
    selected_industry = st.sidebar.multiselect("Select Industry", options=df['Industry'].unique(), default=df['Industry'].unique())
    rsi_range = st.sidebar.slider("RSI Range", 0, 100, (0, 100))
    vol_min = st.sidebar.number_input("Min Volume Multiple", value=0.0, step=0.5)

    # Filter data based on sidebar
    filtered_df = df[
        (df['Industry'].isin(selected_industry)) &
        (df['RSI'].between(rsi_range[0], rsi_range[1])) &
        (df['Vol_Mult'] >= vol_min)
    ]
    if search_symbol:
        filtered_df = filtered_df[filtered_df['Symbol'].str.contains(search_symbol.upper())]

    # --- MAIN VIEW ---
    st.title("📈 RSI Sector Intelligence")
    
    # 1. Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Stocks Scanned", len(filtered_df))
    with c2: st.metric("Avg RSI", f"{filtered_df['RSI'].mean():.1f}")
    with c3: st.metric("Bullish (>60)", len(filtered_df[filtered_df['RSI'] > 60]))
    with c4: st.metric("Vol Spikes (>2x)", len(filtered_df[filtered_df['Vol_Mult'] > 2]))

    # 2. Charts Row
    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("RSI Distribution")
        fig_rsi = px.histogram(filtered_df, x="RSI", nbins=20, color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig_rsi, use_container_width=True)

    with chart_col2:
        st.subheader("Industry Strength (Avg RSI)")
        ind_avg = filtered_df.groupby("Industry")["RSI"].mean().sort_values()
        fig_ind = px.bar(ind_avg, orientation='h', color_discrete_sequence=['#00CC96'])
        st.plotly_chart(fig_ind, use_container_width=True)

    # 3. Interactive Data Table
    st.markdown("---")
    st.subheader("Market Scan Results")
    st.dataframe(
        filtered_df.style.background_gradient(subset=['RSI'], cmap='RdYlGn_r')
        .background_gradient(subset=['Vol_Mult'], cmap='Blues')
        .format({"Price": "{:,.2f}", "Vol_Mult": "{:.2f}x"}),
        use_container_width=True,
        height=500
    )

except Exception as e:
    st.error(f"Waiting for data or layout change: {e}")
