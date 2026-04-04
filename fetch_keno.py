import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import time
from datetime import datetime

DB_PATH = "katalot.db"
BASE_URL = "https://ketquaday.vn/ket-qua-keno-ky-{}"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS KQKENO (
            ky        INTEGER PRIMARY KEY,
            ngay      TEXT,
            n20       TEXT,
            chan      INTEGER,
            le        INTEGER,
            lon       INTEGER,
            nho       INTEGER,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def ky_exists(ky_so):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT 1 FROM KQKENO WHERE ky = ?", (ky_so,)).fetchone()
    conn.close()
    return row is not None


def save_keno(data):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT OR IGNORE INTO KQKENO (ky, ngay, n20, chan, le, lon, nho, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["ky"],
        data["ngay"],
        data["n20"],
        data["chan"],
        data["le"],
        data["lon"],
        data["nho"],
        datetime.now().isoformat(),
    ))
    conn.commit()
    conn.close()


def fetch_keno(ky_so):
    url = BASE_URL.format(ky_so)
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if res.status_code != 200:
            print(f"  ⚠️  Kỳ {ky_so}: HTTP {res.status_code}")
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        # Lấy 20 số
        numbers = []
        for tag in soup.find_all(string=re.compile(r'^\d{2}$')):
            n = int(tag.strip())
            if 1 <= n <= 80:
                numbers.append(n)
        numbers = sorted(set(numbers))

        if len(numbers) != 20:
            print(f"  ⚠️  Kỳ {ky_so}: parse được {len(numbers)} số (cần 20)")
            return None

        # Lấy ngày giờ
        text = soup.get_text()
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{2}:\d{2})', text)
        ngay = date_match.group(1) if date_match else ""

        chan = len([n for n in numbers if n % 2 == 0])
        le   = len([n for n in numbers if n % 2 != 0])
        lon  = len([n for n in numbers if n > 40])
        nho  = len([n for n in numbers if n <= 40])

        return {
            "ky":   ky_so,
            "ngay": ngay,
            "n20":  " ".join(f"{n:02d}" for n in numbers),
            "chan":  chan,
            "le":   le,
            "lon":  lon,
            "nho":  nho,
        }

    except Exception as e:
        print(f"  ❌ Kỳ {ky_so}: {e}")
        return None


def get_latest_ky():
    """Lấy kỳ mới nhất đã lưu trong DB"""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT MAX(ky) FROM KQKENO").fetchone()
    conn.close()
    return row[0] if row[0] else None


def get_latest_ky_from_site():
    """Tự động lấy kỳ mới nhất từ ketquaday.vn"""
    try:
        res = requests.get(
            "https://ketquaday.vn/ket-qua-keno",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        matches = re.findall(r'ket-qua-keno-ky-(\d+)', res.text)
        if matches:
            latest = max(int(k) for k in matches)
            print(f"🌐 Kỳ mới nhất trên site: {latest}")
            return latest
    except Exception as e:
        print(f"⚠️  Không lấy được kỳ từ site: {e}")
    return None


def run(start_ky, end_ky):
    init_db()
    print(f"🚀 Fetch kỳ {start_ky} → {end_ky}")

    saved = 0
    skipped = 0

    for ky in range(start_ky, end_ky + 1):
        if ky_exists(ky):
            skipped += 1
            continue

        data = fetch_keno(ky)
        if data:
            save_keno(data)
            print(f"  ✅ Kỳ {ky} | {data['ngay']} | {data['n20']}")
            saved += 1
        else:
            print(f"  ⏭️  Kỳ {ky}: bỏ qua")

        time.sleep(0.5)  # tránh spam server

    print(f"\n✔️  Xong! Đã lưu: {saved} | Bỏ qua (đã có): {skipped}")


if __name__ == "__main__":
    init_db()

    # Kỳ mới nhất trong DB
    latest_db = get_latest_ky()

    # Kỳ mới nhất trên site
    latest_site = get_latest_ky_from_site()
    if not latest_site:
        print("❌ Không lấy được kỳ mới nhất từ site, dừng lại.")
        exit(1)

    # So sánh DB vs Site
    print(f"\n📊 So sánh:")
    print(f"   DB   : {latest_db if latest_db else 'trống'}")
    print(f"   Site : {latest_site}")

    if latest_db and latest_db >= latest_site:
        print(f"✅ DB đã cập nhật đầy đủ, không có kỳ mới.")
        exit(0)

    new_count = latest_site - (latest_db if latest_db else 276299)
    print(f"   Cần fetch thêm: {new_count} kỳ\n")

    start = (latest_db + 1) if latest_db else 276300
    run(start, latest_site)
