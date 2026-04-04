import requests
from bs4 import BeautifulSoup
 
res = requests.get(
    'https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/view-detail-keno-result?id=0276332',
    headers={'User-Agent': 'Mozilla/5.0'}
)
soup = BeautifulSoup(res.text, 'html.parser')
 
# In toàn bộ text để xem cấu trúc
print(soup.get_text()[:3000])