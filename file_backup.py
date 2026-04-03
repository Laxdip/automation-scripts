#!/usr/bin/env python3
"""
File Backup - Copy / mirror files to a backup location with optional versioning.
Supports incremental backups (only changed files), compression, and restore.
"""

import os
import shutil
import hashlib
import argparse
import zipfile
import json
from datetime import datetime
from pathlib import Path


MANIFEST_FILE = ".backup_manifest.json"


def format_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def file_hash(filepath, chunk=65536):
    h = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for block in iter(lambda: f.read(chunk), b""):
                h.update(block)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def load_manifest(backup_root):
    path = os.path.join(backup_root, MANIFEST_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_manifest(backup_root, manifest):
    path = os.path.join(backup_root, MANIFEST_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def backup(
    source,
    dest,
    incremental=True,
    versioned=False,
    compress=False,
    extensions=None,
    exclude_dirs=None,
    dry_run=True,
):
    """
    Back up files from source → dest.

    Args:
        source      : Source directory
        dest        : Backup destination
        incremental : Only copy files that have changed (uses MD5 manifest)
        versioned   : Stamp destination with current datetime
        compress    : Create a .zip archive instead of plain copy
        extensions  : Only back up these extensions
        exclude_dirs: Directory names to skip
        dry_run     : When True, only preview
    """

    if not os.path.exists(source):
        print(f"❌ Source does not exist: {source}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if versioned:
        dest = os.path.join(dest, timestamp)

    if compress:
        zip_path = (dest if dest.endswith(".zip") else dest) + (
            "" if dest.endswith(".zip") else f"_{timestamp}.zip"
        )
        _backup_compressed(source, zip_path, extensions, exclude_dirs, dry_run)
        return

    exclude_dirs = set(exclude_dirs or [])
    manifest = load_manifest(dest) if incremental and not versioned else {}

    copied = skipped = errors = 0
    total_bytes = 0

    print(f"{'[DRY RUN] ' if dry_run else ''}Backup: {source}  →  {dest}")
    print(f"   Incremental: {incremental}  |  Versioned: {versioned}\n")

    new_manifest = {}

    for root, dirs, files in os.walk(source):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in exclude_dirs]

        rel_root = os.path.relpath(root, source)

        for fname in sorted(files):
            if extensions:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in extensions:
                    continue

            src_path = os.path.join(root, fname)
            rel_path = os.path.join(rel_root, fname)
            dst_path = os.path.join(dest, rel_path)

            try:
                fhash = file_hash(src_path)
            except Exception:
                fhash = None

            # Incremental: skip if unchanged
            if incremental and fhash and manifest.get(rel_path) == fhash:
                skipped += 1
                new_manifest[rel_path] = fhash
                continue

            size = os.path.getsize(src_path)
            total_bytes += size

            if dry_run:
                print(f"  COPY  {rel_path}  ({format_size(size)})")
            else:
                try:
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    print(f"  ✅  {rel_path}  ({format_size(size)})")
                    copied += 1
                except Exception as e:
                    print(f"  ⚠️   {rel_path}: {e}")
                    errors += 1
                    continue

            if fhash:
                new_manifest[rel_path] = fhash

            copied += 1

    if not dry_run and not versioned:
        full_manifest = {**manifest, **new_manifest}
        save_manifest(dest, full_manifest)

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Done")
    print(f"  Copied  : {copied}")
    print(f"  Skipped : {skipped}  (unchanged)")
    print(f"  Errors  : {errors}")
    print(f"  Data    : {format_size(total_bytes)}")
    if dry_run:
        print("\nAdd --execute to perform the backup.")


def _backup_compressed(source, zip_path, extensions, exclude_dirs, dry_run):
    exclude_dirs = set(exclude_dirs or [])
    total = 0

    print(f"{'[DRY RUN] ' if dry_run else ''}Creating archive: {zip_path}")

    if dry_run:
        for root, dirs, files in os.walk(source):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for fname in files:
                if extensions:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in extensions:
                        continue
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, source)
                size = os.path.getsize(fpath)
                total += size
                print(f"  ADD  {rel}  ({format_size(size)})")
        print(f"\n[DRY RUN] Archive would contain: {format_size(total)}")
        print("Add --execute to create the zip.")
        return

    os.makedirs(os.path.dirname(os.path.abspath(zip_path)), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for fname in files:
                if extensions:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in extensions:
                        continue
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, source)
                zf.write(fpath, rel)
                total += os.path.getsize(fpath)
                print(f"  ✅  {rel}")

    zip_size = os.path.getsize(zip_path)
    print(f"\n✅ Archive: {zip_path}")
    print(f"   Original : {format_size(total)}")
    print(f"   Compressed: {format_size(zip_size)}  ({100*(1-zip_size/total):.1f}% saved)")


def restore(backup_dir, dest, dry_run=True):
    """Restore files from backup_dir back to dest."""
    if not os.path.exists(backup_dir):
        print(f"❌ Backup does not exist: {backup_dir}")
        return

    restored = skipped = 0
    print(f"{'[DRY RUN] ' if dry_run else ''}Restore: {backup_dir}  →  {dest}\n")

    for root, dirs, files in os.walk(backup_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if fname == MANIFEST_FILE:
                continue
            src_path = os.path.join(root, fname)
            rel = os.path.relpath(src_path, backup_dir)
            dst_path = os.path.join(dest, rel)

            if dry_run:
                print(f"  RESTORE  {rel}")
            else:
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
                print(f"  ✅  {rel}")
            restored += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Restored: {restored}  |  Skipped: {skipped}")
    if dry_run:
        print("Add --execute to apply.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backup and restore files with optional versioning and compression.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python file_backup.py backup /source /dest --dry-run
  python file_backup.py backup /source /dest --execute
  python file_backup.py backup /source /dest --versioned --execute
  python file_backup.py backup /source /dest --compress --execute
  python file_backup.py backup /source /dest --incremental --ext .py .txt --execute
  python file_backup.py restore /dest/20240101_120000 /restored --execute
        """,
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # backup subcommand
    bp = sub.add_parser("backup", help="Back up files")
    bp.add_argument("source",                   help="Source directory")
    bp.add_argument("dest",                     help="Backup destination")
    bp.add_argument("--incremental", action="store_true", default=True,
                    help="Only copy changed files (default: True)")
    bp.add_argument("--full",        action="store_true", help="Force full backup (disable incremental)")
    bp.add_argument("--versioned",   action="store_true", help="Timestamp the destination folder")
    bp.add_argument("--compress",    action="store_true", help="Create a .zip archive")
    bp.add_argument("--ext",         nargs="+", metavar="EXT", help="Only back up these extensions")
    bp.add_argument("--exclude-dirs",nargs="+", metavar="DIR", help="Directory names to skip")
    bp.add_argument("--dry-run",     action="store_true", default=True)
    bp.add_argument("--execute",     action="store_true")

    # restore subcommand
    rp = sub.add_parser("restore", help="Restore files from backup")
    rp.add_argument("backup_dir", help="Backup directory")
    rp.add_argument("dest",       help="Restore destination")
    rp.add_argument("--dry-run",  action="store_true", default=True)
    rp.add_argument("--execute",  action="store_true")

    args = parser.parse_args()

    if args.command == "backup":
        exts = [e if e.startswith(".") else f".{e}" for e in args.ext] if args.ext else None
        backup(
            source=args.source,
            dest=args.dest,
            incremental=not args.full,
            versioned=args.versioned,
            compress=args.compress,
            extensions=exts,
            exclude_dirs=args.exclude_dirs,
            dry_run=not args.execute,
        )
    elif args.command == "restore":
        restore(
            backup_dir=args.backup_dir,
            dest=args.dest,
            dry_run=not args.execute,
        )
