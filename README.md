![Python](https://img.shields.io/badge/Python-3.6+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

# 🔧 Automation Scripts

A collection of powerful Python automation scripts to organize files, clean your system, rename in bulk, find duplicates, analyze storage, and track recent files.

## 🚀 Scripts Overview

| Script | What it does | Command |
|--------|--------------|---------|
| **File Organizer** | Sorts files into folders by type (Images, Videos, Docs, etc.) | `python file_organizer.py ~/Downloads` |
| **System Cleaner** | Deletes temp files, cache, and trash | `python system_cleaner.py --execute` |
| **Bulk Renamer** | Add prefix/suffix, numbering, replace text | `python bulk_renamer.py ~/Pics --prefix "vacation_"` |
| **Duplicate Finder** | Finds duplicate files using MD5 hash | `python duplicate_finder.py ~/Documents` |
| **Folder Analyzer** | Shows which folders take most space | `python folder_analyzer.py ~/Downloads --top 10` |
| **Extension Changer** | Bulk change file extensions (.txt → .md) | `python extension_changer.py ext ~/Files .txt .md` |
| **Recent Files Tracker** | Lists files modified in last X days | `python recent_files_tracker.py ~/Documents --days 7` |

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/automation-scripts.git
cd automation-scripts

# No external dependencies — uses only Python standard library
```
## 📁 Script Details
##1. File Organizer (file_organizer.py)
Automatically sorts files into folders based on extension.

File type categories:
Images → .jpg, .png, .gif, .svg, .webp
Videos → .mp4, .mkv, .avi, .mov
Documents → .pdf, .docx, .txt, .md
Audio → .mp3, .wav, .flac
Archives → .zip, .rar, .7z
Code → .py, .js, .html, .css
Executables → .exe, .msi, .sh
Fonts → .ttf, .otf

# Preview what will happen
python file_organizer.py ~/Downloads --dry-run
# Actually organize files
python file_organizer.py ~/Downloads

2. System Cleaner (system_cleaner.py)
Deletes temporary files, cache, and trash across Windows, macOS, and Linux.

Cleans:
Temp folders (/tmp, %TEMP%, ~/Library/Caches)
Downloads folder (optional)
Browser caches
Trash/Recycle Bin

# Preview what will be deleted
python system_cleaner.py --dry-run
# Actually clean the system
python system_cleaner.py --execute

3. Bulk Renamer (bulk_renamer.py)
Rename multiple files with patterns.

Features:
Add prefix or suffix
Add numbering (001, 002, 003...)
Replace text in filenames

# Add prefix and numbering
python bulk_renamer.py ~/Photos --prefix "vacation_" --numbering --dry-run
# Replace text in filenames
python bulk_renamer.py ~/Documents --replace "old" "new"
# Add suffix
python bulk_renamer.py ~/Files --suffix "_backup"

4. Duplicate Finder (duplicate_finder.py)
Finds duplicate files by calculating MD5 hash of each file.

# Preview duplicates
python duplicate_finder.py ~/Documents --dry-run
# Delete duplicates (keeps one copy)
# Remove --dry-run to actually delete
python duplicate_finder.py ~/Documents

5. Folder Analyzer (folder_analyzer.py)
Shows which folders take the most space with visual progress bars.

# Analyze current directory
python folder_analyzer.py .
# Show top 15 largest folders
python folder_analyzer.py ~/Downloads --top 15
Output example:
📁 Analyzing: /home/user/Downloads
Total size: 45.2 GB

🔝 Top 10 largest folders:

 1. Videos
    ████████████████░░░░░░░░░░░░░░░░░░ 8.5 GB (18.8%)
    📍 /home/user/Downloads/Videos

 2. Software
    ██████████░░░░░░░░░░░░░░░░░░░░░░░░ 5.2 GB (11.5%)
    📍 /home/user/Downloads/Software

6. Extension Changer (extension_changer.py)
Bulk change file extensions and track recent files.

Change extensions:
# Preview extension changes
python extension_changer.py ext ~/Files .txt .md --dry-run
# Actually change extensions
python extension_changer.py ext ~/Files .jpeg .jpg
# Convert all .txt to .md
python extension_changer.py ext ~/Documents .txt .md
Track recent files:
# Files modified in last 7 days
python extension_changer.py recent ~/Documents
# Last 3 days, limit 20 files
python extension_changer.py recent ~/Downloads --days 3 --limit 20
# Sort by file size
python extension_changer.py recent ~/Documents --sort size
# Export to CSV
python extension_changer.py recent ~/Documents --export report.csv

7. Recent Files Tracker (recent_files_tracker.py)
Lists files modified in the last X days with detailed information.

# Files modified in last 7 days
python recent_files_tracker.py ~/Documents
# Last 3 days, limit 20 files
python recent_files_tracker.py ~/Downloads --days 3 --limit 20
# Sort by file size (largest first)
python recent_files_tracker.py ~/Documents --sort size
# Don't show file sizes
python recent_files_tracker.py ~/Documents --no-size
# Export to CSV
python recent_files_tracker.py ~/Documents --export recent_files.csv

🛡️ Safety Features
All scripts include a --dry-run mode that shows what will happen without making any changes. Always run with --dry-run first!

# Preview first
python file_organizer.py ~/Downloads --dry-run
# Then execute
python file_organizer.py ~/Downloads

💻 System Compatibility
Script	Windows	macOS	Linux
File Organizer	✅	✅	✅
System Cleaner	✅	✅	✅
Bulk Renamer	✅	✅	✅
Duplicate Finder	✅	✅	✅
Folder Analyzer	✅	✅	✅
Extension Changer	✅	✅	✅
Recent Files Tracker	✅	✅	✅

📄 License
MIT License — free to use, modify, and share.

👤 Author
Built by Prasad
