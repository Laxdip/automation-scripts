#!/usr/bin/env python3
"""
Extension Changer - Bulk change file extensions with safety checks.
"""

import os
import argparse


def format_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.0f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} GB"


def change_extension(path, old_ext, new_ext, recursive=False, dry_run=True):
    """
    Bulk-change file extensions.

    Args:
        path      : Target directory
        old_ext   : Extension to replace (with or without leading dot)
        new_ext   : Replacement extension (with or without leading dot)
        recursive : Walk subdirectories
        dry_run   : When True, only preview changes
    """

    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return []

    # Normalise extensions
    old_ext = old_ext if old_ext.startswith(".") else f".{old_ext}"
    new_ext = new_ext if new_ext.startswith(".") else f".{new_ext}"

    if old_ext.lower() == new_ext.lower():
        print("⚠️  Old and new extensions are the same — nothing to do.")
        return []

    changed = []
    skipped = 0

    walker = os.walk(path) if recursive else [(path, [], os.listdir(path))]

    print(f"{'[DRY RUN] ' if dry_run else ''}Changing *{old_ext}  →  *{new_ext}\n")

    for root, _, files in walker:
        for filename in sorted(files):
            if not filename.lower().endswith(old_ext.lower()):
                continue

            new_filename = filename[: -len(old_ext)] + new_ext
            old_path = os.path.join(root, filename)
            new_path = os.path.join(root, new_filename)

            if os.path.exists(new_path):
                print(f"  ⚠️  Skipped (target exists): {filename}")
                skipped += 1
                continue

            if dry_run:
                print(f"  {filename}  →  {new_filename}")
            else:
                os.rename(old_path, new_path)
                print(f"  ✅ {filename}  →  {new_filename}")

            changed.append((old_path, new_path))

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Changed: {len(changed)}  |  Skipped: {skipped}")
    if dry_run:
        print("Add --execute to apply changes.")
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bulk-change file extensions.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python extension_changer.py /path/to/folder .txt .md --dry-run
  python extension_changer.py /path/to/folder .jpeg .jpg --execute
  python extension_changer.py /path/to/folder .htm .html --recursive --execute
        """,
    )
    parser.add_argument("path", help="Target folder")
    parser.add_argument("old_ext", help="Extension to replace  (e.g. .txt)")
    parser.add_argument("new_ext", help="Replacement extension (e.g. .md)")
    parser.add_argument("--recursive", action="store_true", help="Process subdirectories too")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default)")
    parser.add_argument("--execute", action="store_true", help="Apply changes")

    args = parser.parse_args()

    change_extension(
        path=args.path,
        old_ext=args.old_ext,
        new_ext=args.new_ext,
        recursive=args.recursive,
        dry_run=not args.execute,
    )
