# Event Ticketing MCP

AI Agent berbasis **Model Context Protocol (MCP)** untuk sistem Event Ticketing. Agent ini memungkinkan user berinteraksi dengan sistem ticketing menggunakan bahasa natural — mencari event, mengecek ketersediaan tiket, membuat order, hingga mengecek status order.

---

## Arsitektur

```
Next.js Frontend
    │
    │  POST /chat  (message + JWT token)
    ▼
MCP Client (FastAPI)          ──────►  LLM via OpenRouter
    │                                   (tool-calling loop)
    │  stdio
    ▼
MCP Server (FastMCP)
    │
    │  HTTP + JWT Bearer
    ▼
Spring Boot REST API
    │
    ▼
PostgreSQL
```

Alur per request:
1. Frontend kirim pesan user beserta JWT token ke MCP Client
2. MCP Client jalankan tool-calling loop bersama LLM via OpenRouter
3. LLM putuskan tool mana yang perlu dipanggil
4. MCP Client inject token lalu kirim ke MCP Server via stdio
5. MCP Server eksekusi tool — manggil Spring Boot REST API dengan Bearer token
6. Hasil tool dikirim balik ke LLM untuk diformat jadi respons natural
7. Respons final dikembalikan ke frontend

Token tidak pernah disimpan di server — hanya mengalir per request.

---

## Tech Stack

| Layer | Teknologi |
|---|---|
| MCP Server | Python, FastMCP |
| MCP Client | Python, FastAPI, AsyncOpenAI |
| LLM | OpenRouter (OpenAI-compatible) |
| Backend API | Java Spring Boot |
| Database | PostgreSQL |
| Frontend | Next.js (TypeScript) |

---

## Struktur Folder

```
event-ticketing-mcp/
├── server/
│   ├── server.py           # FastMCP server — register semua tools
│   ├── api_client.py       # HTTP client ke Spring Boot
│   ├── schemas.py          # Pydantic models input/output tools
│   └── utils/
│       ├── __init__.py
│       └── status_order.py # Status map PENDING/PAID/CANCELLED
├── client/
│   ├── main.py             # FastAPI app — endpoint POST /chat
│   ├── client.py           # Tool-calling loop (run_agent)
│   ├── schemas.py          # ChatRequest, ChatResponse
│   └── utils/
│       ├── __init__.py
│       └── system_prompt.py
├── .env
├── requirements.txt
└── README.md
```

---

## Tools MCP

| Tool | Deskripsi | Endpoint Spring Boot |
|---|---|---|
| `search_event` | Cari event berdasarkan nama | `GET /api/events/search?nama=` |
| `get_event_availability` | Detail informasi sebuah event | `GET /api/events/{id}` |
| `get_ticket_category_event` | Daftar kategori tiket + sisa kuota | `GET /api/events/{id}/tiket-kategori` |
| `create_order` | Buat order tiket baru | `POST /api/orders` |
| `check_order_status` | Cek status order | `GET /api/orders/{id}` |

Token JWT di-inject otomatis ke setiap tool call — user tidak perlu tahu UUID atau token apapun.

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ (untuk MCP Inspector)
- Spring Boot API sudah berjalan
- OpenRouter API key

### Instalasi

```bash
# Clone repository
git clone https://github.com/Aldinokhalifah/event-ticketing-mcp.git
cd event-ticketing-mcp

# Buat virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Buat file `.env` di root folder:

```env
API_BASE_URL=
FRONTEND_BASE_URL=
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_model_name
```

Untuk memilih model OpenRouter yang support tool calling, cek di [openrouter.ai/models](https://openrouter.ai/models) dengan filter `supported_parameters=tools`.

---

## Menjalankan

### 1. MCP Server (untuk testing via MCP Inspector)

```bash
cd server
python server.py
```

### 2. MCP Client (FastAPI)

```bash
cd client
uvicorn main:app --reload --port 8001
```

FastAPI docs tersedia di `http://localhost:8001/docs`

---

## Testing

### Tahap 1 — Tes MCP Server via MCP Inspector

```bash
cd server
npx @modelcontextprotocol/inspector python server.py
```

Buka `http://localhost:6274` lalu:
- Pastikan 5 tools terdaftar di tab **Tools**
- Tes tiap tool manual dengan mengisi `event_id`/`token` yang valid

### Tahap 2 — Tes End-to-End via Postman

```bash
POST http://localhost:8001/chat
Content-Type: application/json

{
  "message": "cari event chelsea dan tampilkan tiket yang tersedia",
  "token": "eyJhbGci...",
  "conversation_history": []
}
```

Contoh response:

```json
{
  "response": "Ditemukan event Chelsea VS AC Milan di Stadion GBK...",
  "actions_taken": ["search_event", "get_ticket_category_event"]
}
```

### Contoh Percakapan

```
User  : "ada event apa minggu ini?"
Agent : memanggil search_event → tampilkan daftar event

User  : "cek tiket untuk Chelsea VS AC Milan"
Agent : memanggil search_event → get_ticket_category_event → tampilkan kategori + sisa kuota

User  : "order 2 tiket Premium"
Agent : memanggil create_order → tampilkan kode order + total harga

User  : "cek status orderku"
Agent : memanggil check_order_status → tampilkan status dalam bahasa Indonesia
```

---

## Catatan Pengembangan

**Error handling** — Semua error dari Spring Boot ditranslate jadi pesan ramah sebelum sampai ke AI. Contoh: stok habis → *"Kuota tiket tidak mencukupi"*, bukan stack trace mentah.

**Token management** — JWT token tidak pernah disimpan di server MCP. Token diterima per request dari frontend dan hanya hidup selama satu siklus request-response.

**AI safety** — Parameter `token` disembunyikan dari schema tools yang dilihat AI, sehingga AI tidak pernah tahu keberadaan token dan tidak akan memintanya ke user.

**Max iterations** — Tool-calling loop dibatasi maksimal 6 iterasi untuk mencegah infinite loop.