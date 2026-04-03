#!/usr/bin/env python3
"""
File Organizer - Sort files into folders by type, date, or custom rules.
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ── Default type-to-folder mapping ───────────────────────────────────────────
FILE_TYPES = {
    "Images":      [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".raw", ".heic"],
    "Videos":      [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"],
    "Documents":   [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".pages", ".numbers", ".key"],
    "Audio":       [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".opus"],
    "Archives":    [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".zst"],
    "Code":        [".py", ".js", ".ts", ".html", ".css", ".cpp", ".c", ".h", ".java", ".go", ".rs", ".php", ".json", ".xml", ".yaml", ".yml", ".sh", ".bat", ".ps1", ".rb", ".swift", ".kt"],
    "Executables": [".exe", ".msi", ".app", ".deb", ".rpm", ".dmg", ".pkg"],
    "Fonts":       [".ttf", ".otf", ".woff", ".woff2", ".eot"],
    "3D_Models":   [".obj", ".stl", ".fbx", ".blend", ".gltf", ".glb"],
    "Ebooks":      [".epub", ".mobi", ".azw", ".azw3", ".fb2"],
}


def ext_to_folder(ext):
    """Return folder name for a given extension, or None if unknown."""
    ext = ext.lower()
    for folder, exts in FILE_TYPES.items():
        if ext in exts:
            return folder
    return None


def format_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} GB"


def organize_by_type(path, dest=None, dry_run=True, ignore_unknown=True):
    """Move files into subfolders based on extension."""
    dest = dest or path
    moved, skipped = 0, 0

    for filename in sorted(os.listdir(path)):
        filepath = os.path.join(path, filename)
        if os.path.isdir(filepath):
            continue

        ext = os.path.splitext(filename)[1].lower()
        folder = ext_to_folder(ext)

        if not folder:
            if ignore_unknown:
                continue
            folder = "Other"

        dest_dir = os.path.join(dest, folder)
        dest_path = os.path.join(dest_dir, filename)

        # Avoid self-move or collision
        if dest_path == filepath:
            continue
        if os.path.exists(dest_path):
            print(f"  ⚠️  Skipped (exists): {filename}  →  {folder}/")
            skipped += 1
            continue

        if dry_run:
            print(f"  {filename}  →  {folder}/")
        else:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(filepath, dest_path)
            print(f"  ✅ {filename}  →  {folder}/")
        moved += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Moved: {moved}  |  Skipped: {skipped}")
    return moved


def organize_by_date(path, dest=None, fmt="%Y/%Y-%m", dry_run=True):
    """Move files into date-based subfolders using file modification date."""
    dest = dest or path
    moved, skipped = 0, 0

    for filename in sorted(os.listdir(path)):
        filepath = os.path.join(path, filename)
        if os.path.isdir(filepath):
            continue

        try:
            mtime = os.path.getmtime(filepath)
            date_str = datetime.fromtimestamp(mtime).strftime(fmt)
        except OSError:
            continue

        dest_dir = os.path.join(dest, date_str)
        dest_path = os.path.join(dest_dir, filename)

        if dest_path == filepath:
            continue
        if os.path.exists(dest_path):
            print(f"  ⚠️  Skipped (exists): {filename}")
            skipped += 1
            continue

        if dry_run:
            print(f"  {filename}  →  {date_str}/")
        else:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(filepath, dest_path)
            print(f"  ✅ {filename}  →  {date_str}/")
        moved += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Moved: {moved}  |  Skipped: {skipped}")
    return moved


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Organize files by type or modification date.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python file_organizer.py /path/to/folder --mode type --dry-run
  python file_organizer.py /path/to/folder --mode type --execute
  python file_organizer.py /path/to/folder --mode date --date-format "%Y/%B" --execute
  python file_organizer.py /path/to/folder --mode type --dest /sorted --include-unknown --execute
        """,
    )
    parser.add_argument("path", help="Folder to organize")
    parser.add_argument("--mode", choices=["type", "date"], default="type",
                        help="Organize by file type or modification date (default: type)")
    parser.add_argument("--dest", help="Destination root folder (default: same as source)")
    parser.add_argument("--date-format", default="%Y/%Y-%m",
                        help='strftime format for date folders (default: "%%Y/%%Y-%%m")')
    parser.add_argument("--include-unknown", action="store_true",
                        help="Move unrecognised files into an 'Other' folder")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default)")
    parser.add_argument("--execute", action="store_true", help="Apply changes")

    args = parser.parse_args()
    do_run = not args.execute

    print(f"{'[DRY RUN] ' if do_run else ''}Organizing: {args.path}  [mode={args.mode}]\n")

    if args.mode == "type":
        organize_by_type(args.path, dest=args.dest, dry_run=do_run,
                         ignore_unknown=not args.include_unknown)
    else:
        organize_by_date(args.path, dest=args.dest, fmt=args.date_format, dry_run=do_run)
