import os
import shutil

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

def flatten_directory(parent_folder):
    """
    Moves all files from subdirectories of parent_folder into parent_folder.
    Removes empty subdirectories.
    """
    if not os.path.isdir(parent_folder):
        print(f"Error: '{parent_folder}' is not a valid directory.")
        return

    print(f"Flattening directory: {parent_folder}")
    files_moved = 0
    
    # Walk top-down so we see files before folders
    # We will encounter subdirs. We want to move files from them.
    # We can't use os.walk strictly top-down for deletion, but for moving it's fine.
    # Actually, os.walk is convenient.
    
    for root, dirs, files in os.walk(parent_folder, topdown=False):
        # topdown=False is better for removing directories later if we wanted, 
        # but here we iterate. 
        # Actually, if we move files, we just need to visit every file.
        
        if root == parent_folder:
            continue
            
        for file in files:
            source_path = os.path.join(root, file)
            
            # Determine destination
            destination_filename = get_unique_filename(parent_folder, file)
            destination_path = os.path.join(parent_folder, destination_filename)
            
            try:
                shutil.move(source_path, destination_path)
                print(f"Moved: {os.path.relpath(source_path, parent_folder)} -> {destination_filename}")
                files_moved += 1
            except Exception as e:
                print(f"Error moving {source_path}: {e}")

        # Try to remove the directory if it's empty now
        try:
            os.rmdir(root)
            print(f"Removed empty dir: {os.path.relpath(root, parent_folder)}")
        except OSError:
            # Directory might not be empty if there were hidden files or errors moving
            pass

    print(f"\nOperation complete. {files_moved} files moved.")

if __name__ == "__main__":
    target_dir = input("Enter the path of the parent folder to flatten: ").strip()
    # Handle quotes if user copies as path
    target_dir = target_dir.replace('"', '')
    
    flatten_directory(target_dir)
