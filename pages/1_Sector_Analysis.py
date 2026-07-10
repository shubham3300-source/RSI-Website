import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🔍 Industry Deep-Dive")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Sheet1", usecols=[0,1,2,3,4,5,6,7,8]).dropna(how="all")

# Sidebar Filter
industry_list = df['Industry'].unique().tolist()
selected_sector = st.sidebar.multiselect("Select Industries", industry_list, default=industry_list[0])

# Show Filtered Data
filtered_df = df[df['Industry'].isin(selected_sector)]
st.dataframe(filtered_df.style.background_gradient(subset=['RSI'], cmap='RdYlGn_r'), use_container_width=True)