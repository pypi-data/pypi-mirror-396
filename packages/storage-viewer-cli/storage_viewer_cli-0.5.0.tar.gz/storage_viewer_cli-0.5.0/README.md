~/storage-viewer-cli $ cat > README.md << 'EOF'
# Storage Viewer CLI

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PyPI](https://img.shields.io/badge/pypi-v0.1.0-orange)

A powerful, feature-rich directory tree visualizer with advanced filtering options for the command line.

## ✨ Features

- 📁 **Hierarchical Tree Display** - Clean, readable directory structures
- 🔍 **Advanced Filtering** - Filter by extension, folder, pattern, and size
- 📊 **Size Analysis** - Show file sizes with human-readable formats
- 🎨 **File Type Icons** - Visual indicators for different file types
- 📏 **Depth Control** - Limit directory traversal depth
- 📤 **Export Capability** - Save tree structure to files
- 📈 **Statistics** - Detailed summary of directories and files
- ⚡ **Fast & Lightweight** - No external dependencies


## BASIC USAGE
# View directory tree
stree /path/to/directory

# With file type icons
stree . --icons

# Show file sizes
stree . --show-size

# Limit depth
stree . --max-depth 3


## ADVANCED EXAMPLE
# Project analysis (exclude development folders)
stree . --exclude-folders __pycache__,node_modules,.git,venv --max-depth 4

# Find large files
stree /home --min-size 100M --show-size --sort-by size --reverse-sort

# Export to file
stree /path --export directory_structure.txt

# Only code files
stree . --include-patterns "*.py,*.js,*.java,*.cpp"

# Clean view (no temp files)
stree . --exclude-extensions tmp,bak,log --exclude-files "*.tmp,*.bak"


## OPTIONS
Usage: stree [OPTIONS] PATH

Display directory tree structure with advanced filtering

Options:
  --show-hidden           Show hidden files and folders
  --no-file              Exclude all files
  --no-folder            Exclude all folders
  --exclude-extensions   Comma-separated file extensions to exclude
  --exclude-folders      Comma-separated folder names to exclude
  --exclude-files        Comma-separated file patterns to exclude
  --include-patterns     Comma-separated patterns to include
  --max-depth            Maximum depth to traverse
  --min-size             Minimum file size (e.g., 1M, 100K, 1G)
  --max-size             Maximum file size (e.g., 1M, 100K, 1G)
  --show-size            Show file sizes
  --icons                Show file type icons
  --sort-by              Sort method: name, size, or type
  --reverse-sort         Reverse sort order
  --export               Export tree to specified file
  --version              Show version
  --help                 Show help message
