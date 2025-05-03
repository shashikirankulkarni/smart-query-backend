# 🤖 Smart Query Bot (FastAPI Backend)

Smart Query Bot is a secure, API-based chatbot backend that allows users to query Excel/CSV/Google Sheets using natural language. The backend uses Cohere's LLM + SentenceTransformer-based semantic search to match questions from the uploaded file.

## 🔧 Features

- ✅ Sync a public Excel/CSV/Google Sheet URL (`/sync`)
- ✅ Ask questions based on synced sheet data (`/query`)
- 🔒 Bearer Token-based authentication for all endpoints
- 🧠 Semantic search with Sentence Transformers
- 💬 LLM response generation using Cohere `command-r` model
- ⚙️ Modular and production-ready architecture

---

## 📁 Project Structure

```
app/
├── api/
│   └── endpoints.py         # API route definitions
├── auth/
│   └── dependencies.py      # Bearer token validation
├── models/
│   └── schemas.py           # Request/response models
├── services/
│   ├── query_service.py     # Handles querying logic
│   └── sync_service.py      # Sheet syncing and validation
├── state/
│   └── cache.py             # Tracks synced URLs
├── utils/
│   └── sheet_loader.py      # Downloads and parses sheets
main.py                      # FastAPI app entrypoint
```

---

## 🚀 API Endpoints

All endpoints require a valid `Bearer Token` in the `Authorization` header.

### 🔍 `/sync`  
Syncs and validates a sheet URL before querying.

**POST** `/sync`

```json
{
  "sheet_url": "https://docs.google.com/spreadsheets/d/your-id/edit"
}
```

Response:
```json
{
  "columns": ["Question", "Answer"],
  "row_count": 23
}
```

---

### 💬 `/query`  
Ask a question based on the synced sheet data.

**POST** `/query`

```json
{
  "sheet_url": "https://docs.google.com/spreadsheets/d/your-id/edit",
  "question": "How do I reset my password?"
}
```

Response:
```json
{
  "answer": "Go to settings and click 'Reset Password'."
}
```

---

### ✅ `/health`  
Health check endpoint to validate API status.

**GET** `/health`

Headers:
```
Authorization: Bearer <your-token>
```

---

## 🔐 Authentication

All endpoints are protected via a simple Bearer Token system.

### Setting Token (locally)
```bash
export BEARER_TOKEN="your-secure-token"
export COHERE_API_KEY="your-cohere-key"
```

---

## 📦 Setup & Run (Local)

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-org/smart-query-backend.git
   cd smart-query-backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 🌍 Deployment

This backend is ready for deployment on:

- [✅ Render.com](https://render.com) *(tested and verified)*
- [Heroku](https://heroku.com)
- [Fly.io](https://fly.io)
- Any Docker-compatible service

> Ensure environment variables are securely set before deploying:
- `COHERE_API_KEY`
- `BEARER_TOKEN`

---

## 🧠 Technologies Used

- FastAPI
- Cohere LLM (`command-r`)
- SentenceTransformers (`MiniLM`)
- Pandas + Requests
- OpenAPI + Swagger Docs

---

## 👨‍💻 Author

Built with ❤️ by Shashikiran Kulkarni

---

## 📄 License

MIT License. Free to use with attribution.
