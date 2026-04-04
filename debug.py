import requests
from bs4 import BeautifulSoup

res = requests.get('https://ketquaday.vn/ket-qua-keno-ky-276316', headers={'User-Agent':'Mozilla/5.0'})
soup = BeautifulSoup(res.text, 'html.parser')
tables = soup.find_all('table')
print(f'So bang: {len(tables)}')
for i, t in enumerate(tables):
    print(f'Bang {i}: {t.get_text(strip=True)[:80]}')