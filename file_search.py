#!/usr/bin/env python3
"""
File Search - Find files by name pattern, content, size, date, or extension.
Pure stdlib — no external dependencies.
"""

import os
import re
import argparse
import csv
from datetime import datetime, timedelta
from fnmatch import fnmatch


def format_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def search(
    path,
    name_pattern=None,
    content_pattern=None,
    extensions=None,
    min_size=None,
    max_size=None,
    modified_after=None,
    modified_before=None,
    regex=False,
    case_sensitive=False,
    limit=200,
    exclude_dirs=None,
    export_csv=None,
):
    """
    Search for files matching given criteria.

    Args:
        path             : Root directory
        name_pattern     : Glob (or regex) pattern for filename
        content_pattern  : Search string (or regex) inside file content
        extensions       : Whitelist of extensions
        min_size         : Minimum file size in bytes
        max_size         : Maximum file size in bytes
        modified_after   : datetime — only files newer than this
        modified_before  : datetime — only files older than this
        regex            : Treat patterns as regex (else glob / plain text)
        case_sensitive   : Case-sensitive matching
        limit            : Max results
        exclude_dirs     : Directory names to skip
        export_csv       : Write results to this CSV file
    """

    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return []

    exclude_dirs = set(exclude_dirs or [])
    results = []

    flags = 0 if case_sensitive else re.IGNORECASE

    # Compile content regex once
    content_re = None
    if content_pattern:
        pat = content_pattern if regex else re.escape(content_pattern)
        try:
            content_re = re.compile(pat, flags)
        except re.error as e:
            print(f"❌ Invalid content pattern: {e}")
            return []

    print(f"🔍 Searching in: {path}")
    if name_pattern:
        print(f"   Name       : {name_pattern}  ({'regex' if regex else 'glob'})")
    if content_pattern:
        print(f"   Content    : {content_pattern}")
    if extensions:
        print(f"   Extensions : {', '.join(extensions)}")
    print()

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in exclude_dirs]

        for fname in files:
            fpath = os.path.join(root, fname)

            # ── Extension filter ─────────────────────────────────────────────
            if extensions:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in extensions:
                    continue

            # ── Name pattern ─────────────────────────────────────────────────
            if name_pattern:
                if regex:
                    if not re.search(name_pattern, fname, flags):
                        continue
                else:
                    check = fname if case_sensitive else fname.lower()
                    pat   = name_pattern if case_sensitive else name_pattern.lower()
                    if not fnmatch(check, pat):
                        continue

            # ── Stat checks ──────────────────────────────────────────────────
            try:
                stat = os.stat(fpath)
            except (OSError, PermissionError):
                continue

            size  = stat.st_size
            mtime = stat.st_mtime

            if min_size  is not None and size < min_size:
                continue
            if max_size  is not None and size > max_size:
                continue
            if modified_after  and mtime < modified_after.timestamp():
                continue
            if modified_before and mtime > modified_before.timestamp():
                continue

            # ── Content search ───────────────────────────────────────────────
            matching_lines = []
            if content_re:
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        for lineno, line in enumerate(f, 1):
                            if content_re.search(line):
                                matching_lines.append((lineno, line.rstrip()))
                    if not matching_lines:
                        continue
                except (OSError, PermissionError):
                    continue

            results.append({
                "path":     fpath,
                "name":     fname,
                "size":     size,
                "modified": mtime,
                "lines":    matching_lines,
            })

            if len(results) >= limit:
                print(f"⚠️  Limit of {limit} results reached. Use --limit to increase.\n")
                break
        else:
            continue
        break

    # ── Display ───────────────────────────────────────────────────────────────
    print(f"Found {len(results)} match(es):\n")
    for i, r in enumerate(results, 1):
        mod_str = datetime.fromtimestamp(r["modified"]).strftime("%Y-%m-%d %H:%M")
        print(f"  {i:4}. {r['name']}  ({format_size(r['size'])})  [{mod_str}]")
        print(f"        {r['path']}")
        for lineno, line in r["lines"][:5]:
            print(f"        L{lineno}: {line[:120]}")
        if len(r["lines"]) > 5:
            print(f"        … and {len(r['lines'])-5} more match(es)")
        print()

    # ── Export ────────────────────────────────────────────────────────────────
    if export_csv and results:
        with open(export_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "path", "size", "modified", "matching_lines"])
            for r in results:
                lines_str = " | ".join(f"L{n}: {l}" for n, l in r["lines"][:10])
                writer.writerow([
                    r["name"], r["path"], r["size"],
                    datetime.fromtimestamp(r["modified"]).strftime("%Y-%m-%d %H:%M:%S"),
                    lines_str,
                ])
        print(f"📄 Results exported → {export_csv}")

    return results


def parse_date(s):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise argparse.ArgumentTypeError(f"Cannot parse date: {s}  (use YYYY-MM-DD)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search for files by name, content, size, or date.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python file_search.py /path/to/folder --name "*.py"
  python file_search.py /path/to/folder --name "report*" --ext .pdf .docx
  python file_search.py /path/to/folder --content "TODO" --ext .py
  python file_search.py /path/to/folder --min-size 1048576 --max-size 104857600
  python file_search.py /path/to/folder --after 2024-01-01 --before 2024-12-31
  python file_search.py /path/to/folder --name "log.*" --regex --export results.csv
        """,
    )
    parser.add_argument("path",                               help="Root directory to search")
    parser.add_argument("--name",       metavar="PATTERN",   help="Filename glob pattern (e.g. '*.txt')")
    parser.add_argument("--content",    metavar="TEXT",       help="Search inside file content")
    parser.add_argument("--ext",        nargs="+",           help="Extensions to include (e.g. .py .txt)")
    parser.add_argument("--min-size",   type=int, metavar="BYTES")
    parser.add_argument("--max-size",   type=int, metavar="BYTES")
    parser.add_argument("--after",      type=parse_date, metavar="DATE", help="Modified after  YYYY-MM-DD")
    parser.add_argument("--before",     type=parse_date, metavar="DATE", help="Modified before YYYY-MM-DD")
    parser.add_argument("--regex",      action="store_true", help="Treat patterns as regex")
    parser.add_argument("--case",       action="store_true", help="Case-sensitive matching")
    parser.add_argument("--limit",      type=int, default=200)
    parser.add_argument("--exclude-dirs", nargs="+", metavar="DIR")
    parser.add_argument("--export",     metavar="FILE",       help="Export results to CSV")

    args = parser.parse_args()
    exts = [e if e.startswith(".") else f".{e}" for e in args.ext] if args.ext else None

    search(
        path=args.path,
        name_pattern=args.name,
        content_pattern=args.content,
        extensions=exts,
        min_size=args.min_size,
        max_size=args.max_size,
        modified_after=args.after,
        modified_before=args.before,
        regex=args.regex,
        case_sensitive=args.case,
        limit=args.limit,
        exclude_dirs=args.exclude_dirs,
        export_csv=args.export,
    )
