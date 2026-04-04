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
            ky         INTEGER PRIMARY KEY,
            ngay       TEXT,
            n20        TEXT,
            b10        TEXT,
            b09        TEXT,
            b08        TEXT,
            b07        TEXT,
            b06        TEXT,
            b05        TEXT,
            b04        TEXT,
            b03        TEXT,
            b02        TEXT,
            b01        TEXT,
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
        INSERT OR IGNORE INTO KQKENO
            (ky, ngay, n20, b10, b09, b08, b07, b06, b05, b04, b03, b02, b01, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["ky"], data["ngay"], data["n20"],
        data["b10"], data["b09"], data["b08"], data["b07"],
        data["b06"], data["b05"], data["b04"], data["b03"],
        data["b02"], data["b01"],
        datetime.now().isoformat(),
    ))
    conn.commit()
    conn.close()


def parse_prizes(soup):
    """
    Parse giai thuong tung loai ve B10->B01.
    Format luu: "10-00,09-00,08-01,..." (so_trung-so_luong)
    """
    prizes = {f"b{i:02d}": "" for i in range(1, 11)}
    b_keys = ["b10", "b09", "b08", "b07", "b06", "b05", "b04", "b03", "b02", "b01"]

    tables = soup.find_all("table")
    for idx, table in enumerate(tables[:10]):
        key = b_keys[idx]
        rows = table.find_all("tr")
        parts = []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                match_so = re.search(r'Trung\s+(\d+)|Trùng\s+(\d+)', label)
                if match_so:
                    so_trung = f"{int(match_so.group(1) or match_so.group(2)):02d}"
                else:
                    so_trung = "00"
                match_sl = re.search(r'S[oố]\s*l[uư][oợ]ng[:\s]*(\d+)', value)
                so_luong = f"{int(match_sl.group(1)):02d}" if match_sl else "00"
                parts.append(f"{so_trung}-{so_luong}")
        prizes[key] = ",".join(parts)

    return prizes


def fetch_keno(ky_so):
    url = BASE_URL.format(ky_so)
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if res.status_code != 200:
            print(f"  Ky {ky_so}: HTTP {res.status_code}")
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        # Lay 20 so ket qua
        numbers = []
        for tag in soup.find_all(string=re.compile(r'^\d{2}$')):
            n = int(tag.strip())
            if 1 <= n <= 80:
                numbers.append(n)
        numbers = sorted(set(numbers))

        if len(numbers) != 20:
            print(f"  Ky {ky_so}: parse duoc {len(numbers)} so (can 20)")
            return None

        # Lay ngay gio
        text = soup.get_text()
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{2}:\d{2})', text)
        ngay = date_match.group(1) if date_match else ""

        prizes = parse_prizes(soup)

        return {
            "ky":   ky_so,
            "ngay": ngay,
            "n20":  " ".join(f"{n:02d}" for n in numbers),
            **prizes,
        }

    except Exception as e:
        print(f"  Ky {ky_so}: {e}")
        return None


def get_latest_ky():
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT MAX(ky) FROM KQKENO").fetchone()
    conn.close()
    return row[0] if row[0] else None


def get_latest_ky_from_site():
    try:
        res = requests.get(
            "https://ketquaday.vn/ket-qua-keno",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        matches = re.findall(r'ket-qua-keno-ky-(\d+)', res.text)
        if matches:
            latest = max(int(k) for k in matches)
            print(f"Ky moi nhat tren site: {latest}")
            return latest
    except Exception as e:
        print(f"Khong lay duoc ky tu site: {e}")
    return None


def run(start_ky, end_ky):
    init_db()
    print(f"Fetch ky {start_ky} -> {end_ky}")
    saved = skipped = 0

    for ky in range(start_ky, end_ky + 1):
        if ky_exists(ky):
            skipped += 1
            continue
        data = fetch_keno(ky)
        if data:
            save_keno(data)
            print(f"  OK Ky {ky} | {data['ngay']} | {data['n20']}")
            saved += 1
        else:
            print(f"  Bo qua ky {ky}")
        time.sleep(0.5)

    print(f"\nXong! Da luu: {saved} | Bo qua (da co): {skipped}")


if __name__ == "__main__":
    init_db()

    latest_db   = get_latest_ky()
    latest_site = get_latest_ky_from_site()

    if not latest_site:
        print("Khong lay duoc ky moi nhat tu site, dung lai.")
        exit(1)

    print(f"\nSo sanh:")
    print(f"  DB   : {latest_db if latest_db else 'trong'}")
    print(f"  Site : {latest_site}")

    if latest_db and latest_db >= latest_site:
        print("DB da cap nhat day du, khong co ky moi.")
        exit(0)

    new_count = latest_site - (latest_db if latest_db else 276299)
    print(f"  Can fetch them: {new_count} ky\n")

    start = (latest_db + 1) if latest_db else 276300
    run(start, latest_site)