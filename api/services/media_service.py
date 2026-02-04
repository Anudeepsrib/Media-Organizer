from pathlib import Path
from datetime import datetime
from services.core_logic import safe_move_file, logger
from services.job_manager import job_manager

MEDIA_EXTENSIONS = {
    '.heic', '.jpg', '.jpeg', '.dng', '.webp', # Photos
    '.mov', '.mp4', '.avi', '.3gp', '.mkv', '.webm', # Videos
    '.gif', '.png', '.arw', '.cr2', '.nef' # Misc/Raw
}


def organize_media_by_date(source_dir: str, dest_dir: str, dry_run: bool = True, job_id: str = None):
    """
    Moves media files into YYYY-MM folders and Screenshots folder.
    Supports job tracking and abort functionality.
    """
    source = Path(source_dir)
    dest = Path(dest_dir)
    
    if not source.exists():
        if job_id:
            job_manager.fail_job(job_id, "Source directory not found")
        return {"error": "Source directory not found"}

    results = {"moved": 0, "errors": 0, "skipped": 0, "details": []}
    
    # First pass: count total files
    all_files = []
    for path in source.rglob('*'):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext in MEDIA_EXTENSIONS:
            all_files.append(path)
    
    total = len(all_files)
    
    if job_id:
        job_manager.start_job(job_id, total)
    
    for i, path in enumerate(all_files):
        # Check for abort
        if job_id and job_manager.is_aborted(job_id):
            results["aborted"] = True
            results["message"] = f"Aborted after processing {i} of {total} files"
            job_manager.mark_aborted(job_id, results)
            return results
        
        ext = path.suffix.lower()
        name = path.name.lower()
        
        # Determine Target
        target_subfolder = None
        reason = ""
        
        if 'screenshot' in name or ext == '.png':
            target_subfolder = dest / "Screenshots"
            reason = "Screenshot detected"
        else:
            # Date based
            try:
                mtime = path.stat().st_mtime
                date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m')
                target_subfolder = dest / date_str
                reason = f"Media File ({date_str})"
            except Exception:
                target_subfolder = dest / "Unknown_Date"
                reason = "Date extraction failed"
        
        # Execute
        res = safe_move_file(path, target_subfolder, dry_run, reason)
        results["details"].append(res)
        
        if res.get("status") in ["moved", "dry_run"]:
            results["moved"] += 1
        elif res.get("status") == "error":
            results["errors"] += 1
        else:
            results["skipped"] += 1
        
        # Update progress
        if job_id:
            job_manager.update_progress(
                job_id,
                current=i + 1,
                total=total,
                message=f"{'[DRY RUN] ' if dry_run else ''}Processing media files...",
                current_file=path.name
            )
    
    # Complete job
    if job_id:
        job_manager.complete_job(job_id, results)
            
    return results


def organize_expanded_dates(root_dir: str, dry_run: bool = True, job_id: str = None):
    """
    Scans YYYY-MM folders and moves files into DD subfolders.
    Supports job tracking and abort functionality.
    """
    import re
    
    root = Path(root_dir)
    if not root.exists():
        if job_id:
            job_manager.fail_job(job_id, "Root directory not found")
        return {"error": "Root directory not found"}
        
    date_folder_pattern = re.compile(r'^(19|20)\d{2}-?(0[1-9]|1[0-2])$')
    
    results = {"moved": 0, "errors": 0, "details": []}
    
    # Identify date folders and collect files
    all_files = []
    for item in root.iterdir():
        if item.is_dir() and date_folder_pattern.match(item.name):
            for file_path in item.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    all_files.append((item, file_path))
    
    total = len(all_files)
    
    if job_id:
        job_manager.start_job(job_id, total)
    
    for i, (folder, file_path) in enumerate(all_files):
        # Check for abort
        if job_id and job_manager.is_aborted(job_id):
            results["aborted"] = True
            results["message"] = f"Aborted after processing {i} of {total} files"
            job_manager.mark_aborted(job_id, results)
            return results
            
        try:
            mtime = file_path.stat().st_mtime
            day_str = datetime.fromtimestamp(mtime).strftime("%d")
            
            day_folder = folder / day_str
            res = safe_move_file(file_path, day_folder, dry_run, f"Day {day_str}")
            results["details"].append(res)
            
            if res.get("status") in ["moved", "dry_run"]:
                results["moved"] += 1
            
            # Update progress
            if job_id:
                job_manager.update_progress(
                    job_id,
                    current=i + 1,
                    total=total,
                    message=f"{'[DRY RUN] ' if dry_run else ''}Expanding to daily folders...",
                    current_file=file_path.name
                )
                
        except Exception as e:
            results["errors"] += 1
    
    # Complete job
    if job_id:
        job_manager.complete_job(job_id, results)
                
    return results
