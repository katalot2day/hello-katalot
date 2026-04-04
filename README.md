# Hello Katalot — Demo App

Stack: **GitHub Actions** → **SQLite** → **Streamlit Cloud**

## Cấu trúc

```
hello-katalot/
├── fetch.py                      # Script chạy bởi GitHub Actions
├── app.py                        # Streamlit web app
├── requirements.txt
├── katalot.db                    # SQLite DB (được commit bởi Actions)
└── .github/workflows/fetch.yml   # Cron job mỗi 1 giờ
```

## Setup

### 1. Tạo GitHub repo & push code

```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/<user>/hello-katalot.git
git push -u origin main
```

### 2. Cấp quyền write cho Actions

Vào repo → **Settings** → **Actions** → **General**
→ `Workflow permissions` → chọn **Read and write permissions** → Save

### 3. Deploy lên Streamlit Cloud

1. Truy cập https://share.streamlit.io
2. **New app** → chọn repo `hello-katalot`
3. Main file: `app.py`
4. Deploy!

### 4. Chạy thủ công

Vào repo → tab **Actions** → `Fetch & Save Hello World` → **Run workflow**

## Flow hoạt động

```
GitHub Actions (cron 1h)
  → chạy fetch.py
  → insert "Hello World!" vào katalot.db
  → git commit & push katalot.db

Streamlit Cloud
  → đọc katalot.db từ repo
  → hiển thị bảng dữ liệu
```
