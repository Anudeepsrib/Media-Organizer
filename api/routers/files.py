from fastapi import APIRouter, HTTPException
from services import file_service
from schemas import PDFRequest, FileTypeRequest, BaseRequest

router = APIRouter()

@router.post("/consolidate-pdfs")
def consolidate_pdfs(request: PDFRequest):
    """
    Find and move all PDFs to a single folder.
    """
    result = file_service.collect_pdfs(
        request.source_dir,
        request.dest_dir,
        request.dry_run
    )
    return result

@router.post("/organize-types")
def organize_by_type(request: FileTypeRequest):
    """
    Organize Installers and Archives into specific folders.
    """
    result = file_service.organize_files_by_type(
        request.source_dir,
        request.dest_dir,
        request.dry_run
    )
    return result

@router.post("/analyze")
def analyze_extensions(request: BaseRequest):
    """
    Analyze file extensions in the directory.
    """
    # Note: request.dry_run is ignored for analysis as it's read-only
    result = file_service.analyze_extensions(request.source_dir)
    return result
