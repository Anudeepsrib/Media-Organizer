import os
import shutil
import argparse
import sys

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

def organize_files(source_dir, dest_base_dir):
    """
    Traverses source_dir, finds specific file types, and moves them to categorized folders in dest_base_dir.
    """
    if not os.path.isdir(source_dir):
        print(f"Error: Source '{source_dir}' is not a valid directory.")
        return
    
    # Define categories and their extensions
    FILE_CATEGORIES = {
        'Software Installers': {'.exe', '.msi', '.iso'},
        'Archives': {'.zip', '.rar', '.7z', '.tar.gz', '.tgz', '.gz'}
    }

    # Normalize paths
    source_dir = os.path.abspath(source_dir)
    dest_base_dir = os.path.abspath(dest_base_dir)

    print(f"Scanning: {source_dir}")
    print(f"Organizing into: {dest_base_dir}")
    print("-" * 50)
    
    metrics = {cat: 0 for cat in FILE_CATEGORIES}
    errors = 0
    
    # Common system directories to skip
    SKIP_DIRS = {
        'windows', 'program files', 'program files (x86)', '$recycle.bin', 
        'system volume information', 'appdata', '.git', '.vs', '__pycache__',
        'auto back up', 'autobackup'
    }

    for root, dirs, files in os.walk(source_dir, topdown=True):
        # Modify dirs in-place to skip system directories
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS and not d.startswith('.')]
        
        # Skip if we are inside the destination folder to avoid loops
        if os.path.commonpath([dest_base_dir, root]) == dest_base_dir:
            continue

        for file in files:
            name, ext = os.path.splitext(file)
            ext_lower = ext.lower()
            
            target_category_folder = None
            
            # Determine category
            for category, extensions in FILE_CATEGORIES.items():
                if ext_lower in extensions:
                    target_category_folder = category
                    break
            
            if target_category_folder:
                source_path = os.path.join(root, file)
                dest_dir = os.path.join(dest_base_dir, target_category_folder)
                
                if not os.path.exists(dest_dir):
                    try:
                        os.makedirs(dest_dir)
                    except OSError as e:
                        print(f"Error creating directory {dest_dir}: {e}")
                        continue

                # Check if same file (can happen if source is same as dest)
                if os.path.dirname(source_path) == dest_dir:
                    continue

                try:
                    destination_filename = get_unique_filename(dest_dir, file)
                    destination_path = os.path.join(dest_dir, destination_filename)
                    
                    shutil.move(source_path, destination_path)
                    print(f"Moved [{target_category_folder}]: {file} -> {destination_filename}")
                    metrics[target_category_folder] += 1
                except PermissionError:
                    print(f"Skipped (Permission Denied): {source_path}")
                    errors += 1
                except Exception as e:
                    print(f"Error moving {source_path}: {e}")
                    errors += 1

    print("-" * 50)
    print("Operation complete.")
    for category, count in metrics.items():
        print(f"  {category}: {count} files")
    
    if errors > 0:
        print(f"Errors encountered: {errors}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize Installers and Archives into specific folders.")
    parser.add_argument("source", nargs="?", help="Source directory to search")
    parser.add_argument("destination", nargs="?", help="Destination base directory")
    
    args = parser.parse_args()
    
    if args.source and args.destination:
        s_dir = args.source.replace('"', '')
        d_dir = args.destination.replace('"', '')
        organize_files(s_dir, d_dir)
    else:
        print("File Type Organizer (Installers & Archives)")
        print("WARNING: This will MOVE files.")
        
        s_dir = input("Enter Source Directory: ").strip().replace('"', '')
        d_dir = input("Enter Destination Directory (Folders will be created inside): ").strip().replace('"', '')
        
        if not s_dir or not d_dir:
            print("Both paths are required.")
            sys.exit(1)
            
        if input(f"Move Installers & Archives from '{s_dir}' to '{d_dir}'? (yes/no): ").lower() == 'yes':
            organize_files(s_dir, d_dir)
        else:
            print("Cancelled.")
