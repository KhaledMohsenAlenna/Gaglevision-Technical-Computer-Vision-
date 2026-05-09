import streamlit as st
import pandas as pd
import psycopg2
from PIL import Image
import os, time

st.set_page_config(layout="wide")
st.title("Equipment Utilization Dashboard")

col1, col2 = st.columns([2, 1])
img_placeholder = col1.empty()
data_placeholder = col2.empty()

def get_data():
    try:
        conn = psycopg2.connect(dbname="equipment_db", user="user", password="password", host="localhost", port="5432")
        df = pd.read_sql("SELECT equipment_id, state, activity, active_sec, util_pct FROM analytics ORDER BY frame_id DESC LIMIT 5", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

while True:
    if os.path.exists("shared_data/latest_frame.jpg"):
        try:
            img = Image.open("shared_data/latest_frame.jpg")
            img_placeholder.image(img, channels="BGR", use_column_width=True)
        except: pass

    df = get_data()
    with data_placeholder.container():
        st.subheader("Live Analytics")
        if not df.empty: st.dataframe(df)
        else: st.info("Waiting for data from PostgreSQL...")

    time.sleep(0.5)
