from pathlib import Path
import re
from services.core_logic import safe_move_file, logger

def clean_android_backup(source_dir: str, threshold_mb: int = 50, dry_run: bool = True):
    """
    Organizes Android backup folder: moves WhatsApp backups, Junk, and Large Cache files.
    """
    source = Path(source_dir)
    if not source.exists():
         return {"error": "Source directory not found"}

    DIR_WHATSAPP = source / "_whatsapp_backup"
    DIR_LARGE_CACHE = source / "_suspected_cache"
    DIR_JUNK_CACHE = source / "_junk_cache"
    
    RE_WHATSAPP = [re.compile(r'.*\.crypt\d+$', re.I), re.compile(r'^msgstore.*\.db.*$', re.I)]
    RE_JUNK_NAME = [re.compile(r'^\d+$'), re.compile(r'^[a-fA-F0-9]+$'), re.compile(r'^\..+')]
    JUNK_EXTS = {'.tmp', '.log', '.chck', '.pcm', '.clean', '.exo', '.bkup', '.swatch'}
    PROTECTED_EXTS = {'.doc', '.docx', '.pdf', '.jpg', '.png', '.mp4', '.apk', '.xlsx', '.pptx'}
    
    threshold_bytes = threshold_mb * 1024 * 1024
    results = {"moved": 0, "errors": 0, "details": []}

    for path in source.rglob('*'):
        if not path.is_file(): continue
        
        # Avoid self-processing
        if any(p.name in ["_whatsapp_backup", "_suspected_cache", "_junk_cache"] for p in path.parents):
            continue
        
        ext = path.suffix.lower()
        name = path.name
        size = path.stat().st_size
        
        target_dir = None
        reason = None
        
        # Logic
        if ext in PROTECTED_EXTS: continue
        
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
            res = safe_move_file(path, target_dir, dry_run, reason)
            results["details"].append(res)
            if res.get("status") in ["moved", "dry_run"]:
                results["moved"] += 1
                
    return results
