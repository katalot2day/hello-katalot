import sqlite3

DB_PATH = "katalot.db"

def init_dmgt():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS DMGT (
            trung  TEXT PRIMARY KEY,
            b10    INTEGER,
            b09    INTEGER,
            b08    INTEGER,
            b07    INTEGER,
            b06    INTEGER,
            b05    INTEGER,
            b04    INTEGER,
            b03    INTEGER,
            b02    INTEGER,
            b01    INTEGER
        )
    """)

    conn.execute("DELETE FROM DMGT")  # xóa data cũ nếu chạy lại

    data = [
        # trung, b10,     b09,    b08,    b07,   b06,   b05,  b04,  b03,  b02,  b01
        ("T10", 2000000, None,   None,   None,  None,  None, None, None, None, None),
        ("T09", 150000,  800000, None,   None,  None,  None, None, None, None, None),
        ("T08", 8000,    12000,  200000, None,  None,  None, None, None, None, None),
        ("T07", 710,     1500,   5000,   40000, None,  None, None, None, None, None),
        ("T06", 80,      150,    500,    1200,  12500, None, None, None, None, None),
        ("T05", 20,      30,     50,     100,   450,   4400, None, None, None, None),
        ("T04", None,    10,     10,     20,    40,    150,  400,  None, None, None),
        ("T03", None,    None,   None,   10,    10,    10,   50,   200,  None, None),
        ("T02", None,    None,   None,   None,  None,  10,   20,   90,   None, None),
        ("T01", None,    None,   None,   None,  None,  None, None, None, None, 20  ),
        ("T00", 10,      10,     10,     None,  None,  None, None, None, None, None),
    ]

    conn.executemany("""
        INSERT INTO DMGT (trung, b10, b09, b08, b07, b06, b05, b04, b03, b02, b01)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()

    # Verify
    rows = conn.execute("SELECT * FROM DMGT ORDER BY trung DESC").fetchall()
    print(f"✅ Tạo xong table DMGT — {len(rows)} dòng:")
    print(f"{'Trùng':>5} | {'B10':>8} | {'B09':>8} | {'B08':>8} | {'B07':>7} | {'B06':>7} | {'B05':>5} | {'B04':>5} | {'B03':>5} | {'B02':>5} | {'B01':>5}")
    print("-" * 95)
    for r in rows:
        vals = [str(v) if v is not None else "-" for v in r]
        print(f"{vals[0]:>5} | {vals[1]:>8} | {vals[2]:>8} | {vals[3]:>8} | {vals[4]:>7} | {vals[5]:>7} | {vals[6]:>5} | {vals[7]:>5} | {vals[8]:>5} | {vals[9]:>5} | {vals[10]:>5}")

    conn.close()

if __name__ == "__main__":
    init_dmgt()
