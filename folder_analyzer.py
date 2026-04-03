#!/usr/bin/env python3
"""
Folder Size Analyzer - Shows which folders/files take the most space.
"""

import os
import argparse
from collections import defaultdict


def format_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def get_size(path):
    """Recursively calculate total size of a path."""
    total = 0
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
        for entry in os.scandir(path):
            try:
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += get_size(entry.path)
            except (PermissionError, OSError):
                pass
    except (PermissionError, OSError):
        pass
    return total


def bar(fraction, width=40):
    filled = round(fraction * width)
    return "█" * filled + "░" * (width - filled)


def analyze_folder(path, top=10, show_files=False, min_size_mb=0):
    """
    Analyze a directory and report its largest subdirectories (and optionally files).

    Args:
        path        : Root directory to analyze
        top         : How many largest items to show
        show_files  : Also list individual large files
        min_size_mb : Only report items larger than this (MB)
    """

    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return

    min_bytes = min_size_mb * 1024 * 1024
    items = []
    ext_sizes = defaultdict(int)
    file_count = 0

    print(f"🔍 Analyzing: {path}\n")

    for entry in os.scandir(path):
        try:
            size = get_size(entry.path)
        except (PermissionError, OSError):
            size = 0

        if size >= min_bytes:
            items.append((entry.name, size, entry.path, entry.is_dir()))

        # Extension breakdown
        if entry.is_file(follow_symlinks=False):
            ext = os.path.splitext(entry.name)[1].lower() or "(no ext)"
            ext_sizes[ext] += entry.stat().st_size
            file_count += 1

    items.sort(key=lambda x: x[1], reverse=True)
    total_size = sum(s for _, s, _, _ in items)

    # ── Top items ─────────────────────────────────────────────────────────────
    print(f"📦 Total tracked size : {format_size(total_size)}")
    print(f"{'='*62}\n")
    print(f"🔝 Top {min(top, len(items))} largest items:\n")

    for i, (name, size, item_path, is_dir) in enumerate(items[:top], 1):
        pct = (size / total_size * 100) if total_size else 0
        icon = "📁" if is_dir else "📄"
        print(f"  {i:2}. {icon} {name}")
        print(f"      {bar(pct/100)}  {format_size(size):>10}  ({pct:.1f}%)")
        print(f"      {item_path}\n")

    # ── Extension breakdown ───────────────────────────────────────────────────
    if ext_sizes:
        print(f"\n📊 Extension breakdown ({file_count} files at root level):\n")
        sorted_exts = sorted(ext_sizes.items(), key=lambda x: -x[1])
        for ext, size in sorted_exts[:15]:
            pct = (size / total_size * 100) if total_size else 0
            print(f"  {ext:<12} {format_size(size):>10}  {bar(pct/100, width=20)}  {pct:.1f}%")

    # ── Large individual files ────────────────────────────────────────────────
    if show_files:
        large_files = []
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    fsize = os.path.getsize(fpath)
                    if fsize >= min_bytes:
                        large_files.append((fname, fsize, fpath))
                except OSError:
                    pass

        large_files.sort(key=lambda x: -x[1])
        print(f"\n\n📄 Largest individual files:\n")
        for i, (fname, fsize, fpath) in enumerate(large_files[:top], 1):
            print(f"  {i:2}. {format_size(fsize):>10}  {fname}")
            print(f"       {fpath}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze folder sizes and show the biggest consumers.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python folder_analyzer.py /path/to/folder
  python folder_analyzer.py /path/to/folder --top 20 --show-files
  python folder_analyzer.py /path/to/folder --min-size 50
        """,
    )
    parser.add_argument("path", help="Directory to analyze")
    parser.add_argument("--top", type=int, default=10, help="Number of top items to display (default: 10)")
    parser.add_argument("--show-files", action="store_true", help="Also list largest individual files")
    parser.add_argument("--min-size", type=float, default=0,
                        metavar="MB", help="Only show items larger than N MB (default: 0)")

    args = parser.parse_args()
    analyze_folder(args.path, top=args.top, show_files=args.show_files, min_size_mb=args.min_size)
