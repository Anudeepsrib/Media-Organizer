"""
Job Manager - Thread-safe job tracking for async operations.
Enables progress tracking, abort functionality, and SSE streaming.
"""
import threading
import uuid
from datetime import datetime
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


@dataclass
class JobState:
    id: str
    job_type: str
    status: JobStatus = JobStatus.PENDING
    progress: int = 0  # 0-100
    current: int = 0   # files processed
    total: int = 0     # total files
    current_file: str = ""
    message: str = "Initializing..."
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status.value,
            "progress": self.progress,
            "current": self.current,
            "total": self.total,
            "current_file": self.current_file,
            "message": self.message,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result
        }


class JobManager:
    """Thread-safe singleton for managing job state across the application."""
    
    _instance: Optional['JobManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._jobs: Dict[str, JobState] = {}
                    cls._instance._abort_flags: Dict[str, bool] = {}
                    cls._instance._job_lock = threading.Lock()
        return cls._instance
    
    def create_job(self, job_type: str) -> str:
        """Create a new job and return its ID."""
        job_id = str(uuid.uuid4())[:8]
        with self._job_lock:
            self._jobs[job_id] = JobState(id=job_id, job_type=job_type)
            self._abort_flags[job_id] = False
        return job_id
    
    def get_job(self, job_id: str) -> Optional[JobState]:
        """Get job state by ID."""
        with self._job_lock:
            return self._jobs.get(job_id)
    
    def get_all_jobs(self) -> list:
        """Get all jobs as dicts."""
        with self._job_lock:
            return [job.to_dict() for job in self._jobs.values()]
    
    def update_progress(
        self, 
        job_id: str, 
        current: int, 
        total: int, 
        message: str = "",
        current_file: str = ""
    ):
        """Update job progress. Called from within service loops."""
        with self._job_lock:
            job = self._jobs.get(job_id)
            if job and job.status == JobStatus.RUNNING:
                job.current = current
                job.total = total
                job.progress = int((current / total) * 100) if total > 0 else 0
                job.message = message
                job.current_file = current_file
    
    def start_job(self, job_id: str, total: int = 0):
        """Mark job as running."""
        with self._job_lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.RUNNING
                job.total = total
                job.message = "Processing..."
    
    def complete_job(self, job_id: str, result: dict):
        """Mark job as completed with results."""
        with self._job_lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.completed_at = datetime.now()
                job.result = result
                job.message = "Completed successfully"
    
    def fail_job(self, job_id: str, error: str):
        """Mark job as failed."""
        with self._job_lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now()
                job.message = f"Failed: {error}"
                job.result = {"error": error}
    
    def abort_job(self, job_id: str) -> bool:
        """Request job abortion. Returns True if job exists."""
        with self._job_lock:
            if job_id in self._abort_flags:
                self._abort_flags[job_id] = True
                job = self._jobs.get(job_id)
                if job:
                    job.message = "Abort requested..."
                return True
            return False
    
    def is_aborted(self, job_id: str) -> bool:
        """Check if abort was requested for this job."""
        with self._job_lock:
            return self._abort_flags.get(job_id, False)
    
    def mark_aborted(self, job_id: str, result: dict):
        """Mark job as aborted with partial results."""
        with self._job_lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.ABORTED
                job.completed_at = datetime.now()
                job.message = "Operation aborted by user"
                job.result = result


# Global instance
job_manager = JobManager()
