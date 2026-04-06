#!/usr/bin/env python3
"""
Tree Structure to ZIP Generator - Works with your exact format
"""

import zipfile
import re
import os

def parse_tree_structure(lines):
    """Parse tree structure and return files with full paths"""
    
    files_with_paths = []
    folders = set()
    
    # Track current path based on indentation level
    path_stack = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        
        # Calculate depth by counting leading spaces and tree characters
        # Count the number of "│   " or "    " or "├──" before the text
        original_line = line
        
        # Remove the actual content to count depth
        content_start = 0
        for i, char in enumerate(line):
            if char not in ['│', '├', '└', '─', ' ', '|']:
                content_start = i
                break
        
        # Calculate depth based on the tree characters
        prefix = line[:content_start]
        # Each "│   " or "    " or "├──" represents one level
        depth = prefix.count('│') + prefix.count('├') + prefix.count('└')
        # Also count spaces in groups of 4
        if depth == 0:
            depth = len(prefix) // 4
        
        # Clean the line - remove tree characters
        cleaned = re.sub(r'^[│├└─\s]+', '', line)
        
        # Remove comments (anything after #)
        if '#' in cleaned:
            cleaned = cleaned.split('#')[0].strip()
        
        # Remove parentheses content like "(your images here)"
        cleaned = re.sub(r'\([^)]*\)', '', cleaned).strip()
        
        if not cleaned:
            continue
        
        # Check if it's a directory (ends with / or has no extension and no dot)
        is_dir = cleaned.endswith('/')
        name = cleaned.rstrip('/').strip()
        
        if not name:
            continue
        
        # Adjust path stack based on depth
        if depth == 0:
            # Root level
            path_stack = [name]
        elif depth <= len(path_stack):
            # Going back up or same level
            path_stack = path_stack[:depth]
            path_stack.append(name)
        else:
            # Going deeper
            path_stack.append(name)
        
        # Build the full path
        if len(path_stack) > 1:
            full_path = '/'.join(path_stack)
        else:
            full_path = path_stack[0]
        
        if is_dir:
            # It's a directory
            folders.add(f"{full_path}/")
            # Also add parent directories
            parts = full_path.split('/')
            for i in range(1, len(parts)):
                parent = '/'.join(parts[:i])
                folders.add(f"{parent}/")
        else:
            # It's a file
            files_with_paths.append(full_path)
            # Add its parent directory
            if '/' in full_path:
                parent_dir = full_path.rsplit('/', 1)[0]
                folders.add(f"{parent_dir}/")
                # Add all parent directories
                parts = parent_dir.split('/')
                for i in range(1, len(parts)):
                    parent = '/'.join(parts[:i])
                    folders.add(f"{parent}/")
    
    return folders, files_with_paths

def main():
    print("\n" + "="*60)
    print("📁 TREE STRUCTURE TO ZIP GENERATOR")
    print("="*60)
    print("\n📝 Paste your tree structure (type 'END' when done):")
    print("-"*60)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled")
            return
    
    if not lines:
        print("\n❌ No structure provided!")
        return
    
    print("\n🔄 Creating zip with proper folder structure...", end=" ", flush=True)
    
    # Parse the tree structure
    folders, files = parse_tree_structure(lines)
    
    if not folders and not files:
        print("\n❌ Could not parse structure. Please check format.")
        return
    
    # Create the zip file
    zip_name = "output.zip"
    
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all folders
            for folder in sorted(folders):
                if folder and folder != '/':
                    zipf.writestr(folder, "")
            
            # Add all files
            for file_path in sorted(files):
                if file_path:
                    zipf.writestr(file_path, "")
        
        print("✅ DONE!")
        print(f"\n📦 ZIP created: {os.path.abspath(zip_name)}")
        print(f"   📁 {len(folders)} folders, 📄 {len(files)} files")
        
        # Show the structure that was created
        print("\n📁 Generated structure:")
        print("-"*50)
        
        # Display the structure
        for item in sorted(folders)[:15]:
            print(f"  📁 {item}")
        for item in sorted(files)[:15]:
            print(f"  📄 {item}")
        
        if len(folders) + len(files) > 30:
            print(f"  ... and {len(folders) + len(files) - 30} more items")
        
        print("\n✨ Ready to use!")
        
    except Exception as e:
        print(f"\n❌ Error creating zip: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")