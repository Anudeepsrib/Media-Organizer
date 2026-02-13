# Mobile Media Organizer

A Python toolkit for organizing mobile media files (iOS & Android) with a **Pro Max Web Dashboard** and **Enterprise-Grade Safety**.

## ✨ Features

- 📱 **Universal Mobile Support** - iOS (HEIC, MOV) and Android (JPG, MP4, etc.)
- 🛡️ **Safe Mode** - **Zero Data Loss** guarantee using "Copy-Verify-Delete" protocol
- 🎨 **OLED Dark UI** - Premium "Pro Max" interface with True Black background
- 📅 **Date-Based Organization** - Auto-sorts media into `YYYY-MM` folders
- 📸 **Screenshot Detection** - Separates screenshots into dedicated folder
- 🌐 **Web Dashboard** - Real-time progress tracking with SSE
- ⛔ **Abort Control** - Graceful cancellation of running operations
- 🔒 **Dry Run Mode** - Preview changes before executing
- 📊 **Job History** - Track all operations with detailed logs

## 🚀 Quick Start

### 1. Install Dependencies

```bash
git clone https://github.com/yourusername/Mobile-Media.git
cd Mobile-Media

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example config and fill in your values
cp .env.example .env        # macOS/Linux
# copy .env.example .env    # Windows

# Edit .env and set at minimum:
#   GEMINI_API_KEY=your_key_here
```

### 3. Start the Dashboard

```bash
cd api
uvicorn main:app --reload --port 8000
```

### 4. Open the Dashboard

Navigate to **http://localhost:8000** in your browser.

## 🛡️ Safe Mode (Active by Default)

Unlike standard file movers, this tool uses a rigorous **Copy-Verify-Delete** strategy:
1.  **Copy**: Files are copied to the destination.
2.  **Verify**: SHA256 checksums of source and destination are compared.
3.  **Delete**: Source files are removed **only** if checksums match exactly.
4.  **Integrity**: If verification fails, the operation rolls back for that file.

*You can toggle Safe Mode off in the configuration panel for faster (but less secure) standard moves.*

## 🎛️ Dashboard Operations

| Operation | Description |
|-----------|-------------|
| **Organize Media** | Sort photos/videos into YYYY-MM folders, separate screenshots |
| **Expand to Days** | Organize YYYY-MM folders into daily subfolders |
| **Clean Android** | Remove WhatsApp backups, cache, and junk files |
| **Organize by Type** | Sort installers and archives into categories |
| **Collect PDFs** | Find all PDFs and consolidate to one location |
| **Analyze** | Get file extension statistics (read-only) |

## 🔌 API Endpoints

All operations return a `job_id` for real-time tracking via SSE.

### Job Management
- `GET /jobs` - List jobs
- `GET /jobs/{id}` - Get status
- `POST /jobs/{id}/abort` - Stop job
- `GET /jobs/{id}/stream` - SSE Stream

### Operations
- `POST /media/organize` (supports `safe_mode: bool`)
- `POST /media/subfolders`
- `POST /android/clean`
- `POST /files/*`

## 📁 Project Structure

```
Mobile-Media/
├── api/
│   ├── main.py              # FastAPI app
│   ├── schemas.py           # Pydantic models (with SafeMode)
│   ├── routers/             # API Endpoints
│   ├── services/
│   │   ├── core_logic.py    # Safe Move Logic (Checksums)
│   │   └── ...
│   └── static/              # OLED UI (HTML/CSS/JS)
├── scripts/                 # Utilities
└── requirements.txt
```

## 🤖 AI Features (Gemini-Powered)

The dashboard includes an **AI Tools** section powered by Google Gemini for intelligent media management.

| Feature | Description |
|---------|-------------|
| **Semantic Search** | Search images with natural language: *"photos of a sunset at the beach"* |
| **Auto-Tagging** | AI-generated labels for scene, objects, quality, and more |
| **Index Library** | Batch-analyze your media library and store results locally |
| **Smart Suggest** | Get AI-powered folder organization recommendations |

### AI Setup

```bash
# Set your Gemini API key (get one at https://aistudio.google.com/apikey)
set GEMINI_API_KEY=your_api_key_here   # Windows
# export GEMINI_API_KEY=your_api_key_here  # macOS/Linux
```

### AI API Endpoints

- `POST /ai/index` — Index a media directory (background job)
- `POST /ai/search` — Semantic search across indexed media
- `POST /ai/analyze` — Analyze a single image file
- `POST /ai/suggestions` — Get AI folder recommendations

### ⚠️ Data Privacy Notice

> **The AI features send image thumbnails (resized to max 512px) to the Google Gemini API for analysis.** No files are uploaded permanently — only transient API calls are made. Image data is processed according to [Google's API Terms of Service](https://ai.google.dev/terms). If you are working with sensitive or private media, review Google's data usage policies before enabling AI features. All AI-generated metadata is stored **locally** in a ChromaDB database (`api/.chromadb/`) and never leaves your machine.

## 🎨 Technology Stack

- **Backend**: FastAPI, Uvicorn, Pydantic, Python `hashlib`
- **AI**: Google Gemini (Vision + Embeddings), ChromaDB, Pillow
- **Frontend**: Vanilla HTML/CSS/JS (Inter/JetBrains Mono Typography)
- **Theme**: OLED Dark Mode (True Black #000000 + Neon Accents)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
