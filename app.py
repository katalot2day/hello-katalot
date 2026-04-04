import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "katalot.db"

st.set_page_config(page_title="Hello Katalot", page_icon="👋", layout="centered")
st.title("👋 Hello Katalot")
st.caption("Demo app — dữ liệu lưu từ GitHub Actions → SQLite → Streamlit")

try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM messages ORDER BY id DESC", conn)
    conn.close()

    st.metric("Tổng số bản ghi", len(df))
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.warning(f"Chưa có dữ liệu hoặc lỗi: {e}")
    st.info("Hãy chạy `python fetch.py` trước để tạo dữ liệu.")
