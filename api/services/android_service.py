from pathlib import Path
import re
from services.core_logic import safe_move_file, logger
from services.job_manager import job_manager


def clean_android_backup(source_dir: str, threshold_mb: int = 50, dry_run: bool = True, job_id: str = None):
    """
    Organizes Android backup folder: moves WhatsApp backups, Junk, and Large Cache files.
    Supports job tracking and abort functionality.
    """
    source = Path(source_dir)
    if not source.exists():
        if job_id:
            job_manager.fail_job(job_id, "Source directory not found")
        return {"error": "Source directory not found"}

    DIR_WHATSAPP = source / "_whatsapp_backup"
    DIR_LARGE_CACHE = source / "_suspected_cache"
    DIR_JUNK_CACHE = source / "_junk_cache"
    
    RE_WHATSAPP = [re.compile(r'.*\.crypt\d+$', re.I), re.compile(r'^msgstore.*\.db.*$', re.I)]
    RE_JUNK_NAME = [re.compile(r'^\d+$'), re.compile(r'^[a-fA-F0-9]+$'), re.compile(r'^\.+')]
    JUNK_EXTS = {'.tmp', '.log', '.chck', '.pcm', '.clean', '.exo', '.bkup', '.swatch'}
    PROTECTED_EXTS = {'.doc', '.docx', '.pdf', '.jpg', '.png', '.mp4', '.apk', '.xlsx', '.pptx'}
    
    threshold_bytes = threshold_mb * 1024 * 1024
    results = {"moved": 0, "errors": 0, "details": []}
    
    # First pass: collect files to process
    all_files = []
    for path in source.rglob('*'):
        if not path.is_file():
            continue
        # Avoid self-processing
        if any(p.name in ["_whatsapp_backup", "_suspected_cache", "_junk_cache"] for p in path.parents):
            continue
        
        ext = path.suffix.lower()
        if ext in PROTECTED_EXTS:
            continue
            
        name = path.name
        size = path.stat().st_size
        
        target_dir = None
        reason = None
        
        if any(p.match(name) for p in RE_WHATSAPP):
            target_dir = DIR_WHATSAPP
            reason = "WhatsApp Backup"
        elif ext in JUNK_EXTS:
            target_dir = DIR_JUNK_CACHE
            reason = f"Junk Extension {ext}"
        elif not ext:
            if size >= threshold_bytes:
                target_dir = DIR_LARGE_CACHE
                reason = f"Large No-Ext File (> {threshold_mb}MB)"
            elif any(p.match(name) for p in RE_JUNK_NAME) or 'thumbdata' in name.lower():
                target_dir = DIR_JUNK_CACHE
                reason = "Junk Name Pattern"
        
        if target_dir:
            all_files.append((path, target_dir, reason))
    
    total = len(all_files)
    
    if job_id:
        job_manager.start_job(job_id, total)
    
    for i, (path, target_dir, reason) in enumerate(all_files):
        # Check for abort
        if job_id and job_manager.is_aborted(job_id):
            results["aborted"] = True
            results["message"] = f"Aborted after processing {i} of {total} files"
            job_manager.mark_aborted(job_id, results)
            return results
        
        res = safe_move_file(path, target_dir, dry_run, reason)
        results["details"].append(res)
        
        if res.get("status") in ["moved", "dry_run"]:
            results["moved"] += 1
        
        # Update progress
        if job_id:
            job_manager.update_progress(
                job_id,
                current=i + 1,
                total=total,
                message=f"{'[DRY RUN] ' if dry_run else ''}Cleaning Android backup...",
                current_file=path.name
            )
    
    if job_id:
        job_manager.complete_job(job_id, results)
                
    return results
