import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "katalot.db"

st.set_page_config(page_title="Kết quả Keno", page_icon="🎱", layout="wide")

st.title("🎱 Kết quả Keno Vietlott")
st.caption("Dữ liệu từ ketquaday.vn · Cập nhật tự động qua GitHub Actions")

@st.cache_data(ttl=300)
def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql(
            "SELECT ky, ngay, n20, b10, b09, b08, b07, b06, b05, b04, b03, b02, b01 FROM KQKENO ORDER BY ky DESC",
            conn
        )
        conn.close()
        return df
    except Exception as e:
        return None

df = load_data()

if df is None or df.empty:
    st.error("Không đọc được DB hoặc chưa có dữ liệu. Hãy chạy `python fetch_keno.py` trước.")
    st.stop()

# ── Metrics ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng số kỳ",      f"{len(df):,}")
col2.metric("Kỳ mới nhất",     df["ky"].iloc[0])
col3.metric("Kỳ cũ nhất",      df["ky"].iloc[-1])
col4.metric("Cập nhật lần cuối", df["ngay"].iloc[0])

st.divider()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📋 Kết quả", "🏆 Giải thưởng"])

with tab1:
    # Filter
    col1, col2 = st.columns([2, 1])
    with col1:
        ky_search = st.text_input("🔍 Tìm theo kỳ", placeholder="VD: 276300")
    with col2:
        limit = st.slider("Số kỳ hiển thị", 10, 200, 50, step=10)

    filtered = df.copy()
    if ky_search:
        filtered = filtered[filtered["ky"].astype(str).str.contains(ky_search)]
    filtered = filtered.head(limit)

    st.dataframe(
        filtered[["ky", "ngay", "n20"]].rename(columns={
            "ky": "Kỳ", "ngay": "Ngày giờ", "n20": "20 số kết quả"
        }),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Kỳ":            st.column_config.NumberColumn(width="small"),
            "Ngày giờ":      st.column_config.TextColumn(width="medium"),
            "20 số kết quả": st.column_config.TextColumn(width="large"),
        }
    )

with tab2:
    col1, col2 = st.columns([2, 1])
    with col1:
        ky_prize = st.text_input("🔍 Tìm theo kỳ", placeholder="VD: 276300", key="prize_search")
    with col2:
        loai_ve = st.selectbox("Loại vé", ["B10", "B09", "B08", "B07", "B06", "B05", "B04", "B03", "B02", "B01"])

    filtered2 = df.copy()
    if ky_prize:
        filtered2 = filtered2[filtered2["ky"].astype(str).str.contains(ky_prize)]
    filtered2 = filtered2.head(50)

    col_key = loai_ve.lower()

    # Parse chuỗi "10-00,09-00,..." thành bảng đẹp
    def parse_prize_str(s):
        if not s:
            return ""
        parts = s.split(",")
        result = []
        for p in parts:
            if "-" in p:
                so_trung, so_luong = p.split("-", 1)
                result.append(f"Trùng {int(so_trung)}: {int(so_luong)} vé")
        return " | ".join(result)

    display2 = filtered2[["ky", "ngay", col_key]].copy()
    display2[col_key] = display2[col_key].apply(parse_prize_str)
    display2.columns = ["Kỳ", "Ngày giờ", f"Giải {loai_ve}"]

    st.dataframe(
        display2,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Kỳ":       st.column_config.NumberColumn(width="small"),
            "Ngày giờ": st.column_config.TextColumn(width="medium"),
            f"Giải {loai_ve}": st.column_config.TextColumn(width="large"),
        }
    )
