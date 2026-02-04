from fastapi import APIRouter, BackgroundTasks
from services import file_service
from services.job_manager import job_manager
from schemas import PDFRequest, FileTypeRequest, BaseRequest

router = APIRouter()


def run_collect_pdfs(source_dir: str, dest_dir: str, dry_run: bool, job_id: str):
    """Background task for PDF collection."""
    try:
        file_service.collect_pdfs(source_dir, dest_dir, dry_run, job_id)
    except Exception as e:
        job_manager.fail_job(job_id, str(e))


def run_organize_by_type(source_dir: str, dest_dir: str, dry_run: bool, job_id: str):
    """Background task for file type organization."""
    try:
        file_service.organize_files_by_type(source_dir, dest_dir, dry_run, job_id)
    except Exception as e:
        job_manager.fail_job(job_id, str(e))


def run_analyze_extensions(source_dir: str, job_id: str):
    """Background task for extension analysis."""
    try:
        file_service.analyze_extensions(source_dir, job_id)
    except Exception as e:
        job_manager.fail_job(job_id, str(e))


@router.post("/consolidate-pdfs")
def consolidate_pdfs(request: PDFRequest, background_tasks: BackgroundTasks):
    """
    Find and move all PDFs to a single folder.
    Returns immediately with a job_id for progress tracking.
    """
    job_id = job_manager.create_job("consolidate_pdfs")
    
    background_tasks.add_task(
        run_collect_pdfs,
        request.source_dir,
        request.dest_dir,
        request.dry_run,
        job_id
    )
    
    return {
        "status": "started",
        "job_id": job_id,
        "message": f"PDF consolidation started. Track progress at /jobs/{job_id}"
    }


@router.post("/organize-types")
def organize_by_type(request: FileTypeRequest, background_tasks: BackgroundTasks):
    """
    Organize Installers and Archives into specific folders.
    Returns immediately with a job_id for progress tracking.
    """
    job_id = job_manager.create_job("organize_types")
    
    background_tasks.add_task(
        run_organize_by_type,
        request.source_dir,
        request.dest_dir,
        request.dry_run,
        job_id
    )
    
    return {
        "status": "started",
        "job_id": job_id,
        "message": f"File organization started. Track progress at /jobs/{job_id}"
    }


@router.post("/analyze")
def analyze_extensions(request: BaseRequest, background_tasks: BackgroundTasks):
    """
    Analyze file extensions in the directory.
    Returns immediately with a job_id for progress tracking.
    """
    job_id = job_manager.create_job("analyze_extensions")
    
    background_tasks.add_task(
        run_analyze_extensions,
        request.source_dir,
        job_id
    )
    
    return {
        "status": "started",
        "job_id": job_id,
        "message": f"Extension analysis started. Track progress at /jobs/{job_id}"
    }
