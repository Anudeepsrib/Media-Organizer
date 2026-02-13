# Mobile Media Organizer - Enterprise Edition

A Python toolkit for organizing mobile media files (iOS & Android) with a **Pro Max Web Dashboard** and **Enterprise-Grade Safety**.

## ✨ Features

- 📱 **Universal Mobile Support** - iOS (HEIC, MOV) and Android (JPG, MP4, etc.)
- 🛡️ **Safe Mode** - **Zero Data Loss** guarantee using "Copy-Verify-Delete" protocol
- 🎨 **Enterprise UI** - Professional Slate/Blue interface with sidebar navigation & glassmorphism
- 📅 **Date-Based Organization** - Auto-sorts media into `YYYY-MM` folders
- 📸 **Screenshot Detection** - Separates screenshots into dedicated folder
- 🌐 **Web Dashboard** - Real-time progress tracking with SSE
- ⛔ **Abort Control** - Graceful cancellation of running operations
- 🔒 **Dry Run Mode** - Preview changes before executing
- 📊 **Job History** - Track all operations with detailed logs
- 🤖 **AI-Powered** - Semantic search & auto-tagging (Gemini)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
git clone https://github.com/Startdust2024/Mobile-Media.git
cd Mobile-Media

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### 2. Configure Environment

The application uses a centralized `.env` file for configuration.

```bash
# Copy the example config
copy .env.example .env    # Windows
# cp .env.example .env    # macOS/Linux

# Edit .env to set your GEMINI_API_KEY
# GEMINI_API_KEY=your_key_here
```

### 3. Start the Application

```bash
cd api
uvicorn main:app --reload --port 8000
```

### 4. Access the Dashboard

Navigate to **http://localhost:8000** in your browser.

## � Project Structure

```
Mobile-Media/
├── api/
│   ├── main.py              # Backend Entry Point
│   ├── config.py            # Configuration Manager
│   ├── routers/             # API Endpoints
│   ├── services/            # Business Logic
│   └── .chromadb/           # Local Vector DB
├── frontend/                # Enterprise UI
│   ├── index.html           # Main Dashboard
│   ├── styles.css           # Slate/Blue Theme
│   └── app.js               # UI Logic
├── scripts/                 # Utilities
└── .env                     # Local Config (Gitignored)
```

## �🛡️ Safe Mode (Active by Default)

Unlike standard file movers, this tool uses a rigorous **Copy-Verify-Delete** strategy:
1.  **Copy**: Files are copied to the destination.
2.  **Verify**: SHA256 checksums of source and destination are compared.
3.  **Delete**: Source files are removed **only** if checksums match exactly.
4.  **Integrity**: If verification fails, the operation rolls back for that file.

*Safe Mode defaults to TRUE. You can toggle it per-operation in the dashboard.*

## 🎛️ Dashboard Operations

| Operation | Description |
|-----------|-------------|
| **Organize Media** | Sort photos/videos into YYYY-MM folders, separate screenshots |
| **Expand to Days** | Organize YYYY-MM folders into daily subfolders |
| **Clean Android** | Remove WhatsApp backups, cache, and junk files |
| **Organize by Type** | Sort installers and archives into categories |
| **Collect PDFs** | Find all PDFs and consolidate to one location |
| **Analyze** | Get file extension statistics (read-only) |

## 🤖 AI Features (Gemini-Powered)

The dashboard includes an **AI Tools** section powered by Google Gemini for intelligent media management.

| Feature | Description |
|---------|-------------|
| **Semantic Search** | Search images with natural language: *"photos of a sunset at the beach"* |
| **Index Library** | Batch-analyze your media library and store results locally |
| **Smart Suggest** | Get AI-powered folder organization recommendations |

### AI Setup
Ensure `GEMINI_API_KEY` is set in your `.env` file. Get a key at [Google AI Studio](https://aistudio.google.com/apikey).

### ⚠️ Data Privacy Notice
> **The AI features send image thumbnails (resized to max 512px) to the Google Gemini API for analysis.** No files are uploaded permanently. Image data is processed according to [Google's API Terms of Service](https://ai.google.dev/terms). All metadata is stored **locally** in ChromaDB.

## 🎨 Technology Stack

- **Backend**: FastAPI, Uvicorn, Pydantic Settings
- **AI**: Google Gemini (Vision), ChromaDB
- **Frontend**: Vanilla HTML/CSS/JS (Inter Typography)
- **Theme**: Enterprise Slate (Slate #0f172a + Blue #3b82f6)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
