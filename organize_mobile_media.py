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

def organize_mobile_media(source_dir, dest_base_dir):
    """
    Moves Mobile media (iPhone, Android, OnePlus, etc.).
    - Screenshots (PNG) -> dest/Screenshots
    - Media (JPG, HEIC, MP4, DNG, GIF, WEBP) -> dest/YYYY-MM
    """
    if not os.path.isdir(source_dir):
        print(f"Error: Source '{source_dir}' is not a valid directory.")
        return
    
    # Extensions - Expanded for Android/OnePlus
    # Note: Android screenshots can sometimes be .jpg, but usually we can only distinguish by name, 
    # which is risky. We stick to extension-based 'Screenshots' folder for .png.
    MEDIA_EXTENSIONS = {
        '.heic', '.jpg', '.jpeg', '.dng', '.webp', # Photos
        '.mov', '.mp4', '.avi', '.3gp', '.mkv', '.webm', # Videos
        '.gif', # Gifs
        '.aae', # Apple sidecar files (edit information)
        '.plist' # Apple property list files (metadata)
    }
    SCREENSHOT_EXTENSIONS = {'.png'}

    # Normalize paths
    source_dir = os.path.abspath(source_dir)
    dest_base_dir = os.path.abspath(dest_base_dir)
    screenshots_dir = os.path.join(dest_base_dir, "Screenshots")

    print(f"Scanning: {source_dir}")
    print(f"MOVING to: {dest_base_dir}")
    print("Strategy: Photos/Videos -> YYYY-MM folders | PNGs -> 'Screenshots' folder")
    print("-" * 50)
    
    counters = {
        'photos_videos': 0,
        'screenshots': 0,
        'skipped': 0,
        'errors': 0
    }
    
    # Common system directories to skip
    SKIP_DIRS = {
        'windows', 'program files', 'program files (x86)', '$recycle.bin', 
        'system volume information', 'appdata', '.git', '.vs', '__pycache__',
        'auto back up', 'autobackup'
    }

    for root, dirs, files in os.walk(source_dir, topdown=True):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS and not d.startswith('.')]
        
        if os.path.commonpath([dest_base_dir, root]) == dest_base_dir:
            continue

        for file in files:
            name, ext = os.path.splitext(file)
            ext_lower = ext.lower()
            
            target_dir = None
            is_screenshot = False
            
            # Determine Category
            if 'screenshot' in name.lower() or ext_lower in SCREENSHOT_EXTENSIONS:
                target_dir = screenshots_dir
                is_screenshot = True
            elif ext_lower in MEDIA_EXTENSIONS:
                # Date based
                source_path = os.path.join(root, file)
                date_obj = get_date_taken(source_path)
                folder_name = date_obj.strftime("%Y-%m")
                target_dir = os.path.join(dest_base_dir, folder_name)
            else:
                continue # Skip other files

            # Process Move
            source_path = os.path.join(root, file)
            
            try:
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                target_filename = file
                target_path = os.path.join(target_dir, target_filename)

                # Collision check - ALWAYS RENAME if exists
                if os.path.exists(target_path):
                    target_filename = get_unique_filename(target_dir, file)
                    target_path = os.path.join(target_dir, target_filename)

                shutil.move(source_path, target_path)
                
                type_label = "Screenshot" if is_screenshot else "Media"
                dest_rel = os.path.relpath(target_path, dest_base_dir)
                print(f"Moved [{type_label}]: {file} -> {dest_rel}")
                
                if is_screenshot:
                    counters['screenshots'] += 1
                else:
                    counters['photos_videos'] += 1
                    
            except PermissionError:
                print(f"Skipped (Permission Denied): {source_path}")
                counters['errors'] += 1
            except Exception as e:
                print(f"Error moving {source_path}: {e}")
                counters['errors'] += 1

    print("-" * 50)
    print("Operation complete.")
    print(f"Photos/Videos moved: {counters['photos_videos']}")
    print(f"Screenshots moved:   {counters['screenshots']}")
    print(f"Skipped (Duplicates):{counters['skipped']}")
    
    if counters['errors'] > 0:
        print(f"Errors encountered:  {counters['errors']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move Mobile media (iOS/Android). Separates PNG screenshots.")
    parser.add_argument("source", nargs="?", help="Source directory")
    parser.add_argument("destination", nargs="?", help="Destination base directory")
    
    args = parser.parse_args()
    
    if args.source and args.destination:
        s_dir = args.source.replace('"', '')
        d_dir = args.destination.replace('"', '')
        organize_mobile_media(s_dir, d_dir)
    else:
        print("Universal Mobile Media Organizer (iOS & Android)")
        print("Actions:")
        print("  1. Moves .png files to 'Screenshots' folder")
        print("  2. Moves photos/videos (.jpg, .heic, .mp4, .dng, etc.) to 'YYYY-MM' folders")
        print("WARNING: This moves files.")
        
        s_dir = input("Enter Source Directory: ").strip().replace('"', '')
        d_dir = input("Enter Destination Directory: ").strip().replace('"', '')
        
        if not s_dir or not d_dir:
            print("Both paths required.")
            sys.exit(1)
            
        if input(f"Move mobile media from '{s_dir}' to '{d_dir}'? (yes/no): ").lower() == 'yes':
            organize_mobile_media(s_dir, d_dir)
        else:
            print("Cancelled.")
