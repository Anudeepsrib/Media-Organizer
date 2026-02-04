import os
import shutil
import argparse
import sys
from datetime import datetime

def get_unique_filename(directory, filename):
    """
    Generates a unique filename if the file already exists in the destination.
    Appends _1, _2, etc. to the filename.
    """
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
        
    return new_filename

def get_date_taken(path):
    """
    Attempts to get the date taken from the file's modification time.
    """
    try:
        stats = os.stat(path)
        timestamp = min(stats.st_ctime, stats.st_mtime)
        return datetime.fromtimestamp(timestamp)
    except Exception:
        return datetime.now()

def move_sorted_raw_photos(source_dir, dest_base_dir):
    """
    Moves RAW photos from source_dir to dest_base_dir, organized by YYYY-MM.
    Safely handles files that might have already been copied.
    """
    if not os.path.isdir(source_dir):
        print(f"Error: Source '{source_dir}' is not a valid directory.")
        return
    
    # Common RAW formats
    RAW_EXTENSIONS = {
        '.cr2', '.cr3', '.nef', '.nrw', '.arw', '.srf', '.sr2', 
        '.dng', '.orf', '.rw2', '.raf', '.pef', '.srw', '.x3f', '.raw'
    }

    # Normalize paths
    source_dir = os.path.abspath(source_dir)
    dest_base_dir = os.path.abspath(dest_base_dir)

    print(f"Scanning: {source_dir}")
    print(f"MOVING to: {dest_base_dir}")
    print("Sorting criteria: Month-wise (based on file date)")
    print("-" * 50)
    
    files_moved = 0
    files_skipped = 0
    errors = 0
    
    RAW_EXTENSIONS_LOWER = {ext.lower() for ext in RAW_EXTENSIONS}
    
    # Common system directories to skip
    SKIP_DIRS = {
        'windows', 'program files', 'program files (x86)', '$recycle.bin', 
        'system volume information', 'appdata', '.git', '.vs', '__pycache__',
        'auto back up', 'autobackup'
    }

    # Walk topdown=True to skip dirs easily
    for root, dirs, files in os.walk(source_dir, topdown=True):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS and not d.startswith('.')]
        
        if os.path.commonpath([dest_base_dir, root]) == dest_base_dir:
            continue

        for file in files:
            name, ext = os.path.splitext(file)
            if ext.lower() in RAW_EXTENSIONS_LOWER:
                source_path = os.path.join(root, file)
                
                try:
                    date_obj = get_date_taken(source_path)
                    folder_name = date_obj.strftime("%Y-%m")
                    target_dir = os.path.join(dest_base_dir, folder_name)
                    
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)

                    target_filename = file 
                    target_path = os.path.join(target_dir, target_filename)

                    # Check for existence (Collision handling)
                    if os.path.exists(target_path):
                        # File with same name exists in correct month folder.
                        # Check if it's likely the same file (size check)
                        src_size = os.path.getsize(source_path)
                        dest_size = os.path.getsize(target_path)
                        
                        if src_size == dest_size:
                            # Likely already copied. Skip move.
                            print(f"Skipped (Already exists): {file} -> {target_path}")
                            files_skipped += 1
                            continue
                        else:
                            # Name collision but different file size -> Rename and Move
                            target_filename = get_unique_filename(target_dir, file)
                            target_path = os.path.join(target_dir, target_filename)

                    # MOVE
                    shutil.move(source_path, target_path)
                    print(f"Moved: {file} -> {folder_name}\\{target_filename}")
                    files_moved += 1
                    
                except PermissionError:
                    print(f"Skipped (Permission Denied): {source_path}")
                    errors += 1
                except Exception as e:
                    print(f"Error moving {source_path}: {e}")
                    errors += 1

    print("-" * 50)
    print("Operation complete.")
    print(f"Total RAW photos moved: {files_moved}")
    print(f"Total skipped (already in dest): {files_skipped}")
    
    if errors > 0:
        print(f"Errors encountered: {errors}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move and sort RAW photos into month-wise folders.")
    parser.add_argument("source", nargs="?", help="Source directory")
    parser.add_argument("destination", nargs="?", help="Destination base directory")
    
    args = parser.parse_args()
    
    default_source = r"D:\Camera RAW files"
    default_dest = r"D:\RAW_Pics"

    if args.source and args.destination:
        s_dir = args.source.replace('"', '')
        d_dir = args.destination.replace('"', '')
        move_sorted_raw_photos(s_dir, d_dir)
    else:
        print("RAW Photo Organizer (MOVE & Sort by Date)")
        print("NOTE: Any files already present in the destination (same name & size) will be skipped (left in source).")
        
        s_input = input(f"Enter Source Directory [Default: {default_source}]: ").strip().replace('"', '')
        s_dir = s_input if s_input else default_source
        
        d_input = input(f"Enter Destination Directory [Default: {default_dest}]: ").strip().replace('"', '')
        d_dir = d_input if d_input else default_dest
        
        print(f"\nConfiguration:")
        print(f"  Source:      {s_dir}")
        print(f"  Destination: {d_dir}")
        print("  Action:      MOVE files (Clean up source)")
        
        if input("\nProceed with MOVE operation? (yes/no): ").lower() == 'yes':
            move_sorted_raw_photos(s_dir, d_dir)
        else:
            print("Cancelled.")
