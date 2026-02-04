# Mobile Media Organizer

A Python toolkit for organizing mobile media files (iOS & Android) when transferred to your computer. Includes both **CLI scripts** for quick operations and a **FastAPI-based REST API** for integration with other tools.

## Features

- 📱 **Universal Mobile Support** - Works with iOS (HEIC, MOV) and Android (JPG, MP4, etc.)
- 📅 **Date-Based Organization** - Automatically sorts media into `YYYY-MM` folders
- 📸 **Screenshot Detection** - Separates screenshots into dedicated folder
- 🔒 **Safe Operations** - Dry-run mode to preview changes before executing
- 🌐 **REST API** - FastAPI server for programmatic control

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Mobile-Media.git
cd Mobile-Media

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### CLI Script

Organize mobile media files directly:

```bash
python organize_mobile_media.py "D:\Phone Backup" "D:\Organized Photos"
```

**What it does:**
- Moves photos/videos (`.jpg`, `.heic`, `.mp4`, `.dng`, etc.) → `YYYY-MM/` folders
- Moves screenshots (`.png`) → `Screenshots/` folder
- Handles filename collisions automatically

### REST API

Start the API server:

```bash
cd api
uvicorn main:app --reload
```

Then visit `http://localhost:8000/docs` for the interactive Swagger UI.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/media/organize` | POST | Organize media by date |
| `/media/expand-dates` | POST | Expand YYYY-MM folders into daily subfolders |
| `/android/clean` | POST | Clean Android backup cache |
| `/files/organize-by-type` | POST | Organize files by extension |
| `/analyze/extensions` | POST | Analyze file extensions in a directory |

### Example API Request

```bash
curl -X POST "http://localhost:8000/media/organize" \
  -H "Content-Type: application/json" \
  -d '{"source_dir": "D:/Phone", "dest_dir": "D:/Organized", "dry_run": true}'
```

## Project Structure

```
Mobile-Media/
├── organize_mobile_media.py   # Main CLI script
├── api/                       # FastAPI application
│   ├── main.py               # API entry point
│   ├── schemas.py            # Pydantic models
│   ├── routers/              # API route handlers
│   │   ├── media.py
│   │   ├── android.py
│   │   ├── files.py
│   │   └── analysis.py
│   └── services/             # Business logic
│       ├── core_logic.py
│       ├── media_service.py
│       ├── file_service.py
│       └── android_service.py
├── scripts/                   # Additional utility scripts
├── requirements.txt
└── README.md
```

## Supported File Types

| Category | Extensions |
|----------|------------|
| Photos | `.heic`, `.jpg`, `.jpeg`, `.dng`, `.webp`, `.png`, `.arw`, `.cr2`, `.nef` |
| Videos | `.mov`, `.mp4`, `.avi`, `.3gp`, `.mkv`, `.webm` |
| Other | `.gif`, `.aae` (Apple sidecar), `.plist` |

## Safety Features

- **Dry Run Mode**: Preview all operations before execution (API default)
- **Collision Handling**: Automatically renames files to prevent overwrites
- **Skip System Folders**: Ignores Windows system directories and hidden folders

## License

MIT License - see [LICENSE](LICENSE) for details.
