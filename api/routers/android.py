from fastapi import APIRouter, BackgroundTasks
from services import android_service
from services.job_manager import job_manager
from schemas import AndroidRequest

router = APIRouter()


def run_clean_android(source_dir: str, threshold_mb: int, dry_run: bool, job_id: str):
    """Background task for Android cleanup."""
    try:
        android_service.clean_android_backup(source_dir, threshold_mb, dry_run, job_id)
    except Exception as e:
        job_manager.fail_job(job_id, str(e))


@router.post("/clean")
def clean_android_backup(request: AndroidRequest, background_tasks: BackgroundTasks):
    """
    Clean Android backup folder by moving WhatsApp backups and large cache files.
    Returns immediately with a job_id for progress tracking.
    """
    job_id = job_manager.create_job("android_clean")
    
    background_tasks.add_task(
        run_clean_android,
        request.source_dir,
        request.threshold_mb,
        request.dry_run,
        job_id
    )
    
    return {
        "status": "started",
        "job_id": job_id,
        "message": f"Android cleanup started. Track progress at /jobs/{job_id}"
    }
