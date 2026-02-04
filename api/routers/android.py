from fastapi import APIRouter, HTTPException
from services import android_service
from schemas import AndroidRequest

router = APIRouter()

@router.post("/clean")
def clean_android_backup(request: AndroidRequest):
    """
    Clean Android backup folder by moving WhatsApp backups and large cache files.
    """
    result = android_service.clean_android_backup(
        request.source_dir,
        request.threshold_mb,
        request.dry_run
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
