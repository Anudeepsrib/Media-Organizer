from pydantic import BaseModel, Field
from typing import Optional

class BaseRequest(BaseModel):
    source_dir: str = Field(..., description="Absolute path to the source directory")
    dry_run: bool = Field(True, description="If true, no files will be moved")
    safe_mode: bool = Field(True, description="If true, use copy-verify-delete instead of move")

class MediaRequest(BaseRequest):
    dest_dir: str = Field(..., description="Destination base directory for media")

class AndroidRequest(BaseRequest):
    threshold_mb: int = Field(50, description="Size threshold for suspected cache files in MB")

class FileTypeRequest(BaseRequest):
    dest_dir: str = Field(..., description="Destination base directory")

class PDFRequest(BaseRequest):
    dest_dir: str = Field(..., description="Destination directory for consolidated PDFs")


# --- AI Request Models ---

class AIIndexRequest(BaseModel):
    source_dir: str = Field(..., description="Directory to index with AI analysis")
    force_reindex: bool = Field(False, description="Re-analyze files even if already indexed")

class AISearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(10, description="Number of results to return", ge=1, le=100)
    source_dir: Optional[str] = Field(None, description="Optional: limit search to this directory")

class AIAnalyzeRequest(BaseModel):
    file_path: str = Field(..., description="Absolute path to the file or directory to analyze")

