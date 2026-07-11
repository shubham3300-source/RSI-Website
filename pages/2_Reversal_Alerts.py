import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout="wide")
st.title("🔄 Trend Reversal Signals")

conn = st.connection("gsheets", type=GSheetsConnection)
full_df = conn.read(worksheet="Sheet1", ttl=60)

# Extract Reversal Table (Columns S to W / index 18 to 23)
rev_df = full_df.iloc[:, 18:23].dropna(how="all")
rev_df.columns = ["Symbol", "Price", "Volume", "RSI", "Vol_Mult"]

if not rev_df.empty:
    st.success(f"Found {len(rev_df)} potential reversal candidates")
    
    # Grid layout for reversal stocks
    for i in range(0, len(rev_df), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(rev_df):
                row = rev_df.iloc[i + j]
                with col:
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; padding:20px; border-radius:10px">
                        <h3>{row['Symbol']}</h3>
                        <p>Price: <b>{row['Price']}</b></p>
                        <p>RSI: <span style="color:blue">{row['RSI']}</span></p>
                        <p>Volume Mult: <b>{row['Vol_Mult']}x</b></p>
                    </div>
                    """, unsafe_allow_html=True)
else:
    st.info("No reversal signals detected in the current scan.")
