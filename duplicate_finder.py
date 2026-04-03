#!/usr/bin/env python3
"""
Duplicate File Finder - Find and optionally remove duplicate files using MD5/SHA256 hashing.
"""

import os
import hashlib
import argparse
import csv
from collections import defaultdict


def get_file_hash(filepath, algorithm="md5", chunk_size=65536):
    """Calculate hash of a file using the specified algorithm."""
    h = hashlib.new(algorithm)
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()
    except (IOError, OSError, PermissionError):
        return None


def format_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def find_duplicates(
    path,
    algorithm="md5",
    min_size=1,
    extensions=None,
    dry_run=True,
    export_csv=None,
    action="report",   # report | delete | move
    move_to=None,
):
    """
    Find duplicate files by content hash.

    Args:
        path        : Root directory to scan
        algorithm   : Hash algorithm — 'md5' or 'sha256'
        min_size    : Skip files smaller than this (bytes)
        extensions  : Only scan these extensions (e.g. ['.jpg', '.png'])
        dry_run     : When True, never delete/move anything
        export_csv  : If given a filepath, write results to CSV
        action      : 'report', 'delete', or 'move'
        move_to     : Destination folder when action='move'
    """

    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return

    if action == "move" and not move_to:
        print("❌ --move-to is required when action=move")
        return

    # ── Phase 1: group files by size (quick pre-filter) ──────────────────────
    size_map = defaultdict(list)
    total_files = 0

    print(f"🔍 Scanning: {path}  [{algorithm.upper()}]")

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for filename in files:
            filepath = os.path.join(root, filename)

            if extensions:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in extensions:
                    continue

            try:
                size = os.path.getsize(filepath)
            except OSError:
                continue

            if size < min_size:
                continue

            size_map[size].append(filepath)
            total_files += 1

    print(f"   Files considered : {total_files}")

    # ── Phase 2: hash files that share the same size ──────────────────────────
    hash_map = defaultdict(list)
    candidates = sum(len(v) for v in size_map.values() if len(v) > 1)
    print(f"   Hashing candidates: {candidates}")

    for size, filepaths in size_map.items():
        if len(filepaths) < 2:
            continue
        for fp in filepaths:
            fhash = get_file_hash(fp, algorithm)
            if fhash:
                hash_map[fhash].append(fp)

    # ── Phase 3: report / act ─────────────────────────────────────────────────
    dup_groups = {h: fps for h, fps in hash_map.items() if len(fps) > 1}
    duplicate_count = sum(len(v) - 1 for v in dup_groups.values())
    duplicate_size = sum(
        os.path.getsize(fps[0]) * (len(fps) - 1) for fps in dup_groups.values()
    )

    print(f"\n{'='*60}")
    print(f"Duplicate groups  : {len(dup_groups)}")
    print(f"Redundant files   : {duplicate_count}")
    print(f"Reclaimable space : {format_size(duplicate_size)}")
    print(f"{'='*60}\n")

    csv_rows = []

    for fhash, filepaths in sorted(dup_groups.items(), key=lambda x: -os.path.getsize(x[1][0])):
        size = os.path.getsize(filepaths[0])
        print(f"📦 [{algorithm.upper()}: {fhash[:12]}…]  {len(filepaths)} copies  ({format_size(size)} each)")
        print(f"   ✅ KEEP : {filepaths[0]}")

        for fp in filepaths[1:]:
            print(f"   ♻️  DUP  : {fp}")
            csv_rows.append({"hash": fhash, "kept": filepaths[0], "duplicate": fp, "size": size})

            if not dry_run:
                if action == "delete":
                    try:
                        os.remove(fp)
                        print(f"        🗑️  Deleted")
                    except Exception as e:
                        print(f"        ⚠️  Error: {e}")

                elif action == "move" and move_to:
                    os.makedirs(move_to, exist_ok=True)
                    dest = os.path.join(move_to, os.path.basename(fp))
                    # Avoid name collision in destination
                    counter = 1
                    while os.path.exists(dest):
                        base, ext = os.path.splitext(os.path.basename(fp))
                        dest = os.path.join(move_to, f"{base}_{counter}{ext}")
                        counter += 1
                    try:
                        import shutil
                        shutil.move(fp, dest)
                        print(f"        📂 Moved → {dest}")
                    except Exception as e:
                        print(f"        ⚠️  Error: {e}")
        print()

    if dry_run and action != "report":
        print("ℹ️  Dry-run mode — no files were modified. Add --execute to apply.\n")

    # ── Export CSV ────────────────────────────────────────────────────────────
    if export_csv and csv_rows:
        with open(export_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["hash", "kept", "duplicate", "size"])
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"📄 Results exported → {export_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find (and optionally remove) duplicate files by content hash.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python duplicate_finder.py /path/to/folder --dry-run
  python duplicate_finder.py /path/to/folder --execute --action delete
  python duplicate_finder.py /path/to/folder --execute --action move --move-to /path/to/dupes
  python duplicate_finder.py /path/to/folder --algo sha256 --ext .jpg .png --export dupes.csv
        """,
    )
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument("--algo", choices=["md5", "sha256"], default="md5", help="Hash algorithm (default: md5)")
    parser.add_argument("--min-size", type=int, default=1, help="Skip files smaller than N bytes (default: 1)")
    parser.add_argument("--ext", nargs="+", metavar="EXT", help="Only scan these extensions e.g. .jpg .png")
    parser.add_argument("--action", choices=["report", "delete", "move"], default="report",
                        help="What to do with duplicates (default: report)")
    parser.add_argument("--move-to", help="Destination folder when action=move")
    parser.add_argument("--export", metavar="FILE", help="Export results to CSV")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default)")
    parser.add_argument("--execute", action="store_true", help="Apply changes")

    args = parser.parse_args()

    exts = [e if e.startswith(".") else f".{e}" for e in args.ext] if args.ext else None

    find_duplicates(
        path=args.path,
        algorithm=args.algo,
        min_size=args.min_size,
        extensions=exts,
        dry_run=not args.execute,
        export_csv=args.export,
        action=args.action,
        move_to=args.move_to,
    )
