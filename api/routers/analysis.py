from fastapi import APIRouter, HTTPException
from services import file_service
from schemas import BaseRequest

router = APIRouter()

@router.post("/extensions")
def extensions_report(request: BaseRequest):
    """
    Get a statistical report of file extensions in the source directory.
    """
    result = file_service.analyze_extensions(request.source_dir)
    return result
