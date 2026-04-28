# Automation Scripts

Python automation tools for file organization, cleanup, renaming, deduplication, backup etc etc...

**Zero dependencies** · **Safe by default**

## Safety First

All destructive scripts preview changes first. Nothing is moved, renamed, or deleted until you add `--execute`.

```bash
# Preview what will happen (safe)
python script_name.py /path --dry-run

# Apply the changes
python script_name.py /path --execute

# Show help
python script_name.py -h
```
## Usage Pattern
#### Every script follows this pattern:

1.Preview mode (default or --dry-run) - See what would happen

2.Execute mode (--execute) - Actually perform the action

## Quick Start
```
git clone https://github.com/laxdip/automation-scripts.git
cd automation-scripts

# Always preview first
python any_script.py ~/Downloads --dry-run

# Then apply when ready
python any_script.py ~/Downloads --execute

# See all options
python any_script.py -h
```
> Remember: --dry-run to preview, --execute to apply

## License
MIT
## 
Prasad
