import os
import argparse
import sys
from collections import defaultdict

def format_size(size_bytes):
    """Formats bytes into human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def analyze_extensions(source_dir):
    """
    Scans a directory and reports file counts and total size by extension.
    """
    if not os.path.isdir(source_dir):
        print(f"Error: Source '{source_dir}' is not a valid directory.")
        return
    
    source_dir = os.path.abspath(source_dir)
    print(f"Analyzing extensions in: {source_dir}")
    print("This might take a moment...")
    print("-" * 50)
    
    ext_counts = defaultdict(int)
    ext_size = defaultdict(int)
    ext_samples = {}
    total_files = 0
    total_bytes = 0
    
    # Common system directories to skip
    SKIP_DIRS = {
        'windows', 'program files', 'program files (x86)', '$recycle.bin', 
        'system volume information', 'appdata', '.git', '.vs', '__pycache__',
        'auto back up', 'autobackup'
    }

    for root, dirs, files in os.walk(source_dir):
        # Prune skip dirs
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS and not d.startswith('.')]
        
        for file in files:
            name, ext = os.path.splitext(file)
            ext_lower = ext.lower()
            if not ext_lower:
                ext_lower = "[No Extension]"
            
            try:
                size = os.path.getsize(os.path.join(root, file))
                ext_counts[ext_lower] += 1
                ext_size[ext_lower] += size
                
                # Capture sample (prefer shorter ones to fit or just first one)
                if ext_lower not in ext_samples:
                    ext_samples[ext_lower] = file
                
                total_files += 1
                total_bytes += size
            except (OSError, PermissionError):
                continue

    if total_files == 0:
        print("No files found.")
        return

    # Sort by count (descending)
    sorted_exts = sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"{'EXTENSION':<20} | {'COUNT':<10} | {'TOTAL SIZE':<15} | {'EXAMPLE FILE'}")
    print("-" * 85)
    
    for ext, count in sorted_exts:
        size_str = format_size(ext_size[ext])
        sample = ext_samples.get(ext, "")
        if len(sample) > 35:
            sample = sample[:32] + "..."
        print(f"{ext:<20} | {count:<10} | {size_str:<15} | {sample}")
        
    print("-" * 50)
    print(f"Total Files: {total_files}")
    print(f"Total Size:  {format_size(total_bytes)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze file extensions in a directory.")
    parser.add_argument("source", nargs="?", help="Source directory to scan")
    
    args = parser.parse_args()
    
    if args.source:
        s_dir = args.source.replace('"', '')
        analyze_extensions(s_dir)
    else:
        print("Extension Analyzer")
        s_dir = input("Enter Source Directory to analyze: ").strip().replace('"', '')
        
        if not s_dir:
            print("Path required.")
            sys.exit(1)
            
        analyze_extensions(s_dir)
