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
        dmgt = pd.read_sql("SELECT * FROM DMGT", conn)
        conn.close()
        return df, dmgt
    except Exception as e:
        return None, None

df, dmgt = load_data()

if df is None or df.empty:
    st.error("Không đọc được DB. Hãy chạy `python fetch_keno.py` trước.")
    st.stop()

# DMGT lookup
dmgt_map = {}
for _, row in dmgt.iterrows():
    trung = row["trung"]
    dmgt_map[trung] = {f"b{i:02d}": row[f"b{i:02d}"] for i in range(1, 11)}

B_COLS = [f"b{i:02d}" for i in range(10, 0, -1)]
T_ROWS = [f"T{i:02d}" for i in range(10, 0, -1)]  # T10→T01

def parse_bxx(s):
    result = {}
    if not s:
        return result
    for part in s.split(","):
        if "-" in part:
            so_trung, so_luong = part.split("-", 1)
            result[int(so_trung)] = int(so_luong)
    return result

def calc_tien_bxx(parsed, b_col):
    total = 0
    for so_trung, so_luong in parsed.items():
        t_key = f"T{so_trung:02d}"
        dm = dmgt_map.get(t_key, {}).get(b_col)
        if dm and so_luong > 0:
            total += so_luong * dm
    return total

def has_dmgt(t_row, b_col):
    return dmgt_map.get(t_row, {}).get(b_col) is not None

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng số kỳ",        f"{len(df):,}")
col2.metric("Kỳ mới nhất",       df["ky"].iloc[0])
col3.metric("Kỳ cũ nhất",        df["ky"].iloc[-1])
col4.metric("Cập nhật lần cuối", df["ngay"].iloc[0])

st.divider()

tab1, tab2 = st.tabs(["📋 Kết quả", "🏆 Giải thưởng"])

with tab1:
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
    )

with tab2:
    col1, col2 = st.columns([2, 1])
    with col1:
        ky_search2 = st.text_input("🔍 Tìm theo kỳ", placeholder="VD: 276300", key="tab2_search")
    with col2:
        limit2 = st.slider("Số kỳ hiển thị", 5, 50, 10, step=5, key="tab2_limit")

    filtered2 = df.copy()
    if ky_search2:
        filtered2 = filtered2[filtered2["ky"].astype(str).str.contains(ky_search2)]
    filtered2 = filtered2.head(limit2)

    st.markdown("""
    <style>
    .keno-table { width:100%; border-collapse:collapse; font-size:13px; }
    .keno-table td, .keno-table th {
        border: 1px solid #ccc;
        padding: 3px 8px;
        text-align: center;
        white-space: nowrap;
        background: white;
        color: black;
    }
    .keno-table th {
        background: #333;
        color: white;
        text-align: center;
    }
    .row-header td {
        background: #4CAF50 !important;
        color: black !important;
        font-weight: bold;
        text-align: center !important;
    }
    .cell-yellow { background: #FFD700 !important; color: black !important; }
    .cell-orange { background: #FF8C00 !important; color: black !important; }
    .cell-white  { background: white !important; }
    .col-label   { text-align: center !important; color: #666; }
    </style>
    """, unsafe_allow_html=True)

    html = '<table class="keno-table"><tr>'
    html += '<th>Ngày</th><th>Kỳ</th><th>BTT</th>'
    for b in B_COLS:
        html += f'<th>{b.upper()}</th>'
    html += '</tr>'

    for _, row in filtered2.iterrows():
        parsed    = {b: parse_bxx(row[b]) for b in B_COLS}
        tien_bxx  = {b: calc_tien_bxx(parsed[b], b) for b in B_COLS}
        btt       = sum(tien_bxx.values())

        # Dòng header kỳ (xanh lá)
        html += '<tr class="row-header">'
        html += f'<td>{row["ngay"]}</td><td>{row["ky"]}</td>'
        html += f'<td>{btt:,.0f}</td>'
        for b in B_COLS:
            val = f'{tien_bxx[b]:,.0f}' if tien_bxx[b] > 0 else ''
            html += f'<td>{val}</td>'
        html += '</tr>'

        # Dòng chi tiết T10→T01
        for t_num in range(10, 0, -1):
            t_key  = f"T{t_num:02d}"
            is_t05 = (t_num == 5)
            html  += '<tr>'
            html  += '<td class="cell-white"></td><td class="cell-white"></td>'
            html  += f'<td class="col-label">{t_key}</td>'
            for b in B_COLS:
                sl = parsed[b].get(t_num, 0)
                if not has_dmgt(t_key, b):
                    # Ô không hợp lệ theo DMGT → trắng
                    html += '<td class="cell-white"></td>'
                elif is_t05:
                    # Hàng T05 → cam
                    html += f'<td class="cell-orange">{sl if sl > 0 else ""}</td>'
                else:
                    # Ô hợp lệ → vàng
                    html += f'<td class="cell-yellow">{sl if sl > 0 else ""}</td>'
            html += '</tr>'

    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)
