#!/usr/bin/env python3
"""
Bulk Renamer - Add prefix/suffix, numbering, replace text, regex support
"""

import os
import re
import argparse


def bulk_rename(
    path,
    prefix="",
    suffix="",
    numbering=False,
    replace_from="",
    replace_to="",
    regex_pattern="",
    regex_replace="",
    lowercase=False,
    uppercase=False,
    strip_spaces=False,
    extensions=None,
    dry_run=True,
):
    """Rename multiple files with various pattern options."""

    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return []

    files = sorted(
        f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
    )

    # Filter by extension if provided
    if extensions:
        exts = [e if e.startswith(".") else f".{e}" for e in extensions]
        files = [f for f in files if os.path.splitext(f)[1].lower() in exts]

    renamed = []
    skipped = 0

    print(f"{'[DRY RUN] ' if dry_run else ''}Processing {len(files)} files in: {path}\n")

    for i, filename in enumerate(files, start=1):
        name, ext = os.path.splitext(filename)
        new_name = name

        # Regex replace (applied first, on full name)
        if regex_pattern:
            try:
                new_name = re.sub(regex_pattern, regex_replace, new_name)
            except re.error as e:
                print(f"⚠️  Invalid regex: {e}")
                continue

        # Simple text replace
        if replace_from:
            new_name = new_name.replace(replace_from, replace_to)

        # Case transformations
        if lowercase:
            new_name = new_name.lower()
        elif uppercase:
            new_name = new_name.upper()

        # Strip spaces / extra whitespace
        if strip_spaces:
            new_name = re.sub(r"\s+", "_", new_name.strip())

        # Prefix / suffix
        if prefix:
            new_name = prefix + new_name
        if suffix:
            new_name = new_name + suffix

        # Numbering (padded to length of file count)
        if numbering:
            pad = len(str(len(files)))
            new_name = f"{str(i).zfill(pad)}_{new_name}"

        new_filename = new_name + ext

        if new_filename == filename:
            skipped += 1
            continue

        old_path = os.path.join(path, filename)
        new_path = os.path.join(path, new_filename)

        # Avoid overwriting an existing file
        if os.path.exists(new_path) and new_path != old_path:
            print(f"⚠️  Skipped (target exists): {filename} → {new_filename}")
            skipped += 1
            continue

        if dry_run:
            print(f"  {filename}  →  {new_filename}")
        else:
            os.rename(old_path, new_path)
            print(f"✅ {filename}  →  {new_filename}")

        renamed.append((filename, new_filename))

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Renamed: {len(renamed)}  |  Skipped: {skipped}")
    if dry_run:
        print("Run without --dry-run to apply changes.")
    return renamed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bulk rename files with prefix, suffix, numbering, or regex.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python bulk_renamer.py /path/to/folder --prefix "2024_" --dry-run
  python bulk_renamer.py /path/to/folder --replace " " "_"
  python bulk_renamer.py /path/to/folder --numbering --suffix "_final"
  python bulk_renamer.py /path/to/folder --regex "\\d+" --regex-replace "NUM" --ext jpg png
        """,
    )
    parser.add_argument("path", help="Path to target folder")
    parser.add_argument("--prefix", default="", help="Prefix to add")
    parser.add_argument("--suffix", default="", help="Suffix to add (before extension)")
    parser.add_argument("--numbering", action="store_true", help="Prepend sequential number")
    parser.add_argument("--replace", nargs=2, metavar=("FROM", "TO"), help="Replace text in filename")
    parser.add_argument("--regex", dest="regex_pattern", default="", help="Regex pattern to match")
    parser.add_argument("--regex-replace", default="", help="Replacement string for regex match")
    parser.add_argument("--lowercase", action="store_true", help="Convert filename to lowercase")
    parser.add_argument("--uppercase", action="store_true", help="Convert filename to uppercase")
    parser.add_argument("--strip-spaces", action="store_true", help="Replace spaces with underscores")
    parser.add_argument("--ext", nargs="+", metavar="EXT", help="Only rename files with these extensions")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default: True)")
    parser.add_argument("--execute", action="store_true", help="Apply changes (disables dry-run)")

    args = parser.parse_args()
    replace_from, replace_to = args.replace if args.replace else ("", "")

    bulk_rename(
        path=args.path,
        prefix=args.prefix,
        suffix=args.suffix,
        numbering=args.numbering,
        replace_from=replace_from,
        replace_to=replace_to,
        regex_pattern=args.regex_pattern,
        regex_replace=args.regex_replace,
        lowercase=args.lowercase,
        uppercase=args.uppercase,
        strip_spaces=args.strip_spaces,
        extensions=args.ext,
        dry_run=not args.execute,
    )
