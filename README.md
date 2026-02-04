# Mobile Media Organizer

A Python toolkit for organizing mobile media files (iOS & Android) with a **modern web dashboard** for real-time progress tracking and control.

## ✨ Features

- 📱 **Universal Mobile Support** - iOS (HEIC, MOV) and Android (JPG, MP4, etc.)
- 📅 **Date-Based Organization** - Auto-sorts media into `YYYY-MM` folders
- 📸 **Screenshot Detection** - Separates screenshots into dedicated folder
- 🌐 **Web Dashboard** - Premium UI with real-time progress tracking
- ⛔ **Abort Control** - Stop operations mid-execution
- 🔒 **Dry Run Mode** - Preview changes before executing
- 📊 **Job History** - Track all operations with detailed stats

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

![Dashboard Preview](docs/dashboard-preview.png)

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
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/jobs` | GET | List all jobs |
| `/jobs/{id}` | GET | Get job status |
| `/jobs/{id}/abort` | POST | Abort a running job |
| `/jobs/{id}/stream` | GET | SSE stream for progress |

### Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/media/organize` | POST | Organize media by date |
| `/media/subfolders` | POST | Expand to daily subfolders |
| `/android/clean` | POST | Clean Android backup |
| `/files/organize-types` | POST | Organize by file type |
| `/files/consolidate-pdfs` | POST | Collect all PDFs |
| `/files/analyze` | POST | Analyze extensions |

### Example: Start Operation with Tracking

```bash
# Start operation
curl -X POST http://localhost:8000/media/organize \
  -H "Content-Type: application/json" \
  -d '{"source_dir": "D:/Phone", "dest_dir": "D:/Organized", "dry_run": true}'

# Response: {"status": "started", "job_id": "abc123", ...}

# Track progress via SSE
curl http://localhost:8000/jobs/abc123/stream

# Or check status
curl http://localhost:8000/jobs/abc123

# Abort if needed
curl -X POST http://localhost:8000/jobs/abc123/abort
```

## 📁 Project Structure

```
Mobile-Media/
├── api/
│   ├── main.py              # FastAPI app entry point
│   ├── schemas.py           # Pydantic models
│   ├── routers/
│   │   ├── jobs.py          # Job management + SSE streaming
│   │   ├── media.py         # Media organization
│   │   ├── android.py       # Android cleanup
│   │   ├── files.py         # File operations
│   │   └── analysis.py      # Extension analysis
│   ├── services/
│   │   ├── job_manager.py   # Thread-safe job state manager
│   │   ├── core_logic.py    # File movement utilities
│   │   ├── media_service.py
│   │   ├── file_service.py
│   │   └── android_service.py
│   └── static/
│       ├── index.html       # Dashboard UI
│       ├── styles.css       # Premium dark theme
│       └── app.js           # Client-side app
├── scripts/                  # Standalone CLI utilities
├── organize_mobile_media.py  # Original CLI script
└── requirements.txt
```

## 🎨 Technology Stack

- **Backend**: FastAPI, Uvicorn, Pydantic
- **Frontend**: Vanilla HTML/CSS/JS (no build required)
- **Real-time**: Server-Sent Events (SSE)
- **Threading**: Thread-safe job management

## 📦 Supported File Types

| Category | Extensions |
|----------|------------|
| Photos | `.heic`, `.jpg`, `.jpeg`, `.dng`, `.webp`, `.png`, `.arw`, `.cr2`, `.nef` |
| Videos | `.mov`, `.mp4`, `.avi`, `.3gp`, `.mkv`, `.webm` |
| Other | `.gif`, `.aae` (Apple sidecar), `.plist` |

## ⚡ CLI Script (Alternative)

For quick operations without the dashboard:

```bash
python organize_mobile_media.py "D:\Phone Backup" "D:\Organized Photos"
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
