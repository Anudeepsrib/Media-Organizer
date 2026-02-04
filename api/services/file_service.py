from pathlib import Path
import shutil
from collections import defaultdict
from services.core_logic import safe_move_file, logger

def collect_pdfs(source_dir: str, dest_dir: str, dry_run: bool = True):
    """
    Finds all PDFs in source_dir recursively and moves them to dest_dir.
    """
    source = Path(source_dir)
    dest = Path(dest_dir)
    results = {"moved": 0, "errors": 0, "details": []}

    SKIP_DIRS = {'Windows', 'Program Files', 'Program Files (x86)', '$Recycle.Bin', 'System Volume Information', 'AppData'}
    
    # Using os.walk equivalent logic with rglob but filtering directories manually to respect skip list would be complex with pathlib only.
    # Let's stick to rglob for simplicity, or re-implement walk? 
    # Actually, rglob('*') finds everything. We can filter parents.
    
    for path in source.rglob('*.pdf'):
        if not path.is_file(): continue
        
        # Skip system dirs
        if any(part in SKIP_DIRS for part in path.parts):
            continue
            
        # Avoid moving if already in dest
        if path.parent.resolve() == dest.resolve():
            continue
            
        res = safe_move_file(path, dest, dry_run, "Consolidate PDF")
        results["details"].append(res)
        if res.get("status") in ["moved", "dry_run"]:
            results["moved"] += 1
            
    return results

def organize_files_by_type(source_dir: str, dest_dir: str, dry_run: bool = True):
    """
    Organizes Installers and Archives into categorized folders.
    """
    source = Path(source_dir)
    dest = Path(dest_dir)
    
    FILE_CATEGORIES = {
        'Software Installers': {'.exe', '.msi', '.iso'},
        'Archives': {'.zip', '.rar', '.7z', '.tar.gz', '.tgz', '.gz'}
    }
    
    results = {"moved": 0, "errors": 0, "details": []}
    
    for path in source.rglob('*'):
        if not path.is_file(): continue
        
        ext = path.suffix.lower()
        category = None
        for cat, exts in FILE_CATEGORIES.items():
            if ext in exts:
                category = cat
                break
        
        if category:
            target_subfolder = dest / category
            res = safe_move_file(path, target_subfolder, dry_run, category)
            results["details"].append(res)
            if res.get("status") in ["moved", "dry_run"]:
                results["moved"] += 1
                
    return results

def analyze_extensions(source_dir: str):
    """
    Returns statistics of file extensions in the directory.
    """
    source = Path(source_dir)
    counts = defaultdict(int)
    sizes = defaultdict(int)
    
    for path in source.rglob('*'):
        if not path.is_file(): continue
        ext = path.suffix.lower() or "No Extension"
        counts[ext] += 1
        sizes[ext] += path.stat().st_size
        
    return {
        "counts": counts,
        "sizes": sizes
    }
