import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sector Analysis", layout="wide")

st.title("🏭 Sector & Industry Deep-Dive")
st.markdown("---")

conn = st.connection("gsheets", type=GSheetsConnection)

def clean_percent(val):
    """Cleans percentage strings and commas"""
    if pd.isna(val) or val == "": return 0.0
    try:
        return float(str(val).replace(',', '').replace('%', '').strip())
    except:
        return 0.0

try:
    # 1. Read the sheet
    df = conn.read(worksheet="Sheet1", ttl=10)

    # 2. Extract Industry Table (Column L to P -> Index 11 to 16)
    # This table usually contains Industry, No. of Stocks, Avg RSI, etc.
    ind_df = df.iloc[:, 11:16].copy()
    
    # 3. Find the header row (Search for 'Industry' in Column L)
    found_idx = -1
    for i in range(min(len(ind_df), 10)):
        if "Industry" in str(ind_df.iloc[i, 0]):
            found_idx = i
            break
            
    if found_idx != -1:
        ind_df.columns = ind_df.iloc[found_idx]
        ind_df = ind_df.iloc[found_idx+1:].reset_index(drop=True)
    else:
        ind_df.columns = ["Industry", "Stocks", "Avg_RSI", "RSI_60_Plus", "Avg_Vol_Mult"]

    # 4. Clean Data
    ind_df = ind_df.dropna(subset=["Industry"])
    for col in ["Avg RSI", "Avg Volume", "Avg_RSI", "RSI>=60"]:
        if col in ind_df.columns:
            ind_df[col] = ind_df[col].apply(clean_percent)

    # --- INTERACTIVE UI ---
    
    # Chart: Industry RSI Comparison
    st.subheader("Industry Strength Heatmap")
    fig = px.bar(
        ind_df.sort_values("Avg RSI", ascending=False), 
        x="Industry", 
        y="Avg RSI", 
        color="Avg RSI",
        color_continuous_scale="RdYlGn",
        text_auto='.1f'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Layout: Table and Metrics
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Industry Summary Table")
        st.dataframe(
            ind_df.style.background_gradient(subset=['Avg RSI'], cmap='RdYlGn')
            .format(precision=2),
            use_container_width=True
        )

    with col2:
        st.subheader("Top Performing Sector")
        if not ind_df.empty:
            top_sector = ind_df.sort_values("Avg RSI", ascending=False).iloc[0]
            st.metric(label=top_sector["Industry"], value=f"{top_sector['Avg RSI']:.1f} RSI")
            st.write(f"This sector has **{top_sector.get('No. of Stocks', 'N/A')}** active stocks.")

except Exception as e:
    st.error(f"Error loading Sector Analysis: {e}")
    st.info("Check if your Industry table starts at Column L in Google Sheets.")
