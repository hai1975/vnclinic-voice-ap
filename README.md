# VN Clinic AI — Voice API

Backend FastAPI độc lập cho **hai1975.com/VNClinicAI**.

Mint ephemeral token Gemini Live — `GEMINI_API_KEY` chỉ lưu trên server (Render), không expose ra browser.

> **Không liên quan** tới repo [VMC](https://hai1975.com/VMC/) — đó là dự án form voice riêng.

## API

| Method | Path | Mô tả |
|--------|------|--------|
| GET | `/api/health` | Health check |
| POST | `/api/demo/live-token` | Body: `{ "demo_id": "01".."08", "language": "vi" \| "en" }` |

## Chạy local

```bash
cd voice-api
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # điền GEMINI_API_KEY
uvicorn app.main:app --port 8001 --reload
```

## Deploy Render

1. Tạo repo GitHub mới (vd: `hai1975/vnclinic-voice-api`)
2. Push **toàn bộ thư mục này** (đây là root repo, không phải subfolder)
3. Render → New → Blueprint hoặc Docker Web Service
4. Env: `GEMINI_API_KEY`, `CORS_ORIGINS=https://hai1975.com,https://www.hai1975.com`

## Frontend kết nối

Trong repo VNClinicAI (frontend), set trước khi build:

```
VITE_VOICE_API_BASE=https://<your-service>.onrender.com
```
