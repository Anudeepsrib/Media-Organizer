from fastapi import APIRouter, HTTPException, BackgroundTasks
from services import media_service
from services.job_manager import job_manager
from schemas import MediaRequest, BaseRequest

router = APIRouter()


def run_media_organize(source_dir: str, dest_dir: str, dry_run: bool, job_id: str, safe_mode: bool):
    """Background task for media organization."""
    try:
        media_service.organize_media_by_date(source_dir, dest_dir, dry_run, job_id, safe_mode)
    except Exception as e:
        job_manager.fail_job(job_id, str(e))


def run_expand_dates(source_dir: str, dry_run: bool, job_id: str, safe_mode: bool):
    """Background task for date expansion."""
    try:
        media_service.organize_expanded_dates(source_dir, dry_run, job_id, safe_mode)
    except Exception as e:
        job_manager.fail_job(job_id, str(e))


@router.post("/organize")
def organize_media(request: MediaRequest, background_tasks: BackgroundTasks):
    """
    Organize photos and videos into YYYY-MM folders and separate screenshots.
    Returns immediately with a job_id for progress tracking.
    """
    # Create job
    job_id = job_manager.create_job("media_organize")
    
    # Start background task
    background_tasks.add_task(
        run_media_organize,
        request.source_dir,
        request.dest_dir,
        request.dry_run,
        job_id,
        request.safe_mode
    )
    
    return {
        "status": "started",
        "job_id": job_id,
        "message": f"Media organization started. Track progress at /jobs/{job_id}"
    }


@router.post("/subfolders")
def organize_subfolders(request: BaseRequest, background_tasks: BackgroundTasks):
    """
    Organize files within existing YYYY-MM folders into DD subfolders.
    Returns immediately with a job_id for progress tracking.
    """
    # Create job
    job_id = job_manager.create_job("expand_dates")
    
    # Start background task
    background_tasks.add_task(
        run_expand_dates,
        request.source_dir,
        request.dry_run,
        job_id,
        request.safe_mode
    )
    
    return {
        "status": "started",
        "job_id": job_id,
        "message": f"Date expansion started. Track progress at /jobs/{job_id}"
    }
