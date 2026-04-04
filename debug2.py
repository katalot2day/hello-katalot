import requests
from bs4 import BeautifulSoup
import re

res = requests.get('https://ketquaday.vn/ket-qua-keno-ky-276316', headers={'User-Agent':'Mozilla/5.0'})
soup = BeautifulSoup(res.text, 'html.parser')
tables = soup.find_all('table')

b_keys = ["b10","b09","b08","b07","b06","b05","b04","b03","b02","b01"]

for idx, table in enumerate(tables[:10]):
    key = b_keys[idx]
    rows = table.find_all("tr")
    parts = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            match_so = re.search(r'Trùng\s+(\d+)', label)
            so_trung = f"{int(match_so.group(1)):02d}" if match_so else "00"
            match_sl = re.search(r'Số lượng[:\s]*(\d+)', value)
            so_luong = f"{int(match_sl.group(1)):02d}" if match_sl else "00"
            parts.append(f"{so_trung}-{so_luong}")
    print(f"{key}: {','.join(parts)}")