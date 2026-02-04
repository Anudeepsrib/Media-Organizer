from pydantic import BaseModel, Field
from typing import Optional

class BaseRequest(BaseModel):
    source_dir: str = Field(..., description="Absolute path to the source directory")
    dry_run: bool = Field(True, description="If true, no files will be moved")

class MediaRequest(BaseRequest):
    dest_dir: str = Field(..., description="Destination base directory for media")

class AndroidRequest(BaseRequest):
    threshold_mb: int = Field(50, description="Size threshold for suspected cache files in MB")

class FileTypeRequest(BaseRequest):
    dest_dir: str = Field(..., description="Destination base directory")

class PDFRequest(BaseRequest):
    dest_dir: str = Field(..., description="Destination directory for consolidated PDFs")
