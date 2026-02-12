from fastapi import APIRouter, BackgroundTasks
from services import ai_service
from services.job_manager import job_manager
from schemas import AIIndexRequest, AISearchRequest, AIAnalyzeRequest

router = APIRouter()


def run_ai_index(source_dir: str, job_id: str, force_reindex: bool):
    """Background task for AI indexing."""
    try:
        ai_service.index_media_library(source_dir, job_id, force_reindex)
    except Exception as e:
        job_manager.fail_job(job_id, str(e))


@router.post("/index")
def index_media(request: AIIndexRequest, background_tasks: BackgroundTasks):
    """
    Start indexing a media directory with AI analysis.
    Each image is analyzed by Gemini Vision and stored in the local vector DB.
    Returns a job_id for real-time progress tracking.
    """
    job_id = job_manager.create_job("ai_index")

    background_tasks.add_task(
        run_ai_index,
        request.source_dir,
        job_id,
        request.force_reindex
    )

    return {
        "status": "started",
        "job_id": job_id,
        "message": f"AI indexing started. Track progress at /jobs/{job_id}"
    }


@router.post("/search")
def search_media(request: AISearchRequest):
    """
    Semantic search across indexed media.
    Uses natural language queries like 'photos of a sunset at the beach'.
    """
    results = ai_service.search_media(
        query=request.query,
        top_k=request.top_k,
        source_dir=request.source_dir
    )
    return results


@router.post("/analyze")
def analyze_file(request: AIAnalyzeRequest):
    """
    Analyze a single image file and return AI-generated tags.
    """
    return ai_service.analyze_image(request.file_path)


@router.post("/suggestions")
def get_suggestions(request: AIAnalyzeRequest):
    """
    Get AI-powered folder organization suggestions for a directory.
    Analyzes a sample of images and proposes an optimal folder structure.
    """
    return ai_service.get_smart_suggestions(request.file_path)
