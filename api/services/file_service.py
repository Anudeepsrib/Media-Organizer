from pathlib import Path
from collections import defaultdict
from services.core_logic import safe_move_file, logger
from services.job_manager import job_manager


def collect_pdfs(source_dir: str, dest_dir: str, dry_run: bool = True, job_id: str = None):
    """
    Finds all PDFs in source_dir recursively and moves them to dest_dir.
    Supports job tracking and abort functionality.
    """
    source = Path(source_dir)
    dest = Path(dest_dir)
    results = {"moved": 0, "errors": 0, "details": []}

    SKIP_DIRS = {'Windows', 'Program Files', 'Program Files (x86)', '$Recycle.Bin', 'System Volume Information', 'AppData'}
    
    # First pass: collect all PDFs
    all_files = []
    for path in source.rglob('*.pdf'):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.parent.resolve() == dest.resolve():
            continue
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
            
        res = safe_move_file(path, dest, dry_run, "Consolidate PDF")
        results["details"].append(res)
        
        if res.get("status") in ["moved", "dry_run"]:
            results["moved"] += 1
        
        # Update progress
        if job_id:
            job_manager.update_progress(
                job_id,
                current=i + 1,
                total=total,
                message=f"{'[DRY RUN] ' if dry_run else ''}Collecting PDFs...",
                current_file=path.name
            )
    
    if job_id:
        job_manager.complete_job(job_id, results)
            
    return results


def organize_files_by_type(source_dir: str, dest_dir: str, dry_run: bool = True, job_id: str = None):
    """
    Organizes Installers and Archives into categorized folders.
    Supports job tracking and abort functionality.
    """
    source = Path(source_dir)
    dest = Path(dest_dir)
    
    FILE_CATEGORIES = {
        'Software Installers': {'.exe', '.msi', '.iso'},
        'Archives': {'.zip', '.rar', '.7z', '.tar.gz', '.tgz', '.gz'}
    }
    
    results = {"moved": 0, "errors": 0, "details": []}
    
    # First pass: collect files
    all_files = []
    for path in source.rglob('*'):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        for cat, exts in FILE_CATEGORIES.items():
            if ext in exts:
                all_files.append((path, cat))
                break
    
    total = len(all_files)
    
    if job_id:
        job_manager.start_job(job_id, total)
    
    for i, (path, category) in enumerate(all_files):
        # Check for abort
        if job_id and job_manager.is_aborted(job_id):
            results["aborted"] = True
            results["message"] = f"Aborted after processing {i} of {total} files"
            job_manager.mark_aborted(job_id, results)
            return results
        
        target_subfolder = dest / category
        res = safe_move_file(path, target_subfolder, dry_run, category)
        results["details"].append(res)
        
        if res.get("status") in ["moved", "dry_run"]:
            results["moved"] += 1
        
        # Update progress
        if job_id:
            job_manager.update_progress(
                job_id,
                current=i + 1,
                total=total,
                message=f"{'[DRY RUN] ' if dry_run else ''}Organizing files by type...",
                current_file=path.name
            )
    
    if job_id:
        job_manager.complete_job(job_id, results)
                
    return results


def analyze_extensions(source_dir: str, job_id: str = None):
    """
    Returns statistics of file extensions in the directory.
    """
    source = Path(source_dir)
    counts = defaultdict(int)
    sizes = defaultdict(int)
    
    if job_id:
        job_manager.start_job(job_id, 0)
        job_manager.update_progress(job_id, 0, 0, "Analyzing extensions...", "")
    
    file_count = 0
    for path in source.rglob('*'):
        if not path.is_file():
            continue
        
        # Check for abort
        if job_id and job_manager.is_aborted(job_id):
            result = {"counts": dict(counts), "sizes": dict(sizes), "aborted": True}
            job_manager.mark_aborted(job_id, result)
            return result
        
        ext = path.suffix.lower() or "No Extension"
        counts[ext] += 1
        sizes[ext] += path.stat().st_size
        file_count += 1
        
        if job_id and file_count % 100 == 0:
            job_manager.update_progress(
                job_id,
                current=file_count,
                total=file_count,
                message="Scanning files...",
                current_file=path.name
            )
    
    result = {"counts": dict(counts), "sizes": dict(sizes)}
    
    if job_id:
        job_manager.complete_job(job_id, result)
        
    return result
