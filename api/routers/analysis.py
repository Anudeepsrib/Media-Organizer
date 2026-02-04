from fastapi import APIRouter, BackgroundTasks
from services import file_service
from services.job_manager import job_manager
from schemas import BaseRequest

router = APIRouter()


def run_extensions_report(source_dir: str, job_id: str):
    """Background task for extension analysis."""
    try:
        file_service.analyze_extensions(source_dir, job_id)
    except Exception as e:
        job_manager.fail_job(job_id, str(e))


@router.post("/extensions")
def extensions_report(request: BaseRequest, background_tasks: BackgroundTasks):
    """
    Get a statistical report of file extensions in the source directory.
    Returns immediately with a job_id for progress tracking.
    """
    job_id = job_manager.create_job("extensions_report")
    
    background_tasks.add_task(
        run_extensions_report,
        request.source_dir,
        job_id
    )
    
    return {
        "status": "started",
        "job_id": job_id,
        "message": f"Extension analysis started. Track progress at /jobs/{job_id}"
    }
