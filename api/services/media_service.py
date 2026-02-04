from pathlib import Path
from datetime import datetime
from services.core_logic import safe_move_file, logger

MEDIA_EXTENSIONS = {
    '.heic', '.jpg', '.jpeg', '.dng', '.webp', # Photos
    '.mov', '.mp4', '.avi', '.3gp', '.mkv', '.webm', # Videos
    '.gif', '.png', '.arw', '.cr2', '.nef' # Misc/Raw
}

def organize_media_by_date(source_dir: str, dest_dir: str, dry_run: bool = True):
    """
    Moves media files into YYYY-MM folders and Screenshots folder.
    """
    source = Path(source_dir)
    dest = Path(dest_dir)
    
    if not source.exists():
        return {"error": "Source directory not found"}

    results = {"moved": 0, "errors": 0, "details": []}
    
    for path in source.rglob('*'):
        if not path.is_file(): continue
        
        ext = path.suffix.lower()
        name = path.name.lower()
        
        if ext not in MEDIA_EXTENSIONS:
            continue

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
            
    return results

def organize_expanded_dates(root_dir: str, dry_run: bool = True):
    """
    Scans YYYY-MM folders and moves files into DD subfolders.
    """
    import re
    
    root = Path(root_dir)
    if not root.exists():
        return {"error": "Root directory not found"}
        
    date_folder_pattern = re.compile(r'^(19|20)\d{2}-?(0[1-9]|1[0-2])$')
    
    results = {"moved": 0, "errors": 0, "details": []}
    
    # Identify date folders
    target_folders = []
    for item in root.iterdir():
        if item.is_dir() and date_folder_pattern.match(item.name):
            target_folders.append(item)
            
    for folder in target_folders:
        for file_path in folder.iterdir():
            if not file_path.is_file() or file_path.name.startswith('.'):
                continue
                
            try:
                mtime = file_path.stat().st_mtime
                day_str = datetime.fromtimestamp(mtime).strftime("%d")
                
                day_folder = folder / day_str
                res = safe_move_file(file_path, day_folder, dry_run, f"Day {day_str}")
                results["details"].append(res)
                if res.get("status") in ["moved", "dry_run"]:
                    results["moved"] += 1
            except Exception as e:
                results["errors"] += 1
                
    return results
