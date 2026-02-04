import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DiskOrganizer")

def get_unique_path(target_dir: Path, filename: str) -> Path:
    """
    Generates a unique filename if the file already exists in the destination.
    Appends _1, _2, etc. to the filename.
    """
    target_path = target_dir / filename
    if not target_path.exists():
        return target_path
    
    stem = target_path.stem
    suffix = target_path.suffix
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = target_dir / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def safe_move_file(src: Path, dest_dir: Path, dry_run: bool = True, reason: str = "") -> dict:
    """
    Moves a file safely, creating directories if needed.
    Returns a dict with status.
    """
    if not src.exists():
        return {"status": "skipped", "reason": "Source not found", "file": src.name}
    
    try:
        if dry_run:
            logger.info(f"[DRY RUN] Move: {src.name} -> {dest_dir.name}/ ({reason})")
            return {"status": "dry_run", "src": str(src), "dest_dir": str(dest_dir), "reason": reason}
            
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = get_unique_path(dest_dir, src.name)
        shutil.move(str(src), str(dest_path))
        logger.info(f"[MOVED] {src.name} -> {dest_path} ({reason})")
        return {"status": "moved", "src": str(src), "dest": str(dest_path), "reason": reason}
        
    except Exception as e:
        logger.error(f"[ERROR] Could not move {src.name}: {e}")
        return {"status": "error", "file": src.name, "error": str(e)}
