from fastapi import APIRouter, HTTPException
from services import media_service
from schemas import MediaRequest, BaseRequest

router = APIRouter()

@router.post("/organize")
def organize_media(request: MediaRequest):
    """
    Organize photos and videos into YYYY-MM folders and separate screenshots.
    """
    result = media_service.organize_media_by_date(
        request.source_dir, 
        request.dest_dir, 
        request.dry_run
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/subfolders")
def organize_subfolders(request: BaseRequest):
    """
    Organize files within existing YYYY-MM folders into DD subfolders.
    """
    result = media_service.organize_expanded_dates(
        request.source_dir,
        request.dry_run
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
