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

### 2. Start the Dashboard

```bash
cd api
uvicorn main:app --reload --port 8000
```

### 3. Open the Dashboard

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

## 🎨 Technology Stack

- **Backend**: FastAPI, Uvicorn, Pydantic, Python `hashlib`
- **Frontend**: Vanilla HTML/CSS/JS (Fira Sans/Code Typography)
- **Theme**: OLED Dark Mode (True Black #000000 + Neon Accents)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
