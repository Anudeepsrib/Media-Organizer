import argparse
import logging
import re
from pathlib import Path
from datetime import datetime

# ================= CONFIGURATION =================

# Explicit cache / junk extensions (safe to delete)
TARGET_EXTENSIONS = {
    '.chck', '.checked', '.irszz9', '.pcm', '.exo',
    '.tmp', '.log', '.cfg', '.ini', '.dat', '.m',
    '.swatch', '.pba', '.cxf', '.bf2', '.fsh', '.exi'
}

# Extensions that must NEVER be deleted (real user data)
SAFE_EXTENSIONS = {
    '.doc', '.docx', '.pptx', '.xlsx', '.rtf', '.txt', '.epub',
    '.jpg', '.jpeg', '.png', '.bmp', '.tif',
    '.mp4', '.mkv', '.avi', '.flv',
    '.opus', '.amr', '.3ga', '.raw',
    '.apk', '.json', '.html', '.htm', '.js', '.css', '.pb'
}

# WhatsApp encrypted backups (NOW SAFE TO DELETE)
WHATSAPP_DELETE_PATTERNS = [
    re.compile(r'msgstore.*\.db.*', re.IGNORECASE),
    re.compile(r'.*\.crypt12$', re.IGNORECASE),
    re.compile(r'.*\.crypt1$', re.IGNORECASE),
]

# No-extension cache name patterns (OnePlus / Android)
NO_EXT_CACHE_PATTERNS = [
    re.compile(r'.*thumbdata.*', re.IGNORECASE),
    re.compile(r'^\..+'),                    # dot-prefixed cache
    re.compile(r'^[0-9]+$'),                  # all digits
    re.compile(r'^[a-f0-9]{10,}$', re.I),     # hash-like
]

# ================= LOGGING =================

def setup_logging(dry_run: bool):
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"cleanup_log_{ts}.log"

    handlers = [logging.StreamHandler()]
    if not dry_run:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=handlers
    )
    return log_file

def format_size(b):
    for u in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} TB"

# ================= HELPERS =================

def is_whatsapp_backup(path: Path) -> bool:
    return any(p.match(path.name) for p in WHATSAPP_DELETE_PATTERNS)

def is_no_media_no_ext(path: Path):
    """
    OnePlus-specific no-media detection:
    - No extension
    - Numeric / hash / thumbdata / dot-prefixed names
    - Any size (cache blobs can be very large)
    """
    name = path.name
    size = path.stat().st_size

    # Zero-byte junk
    if size == 0:
        return True, "Zero-byte cache"

    for pat in NO_EXT_CACHE_PATTERNS:
        if pat.match(name):
            return True, f"Cache pattern: {pat.pattern}"

    return False, "Not cache"

# ================= CORE =================

def scan_and_clean(root_path: str, dry_run: bool):
    root = Path(root_path)
    if not root.exists():
        logging.error(f"Invalid path: {root}")
        return

    deleted = 0
    reclaimed = 0

    if dry_run:
        logging.info("--- DRY RUN (NO FILES DELETED) ---")
        logging.info(f"{'PATH':<70} | {'SIZE':<10} | REASON")
        logging.info("-" * 110)

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        suffix = path.suffix.lower()
        size = path.stat().st_size

        # --- DELETE WhatsApp encrypted backups ---
        if is_whatsapp_backup(path):
            reason = "WhatsApp encrypted backup"

        # --- Protect real user data ---
        elif suffix in SAFE_EXTENSIONS:
            continue

        # --- Explicit cache extensions ---
        elif suffix in TARGET_EXTENSIONS:
            reason = f"Cache ext {suffix}"

        # --- No-extension OnePlus cache ---
        elif suffix == "":
            is_cache, reason = is_no_media_no_ext(path)
            if not is_cache:
                continue

        else:
            continue

        # ACTION
        if dry_run:
            logging.info(f"{str(path):<70} | {format_size(size):<10} | {reason}")
        else:
            try:
                path.unlink()
                deleted += 1
                reclaimed += size
                logging.info(f"Deleted: {path} ({format_size(size)}) [{reason}]")
            except Exception as e:
                logging.error(f"Failed to delete {path}: {e}")

    logging.info("-" * 60)
    if dry_run:
        logging.info("DRY RUN COMPLETE")
    else:
        logging.info(f"FILES DELETED: {deleted}")
        logging.info(f"SPACE RECLAIMED: {format_size(reclaimed)}")

# ================= CLI =================

if __name__ == "__main__":
    parser = argparse.ArgumentParser("OnePlus / Android No-Media + WhatsApp Cleaner")
    parser.add_argument("source", nargs="?", help="Root directory to scan")
    parser.add_argument("--delete", action="store_true", help="Actually delete files")

    args = parser.parse_args()

    source = args.source
    if not source:
        source = input("Enter source directory: ").strip().strip('"')
        if not source:
            print("No source provided. Exiting.")
            exit(1)

    dry = not args.delete
    log_file = setup_logging(dry)
    scan_and_clean(source, dry_run=dry)

    if not dry:
        print(f"\nLog saved to: {log_file}")
