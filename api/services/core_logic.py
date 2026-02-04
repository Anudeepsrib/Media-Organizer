import os
import shutil
import logging
import hashlib
from pathlib import Path
from typing import Optional, Callable

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

def calculate_checksum(file_path: Path, algorithm: str = 'sha256', chunk_size: int = 8192) -> str:
    """Calculates the checksum of a file."""
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def check_disk_space(dest_dir: Path, required_bytes: int) -> bool:
    """Checks if destination has enough free space."""
    try:
        total, used, free = shutil.disk_usage(dest_dir.anchor)
        return free >= required_bytes
    except Exception as e:
        logger.warning(f"Could not check disk space: {e}")
        return True # Assume space exists if check fails (network drives etc)

def safe_move_file(
    src: Path, 
    dest_dir: Path, 
    dry_run: bool = True, 
    reason: str = "", 
    safe_mode: bool = True,
    progress_callback: Optional[Callable[[str], None]] = None
) -> dict:
    """
    Moves a file safely.
    If safe_mode is True: Copy -> Verify -> Delete.
    """
    if not src.exists():
        return {"status": "skipped", "reason": "Source not found", "file": src.name}
    
    try:
        # Determine destination path
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = get_unique_path(dest_dir, src.name)
        
        if dry_run:
            logger.info(f"[DRY RUN] Move: {src.name} -> {dest_path.name} ({reason})")
            return {
                "status": "dry_run", 
                "src": str(src), 
                "dest": str(dest_path), 
                "reason": reason,
                "mode": "safe" if safe_mode else "standard"
            }
            
        # Disk Check
        file_size = src.stat().st_size
        if not check_disk_space(dest_dir, file_size):
            raise OSError("Insufficient disk space")

        if safe_mode:
            # COPY
            if progress_callback: progress_callback("Copying...")
            shutil.copy2(src, dest_path)
            
            # VERIFY
            if progress_callback: progress_callback("Verifying checksum...")
            src_hash = calculate_checksum(src)
            dest_hash = calculate_checksum(dest_path)
            
            if src_hash != dest_hash:
                # INTEGRITY ERROR - CLEANUP DEST
                os.remove(dest_path)
                raise ValueError(f"Checksum mismatch! Source: {src_hash}, Dest: {dest_hash}")
                
            # DELETE SOURCE
            if progress_callback: progress_callback("Cleaning source...")
            os.remove(src)
            
            logger.info(f"[SAFE MOVED] {src.name} -> {dest_path} ({reason})")
            return {
                "status": "moved", 
                "src": str(src), 
                "dest": str(dest_path), 
                "reason": reason,
                "mode": "safe_verify"
            }
            
        else:
            # STANDARD MOVE
            if progress_callback: progress_callback("Moving...")
            shutil.move(str(src), str(dest_path))
            logger.info(f"[MOVED] {src.name} -> {dest_path} ({reason})")
            return {
                "status": "moved", 
                "src": str(src), 
                "dest": str(dest_path), 
                "reason": reason, 
                "mode": "standard"
            }
            
    except Exception as e:
        logger.error(f"[ERROR] Could not move {src.name}: {e}")
        return {"status": "error", "file": src.name, "error": str(e)}
