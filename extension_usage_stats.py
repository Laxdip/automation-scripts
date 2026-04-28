"""
Extension Usage Statistics - Analyze file extension distribution in a directory.
Part of the automation-scripts collection.
"""

import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict
import json

def get_extension(filepath):
    """Extract file extension (lowercase, without dot)."""
    ext = os.path.splitext(filepath)[1]
    return ext.lower()[1:] if ext else 'NO_EXTENSION'

def analyze_directory(directory, recursive=True, include_hidden=False, min_file_size=0):
    """
    Analyze file extensions in a directory.
    
    Returns:
        Dictionary with extension stats
    """
    stats = defaultdict(lambda: {'count': 0, 'total_size': 0, 'files': []})
    total_files = 0
    total_size = 0
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories
            if not include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # Skip hidden files
                if not include_hidden and file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    
                    # Apply minimum size filter
                    if file_size >= min_file_size:
                        ext = get_extension(file_path)
                        stats[ext]['count'] += 1
                        stats[ext]['total_size'] += file_size
                        stats[ext]['files'].append(file_path)
                        
                        total_files += 1
                        total_size += file_size
                except (OSError, IOError):
                    continue
    else:
        # Non-recursive: only top level
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    if not include_hidden and item.startswith('.'):
                        continue
                    
                    file_size = os.path.getsize(item_path)
                    if file_size >= min_file_size:
                        ext = get_extension(item_path)
                        stats[ext]['count'] += 1
                        stats[ext]['total_size'] += file_size
                        stats[ext]['files'].append(item_path)
                        
                        total_files += 1
                        total_size += file_size
        except Exception as e:
            print(f"Error reading directory: {e}", file=sys.stderr)
    
    return stats, total_files, total_size

def format_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def print_bar_chart(stats_items, total_size, width=50):
    """Print ASCII bar chart for extension sizes."""
    if not stats_items:
        return
    
    max_size = stats_items[0][1]['total_size']
    
    for ext, data in stats_items:
        percentage = (data['total_size'] / total_size * 100) if total_size > 0 else 0
        bar_length = int((data['total_size'] / max_size) * width) if max_size > 0 else 0
        bar = '█' * bar_length + '░' * (width - bar_length)
        
        print(f"  {ext:15} {bar} {format_size(data['total_size']):>10} ({percentage:.1f}%)")
        print(f"                    {data['count']} files")

def main():
    parser = argparse.ArgumentParser(
        description='Analyze file extension distribution in a directory',
        epilog='Example: python extension_usage_stats.py ~/Downloads --top 10 --export stats.json'
    )
    
    parser.add_argument('directory', help='Directory to analyze')
    parser.add_argument('--recursive', action='store_true', default=True,
                       help='Scan subdirectories recursively (default: True)')
    parser.add_argument('--no-recursive', dest='recursive', action='store_false',
                       help='Only scan top-level directory')
    parser.add_argument('--include-hidden', action='store_true',
                       help='Include hidden files and directories')
    parser.add_argument('--min-size', type=int, default=0,
                       help='Minimum file size in bytes to include (default: 0)')
    parser.add_argument('--top', type=int, default=20,
                       help='Show top N extensions by size (default: 20)')
    parser.add_argument('--show-files', action='store_true',
                       help='Show sample files for each extension')
    parser.add_argument('--export', help='Export results to JSON or CSV file')
    parser.add_argument('--json', action='store_true',
                       help='Export as JSON (alternative to --export with .json)')
    
    args = parser.parse_args()
    
    # Validate directory
    target_dir = os.path.expanduser(args.directory)
    if not os.path.exists(target_dir):
        print(f"Error: Directory '{target_dir}' does not exist")
        sys.exit(1)
    
    print(f"Analyzing: {target_dir}")
    print(f"Recursive: {args.recursive}")
    print(f"Include hidden: {args.include_hidden}")
    print(f"Minimum file size: {format_size(args.min_size)}")
    print()
    
    # Perform analysis
    stats, total_files, total_size = analyze_directory(
        target_dir, 
        args.recursive, 
        args.include_hidden,
        args.min_size
    )
    
    if total_files == 0:
        print("No files found matching the criteria.")
        return
    
    # Sort by total size (descending)
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['total_size'], reverse=True)
    
    # Display summary
    print("=" * 60)
    print(f"📊 EXTENSION USAGE STATISTICS")
    print("=" * 60)
    print(f"Total files scanned: {total_files:,}")
    print(f"Total size: {format_size(total_size)}")
    print(f"Unique extensions: {len(stats)}")
    print()
    
    # Show top N
    top_n = sorted_stats[:args.top]
    other_files = sum(data['count'] for ext, data in sorted_stats[args.top:])
    other_size = sum(data['total_size'] for ext, data in sorted_stats[args.top:])
    
    print(f"📈 TOP {args.top} EXTENSIONS BY SIZE")
    print("-" * 60)
    print_bar_chart(top_n, total_size)
    
    if other_files > 0:
        print(f"\n  Other ({len(stats) - args.top} extensions)    {format_size(other_size):>10} ({other_size/total_size*100:.1f}%)")
        print(f"                    {other_files} files")
    
    print()
    
    # Show file samples if requested
    if args.show_files and args.top <= 10:
        print("📄 SAMPLE FILES")
        print("-" * 60)
        for ext, data in top_n[:5]:  # Show top 5 extensions
            print(f"\n.{ext} ({data['count']} files):")
            for file_path in data['files'][:3]:  # Show up to 3 samples
                rel_path = os.path.relpath(file_path, target_dir)
                file_size = format_size(os.path.getsize(file_path))
                print(f"  - {rel_path} ({file_size})")
    
    # Export results
    if args.export:
        export_path = os.path.expanduser(args.export)
        
        if export_path.endswith('.json') or args.json:
            # Export as JSON
            export_data = {
                'directory': target_dir,
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_human': format_size(total_size),
                'extensions': []
            }
            
            for ext, data in sorted_stats:
                export_data['extensions'].append({
                    'extension': ext,
                    'count': data['count'],
                    'total_size_bytes': data['total_size'],
                    'total_size_human': format_size(data['total_size']),
                    'percentage': (data['total_size'] / total_size * 100) if total_size > 0 else 0
                })
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"\n✓ Results exported to JSON: {export_path}")
        
        elif export_path.endswith('.csv'):
            # Export as CSV
            import csv
            with open(export_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Extension', 'File Count', 'Total Size (Bytes)', 'Total Size (Human)', 'Percentage'])
                for ext, data in sorted_stats:
                    percentage = (data['total_size'] / total_size * 100) if total_size > 0 else 0
                    writer.writerow([
                        ext, 
                        data['count'], 
                        data['total_size'], 
                        format_size(data['total_size']),
                        f"{percentage:.2f}%"
                    ])
            print(f"\n✓ Results exported to CSV: {export_path}")
        else:
            print(f"\n⚠️  Unknown export format. Use .json or .csv extension")

if __name__ == "__main__":
    main()
