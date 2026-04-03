#!/usr/bin/env python3
"""
Recent Files Tracker - Lists files modified/created in the last X days.
Supports filtering, sorting, CSV export, and size summaries.
"""

import os
import time
import csv
import argparse
from datetime import datetime


def format_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def get_file_info(filepath):
    try:
        stat = os.stat(filepath)
        return {
            "path": filepath,
            "name": os.path.basename(filepath),
            "ext": os.path.splitext(filepath)[1].lower(),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
        }
    except (OSError, PermissionError):
        return None


def recent_files_tracker(
    path,
    days=7,
    limit=50,
    sort_by="modified",
    extensions=None,
    min_size=0,
    max_size=None,
    export_csv=None,
    show_created=False,
):
    """
    Find files modified in the last N days.

    Args:
        path        : Root directory to scan
        days        : Look-back window in days
        limit       : Max results to display
        sort_by     : 'modified' | 'size' | 'name' | 'type'
        extensions  : Whitelist of extensions (e.g. ['.py', '.txt'])
        min_size    : Minimum file size in bytes
        max_size    : Maximum file size in bytes (None = no limit)
        export_csv  : Path to write CSV report
        show_created: Also show file creation time
    """

    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return []

    cutoff = time.time() - (days * 86400)
    files_found = []

    print(f"🔍 Scanning : {path}")
    print(f"📅 Last     : {days} day(s)  (since {datetime.fromtimestamp(cutoff).strftime('%Y-%m-%d %H:%M')})")
    if extensions:
        print(f"📎 Filter   : {', '.join(extensions)}")
    print("-" * 70)

    for root, dirs, filenames in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for filename in filenames:
            filepath = os.path.join(root, filename)
            info = get_file_info(filepath)
            if not info:
                continue
            if info["modified"] < cutoff:
                continue
            if extensions and info["ext"] not in extensions:
                continue
            if info["size"] < min_size:
                continue
            if max_size is not None and info["size"] > max_size:
                continue
            files_found.append(info)

    # Sort
    sort_keys = {
        "modified": lambda x: x["modified"],
        "size":     lambda x: x["size"],
        "name":     lambda x: x["name"].lower(),
        "type":     lambda x: x["ext"],
    }
    files_found.sort(key=sort_keys.get(sort_by, sort_keys["modified"]), reverse=(sort_by != "name"))

    total_size = sum(f["size"] for f in files_found)
    display = files_found[:limit]

    print(f"\n📁 Found {len(files_found)} file(s) — showing {len(display)}  (sorted by {sort_by})\n")

    for i, info in enumerate(display, 1):
        mod_str = datetime.fromtimestamp(info["modified"]).strftime("%Y-%m-%d %H:%M:%S")
        size_str = format_size(info["size"])
        print(f"  {i:3}. {mod_str}  {size_str:>10}  {info['name']}")
        if show_created:
            cre_str = datetime.fromtimestamp(info["created"]).strftime("%Y-%m-%d %H:%M:%S")
            print(f"       Created : {cre_str}")
        print(f"       📍 {info['path']}\n")

    print("=" * 70)
    print(f"📊 Total recent files : {len(files_found)}")
    print(f"   Combined size      : {format_size(total_size)}")

    if export_csv:
        with open(export_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["name", "path", "size", "modified", "created", "ext"]
            )
            writer.writeheader()
            for info in files_found:
                writer.writerow({
                    "name":     info["name"],
                    "path":     info["path"],
                    "size":     info["size"],
                    "modified": datetime.fromtimestamp(info["modified"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "created":  datetime.fromtimestamp(info["created"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "ext":      info["ext"],
                })
        print(f"\n📄 Exported → {export_csv}")

    return files_found


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find recently modified files in a directory tree.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python recent_files_tracker.py /path/to/folder
  python recent_files_tracker.py /path/to/folder --days 30 --sort size
  python recent_files_tracker.py /path/to/folder --ext .py .txt --export recent.csv
  python recent_files_tracker.py /path/to/folder --min-size 1048576  # >1 MB
        """,
    )
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument("--days",     type=int,   default=7,        help="Days to look back (default: 7)")
    parser.add_argument("--limit",    type=int,   default=50,       help="Max files to display (default: 50)")
    parser.add_argument("--sort",     choices=["modified", "size", "name", "type"], default="modified")
    parser.add_argument("--ext",      nargs="+",  metavar="EXT",    help="Only show these extensions")
    parser.add_argument("--min-size", type=int,   default=0,        metavar="BYTES")
    parser.add_argument("--max-size", type=int,   default=None,     metavar="BYTES")
    parser.add_argument("--export",   metavar="FILE",               help="Export results to CSV")
    parser.add_argument("--show-created", action="store_true",      help="Also display file creation time")

    args = parser.parse_args()
    exts = [e if e.startswith(".") else f".{e}" for e in args.ext] if args.ext else None

    recent_files_tracker(
        path=args.path,
        days=args.days,
        limit=args.limit,
        sort_by=args.sort,
        extensions=exts,
        min_size=args.min_size,
        max_size=args.max_size,
        export_csv=args.export,
        show_created=args.show_created,
    )
