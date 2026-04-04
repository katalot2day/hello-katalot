import requests
from bs4 import BeautifulSoup
import re

def parse_prizes(soup):
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

for ky in [276330, 276331, 276332]:
    url = f"https://ketquaday.vn/ket-qua-keno-ky-{ky}"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    prizes = parse_prizes(soup)
    print(f"Ky {ky}: b10={prizes['b10']}")
