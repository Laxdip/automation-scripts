#!/usr/bin/env python3
"""
System Cleaner - Safely delete temp files, cache, and empty folders.
Supports dry-run preview, selective targets, and per-platform paths.
"""

import os
import shutil
import platform
import argparse


def get_temp_paths(system=None):
    """Return OS-specific clean targets."""
    system = system or platform.system()

    if system == "Windows":
        user = os.environ.get("USERPROFILE", "")
        return {
            "temp_env":    os.environ.get("TEMP", ""),
            "tmp_env":     os.environ.get("TMP", ""),
            "local_temp":  os.path.join(user, "AppData", "Local", "Temp"),
            "chrome_cache": os.path.join(user, "AppData", "Local", "Google", "Chrome",
                                          "User Data", "Default", "Cache"),
            "edge_cache":  os.path.join(user, "AppData", "Local", "Microsoft", "Edge",
                                         "User Data", "Default", "Cache"),
        }
    elif system == "Darwin":
        return {
            "user_caches":  os.path.expanduser("~/Library/Caches"),
            "user_logs":    os.path.expanduser("~/Library/Logs"),
            "trash":        os.path.expanduser("~/.Trash"),
            "tmp":          "/tmp",
        }
    else:  # Linux
        return {
            "tmp":          "/tmp",
            "var_tmp":      "/var/tmp",
            "user_cache":   os.path.expanduser("~/.cache"),
            "trash":        os.path.expanduser("~/.local/share/Trash"),
        }


def format_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def get_size(path):
    total = 0
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_size(entry.path)
    except (PermissionError, OSError):
        pass
    return total


def remove_empty_dirs(path, dry_run=True):
    """Recursively remove empty subdirectories."""
    removed = 0
    for root, dirs, files in os.walk(path, topdown=False):
        if root == path:
            continue
        try:
            if not os.listdir(root):
                if dry_run:
                    print(f"  [DRY RUN] Empty dir: {root}")
                else:
                    os.rmdir(root)
                    print(f"  🗑️  Removed empty dir: {root}")
                removed += 1
        except (PermissionError, OSError):
            pass
    return removed


def clean_by_extension(path, extensions, dry_run=True, recursive=True):
    """Delete files matching given extensions."""
    deleted = 0
    freed = 0
    walker = os.walk(path) if recursive else [(path, [], os.listdir(path))]

    for root, dirs, files in walker:
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in extensions:
                fpath = os.path.join(root, fname)
                try:
                    size = os.path.getsize(fpath)
                    if dry_run:
                        print(f"  [DRY RUN] {fpath}  ({format_size(size)})")
                    else:
                        os.remove(fpath)
                        print(f"  🗑️  Deleted: {fpath}  ({format_size(size)})")
                    deleted += 1
                    freed += size
                except (PermissionError, OSError) as e:
                    print(f"  ⚠️  Error: {fpath}: {e}")

    return deleted, freed


def clean_system(targets=None, dry_run=True, remove_empty=False, extra_path=None, extra_extensions=None):
    """
    Clean OS temp / cache locations.

    Args:
        targets          : List of target keys (None = all)
        dry_run          : When True, only preview
        remove_empty     : Also remove empty directories
        extra_path       : Custom path to clean (by extension)
        extra_extensions : Extensions to delete in extra_path
    """
    all_paths = get_temp_paths()
    if targets:
        paths = {k: v for k, v in all_paths.items() if k in targets}
    else:
        paths = all_paths

    total_freed = 0
    total_cleaned = 0

    print(f"🖥️  System  : {platform.system()} {platform.release()}")
    print(f"{'[DRY RUN] ' if dry_run else ''}Scanning targets...\n")

    for key, path in paths.items():
        if not path or not os.path.exists(path):
            continue

        size = get_size(path)
        if size == 0:
            continue

        print(f"📂 [{key}]  {path}")
        print(f"   Size: {format_size(size)}")

        if not dry_run:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path, ignore_errors=True)
                    os.makedirs(path, exist_ok=True)
                print(f"   ✅ Cleaned\n")
                total_cleaned += 1
            except Exception as e:
                print(f"   ⚠️  Error: {e}\n")
        else:
            print(f"   [DRY RUN] Would clean\n")

        total_freed += size

    # Custom extension-based cleaning
    if extra_path and extra_extensions:
        exts = [e if e.startswith(".") else f".{e}" for e in extra_extensions]
        print(f"\n🧹 Custom clean: {extra_path}  extensions={exts}")
        deleted, freed = clean_by_extension(extra_path, exts, dry_run=dry_run)
        total_freed += freed
        print(f"   Files matched: {deleted}  ({format_size(freed)})")

    # Remove empty directories
    if remove_empty:
        for path in paths.values():
            if path and os.path.isdir(path):
                n = remove_empty_dirs(path, dry_run=dry_run)
                if n:
                    print(f"\n🗂️  Empty dirs {'would be ' if dry_run else ''}removed in {path}: {n}")

    print(f"\n{'='*50}")
    if dry_run:
        print(f"[DRY RUN] Reclaimable space : {format_size(total_freed)}")
        print("Add --execute to apply.")
    else:
        print(f"✅ Locations cleaned : {total_cleaned}")
        print(f"✅ Space freed       : {format_size(total_freed)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean system temp files, cache, and empty directories.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python system_cleaner.py --dry-run
  python system_cleaner.py --execute
  python system_cleaner.py --execute --remove-empty
  python system_cleaner.py --custom-path /my/folder --custom-ext .log .tmp --execute
  python system_cleaner.py --targets tmp user_cache --execute
        """,
    )
    parser.add_argument("--targets", nargs="+", metavar="KEY",
                        help="Specific targets to clean (omit for all)")
    parser.add_argument("--remove-empty", action="store_true",
                        help="Also remove empty directories")
    parser.add_argument("--custom-path",  metavar="PATH",
                        help="Additional folder to clean by extension")
    parser.add_argument("--custom-ext",   nargs="+", metavar="EXT",
                        help="Extensions to delete in --custom-path")
    parser.add_argument("--dry-run",  action="store_true", default=True, help="Preview only (default)")
    parser.add_argument("--execute",  action="store_true", help="Apply changes")

    args = parser.parse_args()

    clean_system(
        targets=args.targets,
        dry_run=not args.execute,
        remove_empty=args.remove_empty,
        extra_path=args.custom_path,
        extra_extensions=args.custom_ext,
    )
