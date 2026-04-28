#!/usr/bin/env python3
"""
Empty Folder Finder - Find and optionally delete empty and near-empty folders.
CORRECTED VERSION - Properly detects folders with files in subdirectories
"""

import os
import sys
import argparse
from pathlib import Path

def has_files_recursive(directory):
    """
    Check if directory contains any files (at any depth).
    Returns True if any files exist anywhere in the directory tree.
    """
    try:
        for root, dirs, files in os.walk(directory):
            if files:  # Found at least one file
                return True
            # Also check for broken symlinks, etc.
            for file in files:
                if os.path.isfile(os.path.join(root, file)):
                    return True
    except (PermissionError, OSError):
        pass
    return False

def count_files_recursive(directory):
    """
    Count total number of files in directory tree.
    """
    total_files = 0
    try:
        for root, dirs, files in os.walk(directory):
            total_files += len(files)
    except (PermissionError, OSError):
        pass
    return total_files

def find_empty_folders(directory, include_near_empty=False, near_empty_threshold=3):
    """
    Find folders that contain NO files (empty) or have very few files.
    
    Args:
        directory: Root directory to scan
        include_near_empty: Include folders with few files
        near_empty_threshold: Max files to consider as near-empty
    
    Returns:
        List of tuples (folder_path, file_count, total_size_bytes)
    """
    results = []
    
    try:
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories (optional)
            if os.path.basename(root).startswith('.'):
                continue
            
            # Get recursive file count
            total_files = count_files_recursive(root)
            
            # Check if TRULY empty (no files anywhere inside)
            if total_files == 0:
                results.append((root, 0, 0))
            
            # Check for near-empty (very few files total in entire tree)
            elif include_near_empty and total_files <= near_empty_threshold:
                # Calculate total size of all files in this tree
                total_size = 0
                for subroot, subdirs, subfiles in os.walk(root):
                    for file in subfiles:
                        try:
                            file_path = os.path.join(subroot, file)
                            total_size += os.path.getsize(file_path)
                        except (OSError, IOError):
                            pass
                results.append((root, total_files, total_size))
                
    except (PermissionError, OSError) as e:
        print(f"Warning: Could not access {directory}: {e}", file=sys.stderr)
    
    return sorted(results, key=lambda x: x[1])  # Sort by file count

def delete_folders(folders, dry_run=True):
    """
    Delete folders recursively.
    
    Args:
        folders: List of folder paths to delete
        dry_run: If True, only preview; if False, actually delete
    
    Returns:
        Tuple (deleted_count, failed_count)
    """
    deleted = 0
    failed = 0
    
    for folder in folders:
        try:
            if dry_run:
                print(f"  [PREVIEW] Would delete: {folder}")
            else:
                import shutil
                shutil.rmtree(folder)
                print(f"  [DELETED] {folder}")
            deleted += 1
        except Exception as e:
            print(f"  [ERROR] Failed to delete {folder}: {e}")
            failed += 1
    
    return deleted, failed

def format_size(bytes_size):
    """Convert bytes to human-readable format."""
    if bytes_size == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def main():
    parser = argparse.ArgumentParser(
        description='Find and optionally delete TRULY empty folders (no files anywhere inside)',
        epilog='WARNING: A folder with subfolders that contain files is NOT considered empty.'
    )
    
    parser.add_argument('directory', help='Root directory to scan')
    parser.add_argument('--include-near-empty', action='store_true',
                       help='Include folders with very few total files (across all subfolders)')
    parser.add_argument('--threshold', type=int, default=3,
                       help='Max total files to consider as near-empty (default: 3)')
    parser.add_argument('--execute', action='store_true',
                       help='Actually delete folders (without this, only preview)')
    parser.add_argument('--export', help='Export results to CSV file')
    parser.add_argument('--min-depth', type=int, default=0,
                       help='Minimum folder depth to consider (0 = any depth)')
    
    args = parser.parse_args()
    
    # Validate directory
    target_dir = os.path.expanduser(args.directory)
    if not os.path.exists(target_dir):
        print(f"Error: Directory '{target_dir}' does not exist")
        sys.exit(1)
    
    print(f"Scanning: {target_dir}")
    print("NOTE: Only folders with NO files ANYWHERE inside will be considered empty")
    print(f"Including near-empty (≤{args.threshold} total files): {args.include_near_empty}")
    print()
    
    # Find empty/near-empty folders
    results = find_empty_folders(target_dir, args.include_near_empty, args.threshold)
    
    if not results:
        print("✓ No truly empty folders found!")
        print("  (Folders containing subfolders with files are NOT considered empty)")
        return
    
    # Filter by depth if needed
    if args.min_depth > 0:
        filtered_results = []
        target_depth = target_dir.rstrip(os.sep).count(os.sep)
        for folder, count, size in results:
            folder_depth = folder.count(os.sep)
            if folder_depth - target_depth >= args.min_depth:
                filtered_results.append((folder, count, size))
        results = filtered_results
    
    if not results:
        print(f"No folders at depth ≥ {args.min_depth}")
        return
    
    # Display results
    print(f"Found {len(results)} folder(s):\n")
    
    empty_folders = [(p, c, s) for p, c, s in results if c == 0]
    near_empty_folders = [(p, c, s) for p, c, s in results if 0 < c <= args.threshold]
    
    if empty_folders:
        print(f"📁 TRULY EMPTY (0 files total): {len(empty_folders)}")
        print("-" * 70)
        for folder, count, size in empty_folders[:20]:
            print(f"  {folder}")
        if len(empty_folders) > 20:
            print(f"  ... and {len(empty_folders) - 20} more")
        print()
    
    if near_empty_folders and args.include_near_empty:
        print(f"📄 NEAR-EMPTY ({args.threshold} total files or fewer): {len(near_empty_folders)}")
        print("-" * 70)
        for folder, count, size in near_empty_folders[:20]:
            print(f"  {folder}")
            print(f"    Total files in tree: {count} | Total size: {format_size(size)}")
        if len(near_empty_folders) > 20:
            print(f"  ... and {len(near_empty_folders) - 20} more")
        print()
    
    # Export to CSV
    if args.export:
        import csv
        csv_path = os.path.expanduser(args.export)
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Folder Path', 'Total Files (Recursive)', 'Total Size Bytes', 'Total Size Human'])
            for folder, count, size in results:
                writer.writerow([folder, count, size, format_size(size)])
        print(f"✓ Results exported to: {csv_path}\n")
    
    # Delete if requested
    if args.execute:
        print("⚠️  DELETE MODE ENABLED")
        folders_to_delete = [p for p, c, s in results]
        
        # Show what will be deleted
        print(f"\nWill delete {len(folders_to_delete)} folder(s):")
        for folder in folders_to_delete[:10]:
            print(f"  - {folder}")
        if len(folders_to_delete) > 10:
            print(f"  ... and {len(folders_to_delete) - 10} more")
        
        confirmation = input(f"\nAre you ABSOLUTELY sure you want to delete these folders? (yes/no): ")
        
        if confirmation.lower() == 'yes':
            print("\nDeleting folders...")
            deleted, failed = delete_folders(folders_to_delete, dry_run=False)
            print(f"\n✓ Deleted: {deleted} | Failed: {failed}")
        else:
            print("Delete cancelled.")
    else:
        print("  DRY RUN - No folders were deleted")
        print("  To actually delete, run with: --execute")
        print("    WILL DELETE ENTIRE FOLDER TREE if truly empty")

