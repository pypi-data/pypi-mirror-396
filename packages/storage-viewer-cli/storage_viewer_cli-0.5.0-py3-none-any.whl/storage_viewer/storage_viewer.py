# src/storage_viewer/storage_viewer.py
import os
import sys
import argparse
from pathlib import Path
import fnmatch

__version__ = "0.5.0"

class DirectoryTree:
    def __init__(self):
        self.stats = {
            'directories': 0,
            'files': 0,
            'total_size': 0,
            'skipped_items': 0
        }
    
    def should_include_item(self, item_path, item_name, options):
        """Determine if an item should be included based on filters"""
        # Skip hidden files unless explicitly shown
        if not getattr(options, 'show_hidden', False) and item_name.startswith('.'):
            return False
        
        # Check if it's a directory
        is_directory = os.path.isdir(item_path)
        
        # Skip files if --no-file is specified
        if not is_directory and getattr(options, 'no_file', False):
            self.stats['skipped_items'] += 1
            return False
        
        # Skip folders if --no-folder is specified
        if is_directory and getattr(options, 'no_folder', False):
            self.stats['skipped_items'] += 1
            return False
        
        # Check folder name exclusion
        if is_directory and getattr(options, 'exclude_folders', []):
            for folder_pattern in options.exclude_folders:
                if fnmatch.fnmatch(item_name.lower(), folder_pattern.lower()):
                    self.stats['skipped_items'] += 1
                    return False
        
        # Check file extension exclusion
        if not is_directory and getattr(options, 'exclude_extensions', []):
            file_ext = Path(item_name).suffix.lower()
            if file_ext and file_ext[1:] in [ext.lower() for ext in options.exclude_extensions]:
                self.stats['skipped_items'] += 1
                return False
        
        # Check file pattern exclusion
        if not is_directory and getattr(options, 'exclude_files', []):
            for file_pattern in options.exclude_files:
                if fnmatch.fnmatch(item_name.lower(), file_pattern.lower()):
                    self.stats['skipped_items'] += 1
                    return False
        
        # Check include patterns
        if getattr(options, 'include_patterns', []):
            matched = False
            for pattern in options.include_patterns:
                if fnmatch.fnmatch(item_name.lower(), pattern.lower()):
                    matched = True
                    break
            if not matched:
                self.stats['skipped_items'] += 1
                return False
        
        # Check max depth
        if getattr(options, 'max_depth', None) and self.current_depth >= options.max_depth:
            return False
        
        # Check size filters
        if not is_directory and getattr(options, 'min_size', None):
            try:
                file_size = os.path.getsize(item_path)
                if file_size < options.min_size:
                    self.stats['skipped_items'] += 1
                    return False
            except (OSError, PermissionError):
                return False
        
        if not is_directory and getattr(options, 'max_size', None):
            try:
                file_size = os.path.getsize(item_path)
                if file_size > options.max_size:
                    self.stats['skipped_items'] += 1
                    return False
            except (OSError, PermissionError):
                return False
        
        return True
    
    def get_file_icon(self, item_name, is_directory):
        """Get appropriate icon for the item"""
        if is_directory:
            return "📁 "
        
        file_ext = Path(item_name).suffix.lower()
        icons = {
            '.py': '🐍 ', '.js': '📜 ', '.html': '🌐 ', '.css': '🎨 ',
            '.json': '📋 ', '.xml': '📄 ', '.txt': '📝 ', '.md': '📖 ',
            '.pdf': '📕 ', '.doc': '📘 ', '.docx': '📘 ',
            '.jpg': '🖼 ', '.jpeg': '🖼 ', '.png': '🖼 ', '.gif': '🖼 ',
            '.mp3': '🎵 ', '.mp4': '🎬 ', '.avi': '🎬 ', '.mkv': '🎬 ',
            '.zip': '📦 ', '.tar': '📦 ', '.gz': '📦 ', '.rar': '📦 ',
            '.exe': '⚙️ ', '.app': '⚙️ ', '.deb': '⚙️ ', '.rpm': '⚙️ ',
        }
        return icons.get(file_ext, '📄 ')
    
    def print_tree(self, start_path, prefix="", is_last=True, options=None, current_depth=0):
        """Recursively print the directory tree structure"""
        self.current_depth = current_depth
        
        item_name = os.path.basename(start_path)
        is_directory = os.path.isdir(start_path)
        
        # Get icon and format item name
        icon = self.get_file_icon(item_name, is_directory) if getattr(options, 'icons', False) else ""
        size_info = ""
        
        if getattr(options, 'show_size', False) and not is_directory:
            try:
                file_size = os.path.getsize(start_path)
                size_info = f" [{self.format_size(file_size)}]"
            except (OSError, PermissionError):
                size_info = " [N/A]"
        
        # Print the current item
        connector = "└── " if is_last else "├── "
        print(prefix + connector + icon + item_name + size_info)
        
        # Update statistics
        if is_directory:
            self.stats['directories'] += 1
        else:
            self.stats['files'] += 1
            try:
                self.stats['total_size'] += os.path.getsize(start_path)
            except (OSError, PermissionError):
                pass
        
        # Process directory contents
        if is_directory and (not getattr(options, 'max_depth', None) or current_depth < getattr(options, 'max_depth', 0)):
            try:
                items = []
                for item in os.listdir(start_path):
                    item_path = os.path.join(start_path, item)
                    if self.should_include_item(item_path, item, options):
                        items.append((item, item_path))
                
                # Sort based on options
                sort_by = getattr(options, 'sort_by', 'name')
                if sort_by == 'name':
                    items.sort(key=lambda x: x[0].lower())
                elif sort_by == 'size':
                    items.sort(key=lambda x: os.path.getsize(x[1]) if os.path.isfile(x[1]) else 0)
                elif sort_by == 'type':
                    items.sort(key=lambda x: (not os.path.isdir(x[1]), Path(x[0]).suffix.lower(), x[0].lower()))
                else:  # default: directories first
                    items.sort(key=lambda x: (not os.path.isdir(x[1]), x[0].lower()))
                
                # Reverse if requested
                if getattr(options, 'reverse_sort', False):
                    items.reverse()
                
                # Calculate new prefix
                new_prefix = prefix + ("    " if is_last else "│   ")
                
                # Process each item
                for i, (item_name, item_path) in enumerate(items):
                    is_last_item = (i == len(items) - 1)
                    self.print_tree(item_path, new_prefix, is_last_item, options, current_depth + 1)
                    
            except PermissionError:
                print(prefix + "    └── 🔒 [Permission Denied]")
            except Exception as e:
                print(prefix + f"    └── ❌ [Error: {str(e)}]")
    
    def export_tree(self, start_path, output_file, options):
        """Export tree to a file"""
        original_stdout = sys.stdout
        with open(output_file, 'w', encoding='utf-8') as f:
            sys.stdout = f
            self.print_detailed_tree(start_path, options)
            sys.stdout = original_stdout
        print(f"Tree exported to: {output_file}")
    
    def print_detailed_tree(self, start_path, options):
        """Print detailed directory tree with header information"""
        print(f"Directory Tree: {start_path}")
        print("=" * 60)
        
        if getattr(options, 'show_size', False):
            total_size = self.get_directory_size(start_path)
            print(f"Total Size: {self.format_size(total_size)}")
        
        print(f"Filters: {self.get_filters_summary(options)}")
        print()
        
        self.print_tree(start_path, options=options)
        
        print()
        print("=" * 60)
        self.print_statistics()
    
    def get_filters_summary(self, options):
        """Get a summary of applied filters"""
        filters = []
        if getattr(options, 'no_file', False):
            filters.append("No Files")
        if getattr(options, 'no_folder', False):
            filters.append("No Folders")
        if getattr(options, 'exclude_folders', []):
            filters.append(f"Exclude folders: {', '.join(options.exclude_folders)}")
        if getattr(options, 'exclude_extensions', []):
            filters.append(f"Exclude extensions: {', '.join(options.exclude_extensions)}")
        if getattr(options, 'exclude_files', []):
            filters.append(f"Exclude files: {', '.join(options.exclude_files)}")
        if getattr(options, 'include_patterns', []):
            filters.append(f"Include patterns: {', '.join(options.include_patterns)}")
        if getattr(options, 'max_depth', None):
            filters.append(f"Max depth: {options.max_depth}")
        if getattr(options, 'min_size', None):
            filters.append(f"Min size: {self.format_size(options.min_size)}")
        if getattr(options, 'max_size', None):
            filters.append(f"Max size: {self.format_size(options.max_size)}")
        
        return "; ".join(filters) if filters else "None"
    
    def print_statistics(self):
        """Print summary statistics"""
        print("Statistics:")
        print(f"  📁 Directories: {self.stats['directories']}")
        print(f"  📄 Files: {self.stats['files']}")
        print(f"  💾 Total Size: {self.format_size(self.stats['total_size'])}")
        print(f"  🚫 Skipped Items: {self.stats['skipped_items']}")
    
    def get_directory_size(self, path):
        """Calculate total directory size"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
        return total_size
    
    def format_size(self, size_bytes):
        """Convert bytes to human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.2f} {size_names[i]}"

def parse_size(size_str):
    """Parse size string like '10M', '1G', '500K' to bytes"""
    if not size_str:
        return None
        
    size_str = size_str.upper().strip()
    multipliers = {'B': 1, 'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
    
    if size_str[-1] in multipliers:
        number = float(size_str[:-1])
        multiplier = multipliers[size_str[-1]]
        return int(number * multiplier)
    else:
        return int(size_str)

def main():
    parser = argparse.ArgumentParser(
        description="Display directory tree structure with advanced filtering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  stree /path/to/directory
  stree /path --no-file
  stree /path --no-folder
  stree /path --exclude-extensions py,txt,log
  stree /path --exclude-folders node_modules,__pycache__
  stree /path --exclude-files "*.tmp,*.bak"
  stree /path --include-patterns "*.py,*.js"
  stree /path --max-depth 3
  stree /path --min-size 1M --max-size 10M
  stree /path --sort-by size --reverse-sort
  stree /path --show-hidden --show-size
  stree /path --icons
  stree /path --export tree.txt
        """
    )
    
    # Basic options
    parser.add_argument("path", help="Path to the directory to analyze")
    parser.add_argument("--show-hidden", action="store_true", help="Show hidden files and folders")
    
    # Exclusion filters
    parser.add_argument("--no-file", action="store_true", help="Exclude all files")
    parser.add_argument("--no-folder", action="store_true", help="Exclude all folders")
    parser.add_argument("--exclude-extensions", help="Comma-separated file extensions to exclude (e.g., py,txt,log)")
    parser.add_argument("--exclude-folders", help="Comma-separated folder names to exclude (e.g., node_modules,__pycache__)")
    parser.add_argument("--exclude-files", help="Comma-separated file patterns to exclude (e.g., *.tmp,*.bak)")
    
    # Inclusion filters
    parser.add_argument("--include-patterns", help="Comma-separated patterns to include (e.g., *.py,*.js)")
    
    # Size and depth filters
    parser.add_argument("--max-depth", type=int, help="Maximum depth to traverse")
    parser.add_argument("--min-size", help="Minimum file size (e.g., 1M, 100K, 1G)")
    parser.add_argument("--max-size", help="Maximum file size (e.g., 1M, 100K, 1G)")
    
    # Display options
    parser.add_argument("--show-size", action="store_true", help="Show file sizes")
    parser.add_argument("--icons", action="store_true", help="Show file type icons")
    parser.add_argument("--sort-by", choices=['name', 'size', 'type'], default='name', help="Sort method")
    parser.add_argument("--reverse-sort", action="store_true", help="Reverse sort order")
    parser.add_argument("--export", help="Export tree to specified file")
    
    # Version
    parser.add_argument("--version", action="version", version=f"storage-viewer {__version__}")
    
    args = parser.parse_args()
    
    # Validate path
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist")
        sys.exit(1)
    
    # Parse comma-separated lists
    if args.exclude_extensions:
        args.exclude_extensions = [ext.strip() for ext in args.exclude_extensions.split(',')]
    else:
        args.exclude_extensions = []
    
    if args.exclude_folders:
        args.exclude_folders = [folder.strip() for folder in args.exclude_folders.split(',')]
    else:
        args.exclude_folders = []
    
    if args.exclude_files:
        args.exclude_files = [pattern.strip() for pattern in args.exclude_files.split(',')]
    else:
        args.exclude_files = []
    
    if args.include_patterns:
        args.include_patterns = [pattern.strip() for pattern in args.include_patterns.split(',')]
    else:
        args.include_patterns = []
    
    # Parse size filters
    if args.min_size:
        args.min_size = parse_size(args.min_size)
    if args.max_size:
        args.max_size = parse_size(args.max_size)
    
    # Convert to absolute path
    abs_path = os.path.abspath(args.path)
    
    try:
        tree = DirectoryTree()
        
        if args.export:
            tree.export_tree(abs_path, args.export, args)
        else:
            tree.print_detailed_tree(abs_path, args)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
