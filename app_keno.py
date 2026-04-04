import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "katalot.db"

st.set_page_config(page_title="Kết quả Keno", page_icon="🎱", layout="wide")

# ── Header ──────────────────────────────────────────────────────────────────
st.title("🎱 Kết quả Keno Vietlott")
st.caption("Dữ liệu từ ketquaday.vn · Cập nhật tự động qua GitHub Actions")

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql(
            "SELECT ky, ngay, n20, chan, le, lon, nho FROM KQKENO ORDER BY ky DESC",
            conn
        )
        conn.close()
        return df
    except Exception as e:
        return None, str(e)

df = load_data()

if df is None or (isinstance(df, tuple)):
    st.error("Không đọc được DB. Hãy chạy `python fetch_keno.py` trước.")
    st.stop()

if df.empty:
    st.warning("Chưa có dữ liệu. Hãy chạy `python fetch_keno.py` trước.")
    st.stop()

# ── Metrics ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng số kỳ", f"{len(df):,}")
col2.metric("Kỳ mới nhất", df["ky"].iloc[0])
col3.metric("Kỳ cũ nhất", df["ky"].iloc[-1])
col4.metric("Cập nhật lần cuối", df["ngay"].iloc[0])

st.divider()

# ── Filters ──────────────────────────────────────────────────────────────────
with st.expander("🔍 Bộ lọc", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        ky_search = st.text_input("Tìm theo kỳ", placeholder="VD: 276300")
    with col2:
        chan_le = st.selectbox("Chẵn / Lẻ nhiều hơn", ["Tất cả", "Chẵn ≥ 11", "Lẻ ≥ 11"])
    col3, col4 = st.columns(2)
    with col3:
        lon_nho = st.selectbox("Lớn / Nhỏ nhiều hơn", ["Tất cả", "Lớn ≥ 11", "Nhỏ ≥ 11"])
    with col4:
        limit = st.slider("Số kỳ hiển thị", 10, 200, 50, step=10)

# Apply filters
filtered = df.copy()
if ky_search:
    filtered = filtered[filtered["ky"].astype(str).str.contains(ky_search)]
if chan_le == "Chẵn ≥ 11":
    filtered = filtered[filtered["chan"] >= 11]
elif chan_le == "Lẻ ≥ 11":
    filtered = filtered[filtered["le"] >= 11]
if lon_nho == "Lớn ≥ 11":
    filtered = filtered[filtered["lon"] >= 11]
elif lon_nho == "Nhỏ ≥ 11":
    filtered = filtered[filtered["nho"] >= 11]

filtered = filtered.head(limit)

# ── Table ────────────────────────────────────────────────────────────────────
st.subheader(f"📋 Danh sách kết quả ({len(filtered)} kỳ)")

# Format display
display = filtered.copy()
display.columns = ["Kỳ", "Ngày giờ", "20 số kết quả", "Chẵn", "Lẻ", "Lớn", "Nhỏ"]

st.dataframe(
    display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Kỳ":           st.column_config.NumberColumn(width="small"),
        "Ngày giờ":     st.column_config.TextColumn(width="medium"),
        "20 số kết quả": st.column_config.TextColumn(width="large"),
        "Chẵn":         st.column_config.NumberColumn(width="small"),
        "Lẻ":           st.column_config.NumberColumn(width="small"),
        "Lớn":          st.column_config.NumberColumn(width="small"),
        "Nhỏ":          st.column_config.NumberColumn(width="small"),
    }
)

# ── Stats ─────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("📊 Thống kê nhanh")

col1, col2, col3, col4 = st.columns(4)
col1.metric("TB Chẵn / kỳ", f"{df['chan'].mean():.1f}")
col2.metric("TB Lẻ / kỳ",   f"{df['le'].mean():.1f}")
col3.metric("TB Lớn / kỳ",  f"{df['lon'].mean():.1f}")
col4.metric("TB Nhỏ / kỳ",  f"{df['nho'].mean():.1f}")

# Biểu đồ chẵn/lẻ theo kỳ
st.line_chart(
    df.head(50).set_index("ky")[["chan", "le"]].sort_index(),
    color=["#4CAF50", "#FF5722"]
)
