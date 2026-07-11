import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sector Analysis", layout="wide")

st.title("🏭 Sector & Industry Deep-Dive")

conn = st.connection("gsheets", type=GSheetsConnection)

def clean_num(val):
    """Safely converts strings with % or commas to numbers"""
    if pd.isna(val) or val == "": return 0.0
    try:
        return float(str(val).replace(',', '').replace('%', '').strip())
    except:
        return 0.0

try:
    # 1. Read the whole sheet
    df = conn.read(worksheet="Sheet1", ttl=0)

    # 2. DYNAMIC SEARCH: Find the 'Industry' table headers
    # This looks for the word "Industry" (the header of your 2nd table)
    start_row, start_col = -1, -1
    for r in range(min(len(df), 15)): # Scan top 15 rows
        for c in range(len(df.columns)):
            if str(df.iloc[r, c]).strip() == "Industry":
                start_row, start_col = r, c
                break
        if start_row != -1: break

    if start_row != -1:
        # 3. Slice the table (Assuming it has 5 columns: Industry, Stocks, Avg RSI, RSI>=60, Avg Vol)
        ind_df = df.iloc[start_row:, start_col : start_col + 5].copy()
        
        # 4. Set Headers
        ind_df.columns = ind_df.iloc[0] # Use the 'Industry' row as header
        ind_df = ind_df.iloc[1:].reset_index(drop=True) # Remove header row from data
        
        # 5. Drop empty rows
        ind_df = ind_df.dropna(subset=[ind_df.columns[0]])
        ind_df = ind_df[ind_df.iloc[:, 0] != ""]

        # 6. Clean Numeric Columns (Avg RSI, RSI>=60, etc.)
        # We clean every column except the first one (Industry Name)
        for col in ind_df.columns[1:]:
            ind_df[col] = ind_df[col].apply(clean_num)

        # --- UI DISPLAY ---
        
        # Metric Row
        top_sector = ind_df.sort_values(ind_df.columns[2], ascending=False).iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Industries", len(ind_df))
        c2.metric("Top Industry", top_sector.iloc[0])
        c3.metric("Highest Avg RSI", f"{top_sector.iloc[2]:.2f}")

        # Plotly Chart
        st.subheader("Industry Strength (Avg RSI)")
        fig = px.bar(
            ind_df.sort_values(ind_df.columns[2], ascending=True), 
            x=ind_df.columns[2], 
            y=ind_df.columns[0], 
            orientation='h',
            color=ind_df.columns[2],
            color_continuous_scale="RdYlGn",
            text_auto='.1f'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Data Table
        st.subheader("Detailed Industry Metrics")
        st.dataframe(
            ind_df.style.background_gradient(subset=[ind_df.columns[2]], cmap='RdYlGn')
            .format(precision=2),
            use_container_width=True
        )

    else:
        st.error("Could not find the 'Industry' table in your Google Sheet.")
        st.info("Ensure the word 'Industry' is written exactly in your sheet (likely Column L).")

except Exception as e:
    st.error(f"Logic Error: {e}")
