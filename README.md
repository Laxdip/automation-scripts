![Python](https://img.shields.io/badge/Python-3.7+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen)

# 🗂️ File Automation Scripts

A collection of powerful Python automation scripts to organize files, clean your system, rename in bulk, find duplicates, analyze storage, track recent files, watch for changes, backup data, and search your file system.

>  **Zero dependencies** — uses only the Python standard library.  
>  **Safe by default** — all destructive scripts preview changes first. Use `--execute` to apply.

---

##  Scripts Overview

| Script | What it does |
|--------|--------------|
| **file_organizer.py** | Sort files into folders by type or modification date |
| **system_cleaner.py** | Delete temp files, cache, and empty directories |
| **bulk_renamer.py** | Add prefix/suffix, numbering, text replace, regex rename |
| **duplicate_finder.py** | Find & remove duplicate files by content hash |
| **folder_analyzer.py** | Show which folders/files consume the most space |
| **extension_changer.py** | Bulk-change file extensions |
| **recent_files_tracker.py** | List files modified in the last N days |
| **file_watcher.py** | Monitor a folder for real-time changes |
| **file_backup.py**  | Incremental/versioned backup with restore support |
| **file_search.py**  | Search files by name, content, size, or date |

---

##  Installation

```bash
# Clone the repository
git clone https://github.com/laxdip/automation-scripts.git
cd automation-scripts

# No pip install needed — pure Python stdlib
```

---

##  Safety First

**All destructive scripts default to dry-run (preview) mode.**  
Nothing is moved, renamed, or deleted until you add `--execute`.

```bash
# Always preview first
python bulk_renamer.py ~/Photos --prefix "vacation_"

# Then apply
python bulk_renamer.py ~/Photos --prefix "vacation_" --execute
```

---

##  Script Details

### 1. File Organizer (`file_organizer.py`)
Automatically sorts files into subfolders based on extension or modification date.

**Supported categories:**
- Images → `.jpg` `.jpeg` `.png` `.gif` `.svg` `.webp` `.heic`
- Videos → `.mp4` `.mkv` `.avi` `.mov` `.webm`
- Documents → `.pdf` `.docx` `.txt` `.md` `.xlsx` `.pptx`
- Audio → `.mp3` `.wav` `.flac` `.aac`
- Archives → `.zip` `.rar` `.7z` `.tar` `.gz`
- Code → `.py` `.js` `.ts` `.html` `.css` `.java` `.go`
- Executables → `.exe` `.msi` `.sh` `.deb`
- Fonts → `.ttf` `.otf` `.woff`
- 3D Models → `.obj` `.stl` `.blend`
- Ebooks → `.epub` `.mobi`

```bash
# Preview (safe — no files moved)
python file_organizer.py ~/Downloads --dry-run

# Sort by file type
python file_organizer.py ~/Downloads --execute

# Sort by modification date (creates folders like 2024/2024-03/)
python file_organizer.py ~/Downloads --mode date --execute

# Sort into a different destination folder
python file_organizer.py ~/Downloads --dest ~/Sorted --execute

# Also move unrecognised files into "Other/"
python file_organizer.py ~/Downloads --include-unknown --execute
```

---

### 2. System Cleaner (`system_cleaner.py`)
Deletes temporary files, cache directories, and optionally empty folders across all platforms.

**Cleans:**
- Temp folders (`/tmp`, `%TEMP%`, `~/Library/Caches`)
- Browser caches (Chrome, Edge)
- Trash / Recycle Bin
- Custom folders by extension

```bash
# Preview what would be deleted
python system_cleaner.py --dry-run

# Clean everything
python system_cleaner.py --execute

# Clean only specific targets
python system_cleaner.py --targets tmp user_cache --execute

# Also remove empty directories
python system_cleaner.py --execute --remove-empty

# Clean a custom folder by extension
python system_cleaner.py --custom-path ~/logs --custom-ext .log .tmp --execute
```

---

### 3. Bulk Renamer (`bulk_renamer.py`)
Rename multiple files with flexible patterns — prefix, suffix, numbering, text replace, regex, and case conversion.

```bash
# Add prefix
python bulk_renamer.py ~/Photos --prefix "2024_" --execute

# Add numbering (001_file, 002_file …)
python bulk_renamer.py ~/Photos --numbering --execute

# Replace text in filenames
python bulk_renamer.py ~/Documents --replace "draft" "final" --execute

# Replace spaces with underscores
python bulk_renamer.py ~/Downloads --strip-spaces --execute

# Convert to lowercase
python bulk_renamer.py ~/Files --lowercase --execute

# Regex rename (remove all digits)
python bulk_renamer.py ~/Files --regex "\d+" --regex-replace "" --execute

# Only rename specific extensions
python bulk_renamer.py ~/Photos --prefix "photo_" --ext jpg png --execute
```

---

### 4. Duplicate Finder (`duplicate_finder.py`)
Finds duplicate files by comparing MD5 (or SHA256) content hashes. Keeps the first copy, acts on the rest.

```bash
# Preview duplicates
python duplicate_finder.py ~/Documents --dry-run

# Delete duplicates
python duplicate_finder.py ~/Documents --action delete --execute

# Move duplicates to a separate folder
python duplicate_finder.py ~/Documents --action move --move-to ~/Duplicates --execute

# Use SHA256, scan only images, export report
python duplicate_finder.py ~/Photos --algo sha256 --ext .jpg .png --export dupes.csv --execute
```

---

### 5. Folder Analyzer (`folder_analyzer.py`)
Shows which folders and files consume the most space, with visual progress bars and extension breakdown.

```bash
# Analyze current directory
python folder_analyzer.py .

# Show top 15 largest folders
python folder_analyzer.py ~/Downloads --top 15

# Also list the largest individual files
python folder_analyzer.py ~/Downloads --show-files

# Only show items larger than 50 MB
python folder_analyzer.py ~/Downloads --min-size 50
```

**Example output:**
```
 Total tracked size : 45.2 GB
════════════════════════════════════════

 Top 3 largest items:

   1.  Videos
      ████████████████░░░░░░░░  8.5 GB  (18.8%)
      /home/user/Downloads/Videos

   2.  Software
      ██████████░░░░░░░░░░░░░░  5.2 GB  (11.5%)
      /home/user/Downloads/Software
```

---

### 6. Extension Changer (`extension_changer.py`)
Bulk-change file extensions with collision detection and optional recursive mode.

```bash
# Preview .txt → .md
python extension_changer.py ~/Files .txt .md

# Apply
python extension_changer.py ~/Files .txt .md --execute

# Process subdirectories too
python extension_changer.py ~/Files .jpeg .jpg --recursive --execute
```

---

### 7. Recent Files Tracker (`recent_files_tracker.py`)
Lists files modified in the last N days with size, date, and optional CSV export.

```bash
# Files modified in last 7 days (default)
python recent_files_tracker.py ~/Documents

# Last 30 days, sorted by size
python recent_files_tracker.py ~/Downloads --days 30 --sort size

# Only Python files, export to CSV
python recent_files_tracker.py ~/Projects --ext .py --export recent.csv

# Files larger than 1 MB modified this week
python recent_files_tracker.py ~/Downloads --min-size 1048576

# Also show file creation time
python recent_files_tracker.py ~/Documents --show-created
```

---

### 8. File Watcher (`file_watcher.py`)
Monitor a directory in real-time for file creates, modifications, and deletions. Pure stdlib — no `watchdog` needed.

```bash
# Watch a folder for any changes
python file_watcher.py ~/Projects

# Watch every 2 seconds, log all events to CSV
python file_watcher.py ~/Projects --interval 2 --log changes.csv

# Only watch Python files for modifications
python file_watcher.py ~/Projects --ext .py --events modified

# Don't watch subdirectories, stop after 100 events
python file_watcher.py ~/Projects --no-recursive --max-events 100
```

---

### 9. File Backup (`file_backup.py`)
Incremental, versioned backup with MD5-based change detection. Supports zip compression and full restore.

```bash
# Incremental backup (only changed files)
python file_backup.py backup ~/Projects ~/Backup --execute

# Full versioned backup (timestamped folder e.g. Backup/20240401_120000/)
python file_backup.py backup ~/Projects ~/Backup --versioned --full --execute

# Compressed zip backup
python file_backup.py backup ~/Projects ~/Backup --compress --execute

# Back up only code files, skip node_modules
python file_backup.py backup ~/Projects ~/Backup --ext .py .js .ts --exclude-dirs node_modules .git --execute

# Restore from a versioned backup
python file_backup.py restore ~/Backup/20240401_120000 ~/Restored --execute
```

---

### 10. File Search (`file_search.py`)
Search files by name pattern, content text, size range, or modification date. Supports glob and regex.

```bash
# Find all Python files
python file_search.py ~/Projects --ext .py

# Find files matching a name pattern
python file_search.py ~/Documents --name "report*.pdf"

# Search inside file contents
python file_search.py ~/Projects --content "TODO" --ext .py .txt

# Find large files (> 100 MB)
python file_search.py ~/Downloads --min-size 104857600

# Find files modified in 2024
python file_search.py ~/Documents --after 2024-01-01 --before 2024-12-31

# Regex filename search, export results
python file_search.py ~/Logs --name "log_\d{4}" --regex --export results.csv
```

---

##  Compatibility

| Script | Windows | macOS | Linux |

---

## License

MIT License — free to use, modify, and share.

---

## Author

Prasad
