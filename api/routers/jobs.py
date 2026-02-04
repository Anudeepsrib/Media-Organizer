"""
Jobs Router - Endpoints for job management, status, and SSE streaming.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.job_manager import job_manager
import asyncio
import json

router = APIRouter()


@router.get("")
def list_jobs():
    """List all jobs (active and recent)."""
    return {"jobs": job_manager.get_all_jobs()}


@router.get("/{job_id}")
def get_job(job_id: str):
    """Get status of a specific job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()


@router.post("/{job_id}/abort")
def abort_job(job_id: str):
    """Request abortion of a running job."""
    success = job_manager.abort_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "abort_requested", "job_id": job_id}


@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str):
    """
    Server-Sent Events stream for real-time job progress.
    Clients connect and receive updates until job completes.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    async def event_generator():
        last_state = None
        while True:
            job = job_manager.get_job(job_id)
            if not job:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break
            
            current_state = job.to_dict()
            
            # Only send if state changed
            if current_state != last_state:
                yield f"data: {json.dumps(current_state)}\n\n"
                last_state = current_state.copy()
            
            # Stop streaming if job is complete
            if job.status.value in ["completed", "aborted", "failed"]:
                break
            
            await asyncio.sleep(0.2)  # 200ms polling interval
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
