#!/usr/bin/env python3
"""
File Watcher - Monitor a directory for real-time changes (create/modify/delete/rename).
Uses only stdlib — no third-party dependencies required.
"""

import os
import sys
import time
import argparse
import hashlib
import csv
from datetime import datetime


def format_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def snapshot(path, recursive=True, extensions=None):
    """
    Return a dict mapping filepath → (mtime, size) for every file under path.
    """
    state = {}
    walker = os.walk(path) if recursive else [(path, [], os.listdir(path))]

    for root, dirs, files in walker:
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if extensions:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in extensions:
                    continue
            fpath = os.path.join(root, fname)
            try:
                stat = os.stat(fpath)
                state[fpath] = (stat.st_mtime, stat.st_size)
            except (OSError, PermissionError):
                pass
    return state


def diff_snapshots(old, new):
    """Return lists of (created, modified, deleted) file paths."""
    created  = [p for p in new if p not in old]
    deleted  = [p for p in old if p not in new]
    modified = [p for p in new if p in old and new[p] != old[p]]
    return created, modified, deleted


def watch(
    path,
    interval=1.0,
    recursive=True,
    extensions=None,
    log_file=None,
    events=None,
    max_events=None,
):
    """
    Poll a directory every `interval` seconds and report changes.

    Args:
        path       : Directory to watch
        interval   : Polling interval in seconds
        recursive  : Watch subdirectories
        extensions : Only watch these extensions
        log_file   : Write events to this CSV file
        events     : Set of event types to report {'created','modified','deleted'}
        max_events : Stop after this many events (None = run forever)
    """

    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return

    events = events or {"created", "modified", "deleted"}

    csv_writer = None
    csv_file_handle = None
    if log_file:
        csv_file_handle = open(log_file, "w", newline="", encoding="utf-8")
        csv_writer = csv.writer(csv_file_handle)
        csv_writer.writerow(["timestamp", "event", "path", "size"])
        print(f"📄 Logging to: {log_file}")

    print(f"👁️  Watching : {path}")
    print(f"   Interval : {interval}s  |  Recursive: {recursive}")
    if extensions:
        print(f"   Filter   : {', '.join(extensions)}")
    print(f"   Events   : {', '.join(sorted(events))}")
    print("   Press Ctrl+C to stop.\n")

    current = snapshot(path, recursive, extensions)
    event_count = 0

    try:
        while True:
            time.sleep(interval)
            new = snapshot(path, recursive, extensions)
            created, modified, deleted = diff_snapshots(current, new)

            for fpath in created:
                if "created" not in events:
                    continue
                size = new[fpath][1]
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"  [{ts}] ✅ CREATED   {fpath}  ({format_size(size)})")
                if csv_writer:
                    csv_writer.writerow([ts, "created", fpath, size])
                event_count += 1

            for fpath in modified:
                if "modified" not in events:
                    continue
                size = new[fpath][1]
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"  [{ts}] ✏️  MODIFIED  {fpath}  ({format_size(size)})")
                if csv_writer:
                    csv_writer.writerow([ts, "modified", fpath, size])
                event_count += 1

            for fpath in deleted:
                if "deleted" not in events:
                    continue
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"  [{ts}] 🗑️  DELETED   {fpath}")
                if csv_writer:
                    csv_writer.writerow([ts, "deleted", fpath, 0])
                event_count += 1

            if csv_file_handle:
                csv_file_handle.flush()

            current = new

            if max_events and event_count >= max_events:
                print(f"\n✅ Reached max events ({max_events}). Stopping.")
                break

    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopped. Total events captured: {event_count}")
    finally:
        if csv_file_handle:
            csv_file_handle.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Watch a directory for file system changes.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python file_watcher.py /path/to/folder
  python file_watcher.py /path/to/folder --interval 2 --log changes.csv
  python file_watcher.py /path/to/folder --ext .py .txt --events created modified
  python file_watcher.py /path/to/folder --no-recursive --max-events 100
        """,
    )
    parser.add_argument("path",        help="Directory to watch")
    parser.add_argument("--interval",  type=float, default=1.0,  help="Poll interval in seconds (default: 1.0)")
    parser.add_argument("--no-recursive", action="store_true",   help="Don't watch subdirectories")
    parser.add_argument("--ext",       nargs="+",  metavar="EXT",help="Only watch these extensions")
    parser.add_argument("--events",    nargs="+",  metavar="EVT",
                        choices=["created", "modified", "deleted"],
                        help="Event types to report (default: all)")
    parser.add_argument("--log",       metavar="FILE",           help="Write events to CSV file")
    parser.add_argument("--max-events",type=int,  default=None,  help="Stop after N events")

    args = parser.parse_args()
    exts = [e if e.startswith(".") else f".{e}" for e in args.ext] if args.ext else None
    evt_set = set(args.events) if args.events else {"created", "modified", "deleted"}

    watch(
        path=args.path,
        interval=args.interval,
        recursive=not args.no_recursive,
        extensions=exts,
        log_file=args.log,
        events=evt_set,
        max_events=args.max_events,
    )
