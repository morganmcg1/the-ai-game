#!/usr/bin/env python3
"""
Flatten frontend and backend folders into a single markdown file for LLM review.
Usage: python flatten_codebase.py [output_file]
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Configuration
INCLUDE_DIRS = ["frontend", "backend"]
EXCLUDE_DIRS = {"node_modules", ".git", "__pycache__", "dist", "build", ".venv", "venv", ".next", ".cache"}
EXCLUDE_FILES = {".DS_Store", "package-lock.json", "uv.lock", ".gitignore"}

# File extensions to include (code and config files)
INCLUDE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".css", ".scss", ".html",
    ".json", ".yaml", ".yml", ".toml", ".md", ".txt", ".env.example",
    ".sh", ".sql", ".graphql"
}

# Binary/large files to skip
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2",
    ".ttf", ".eot", ".mp3", ".mp4", ".webm", ".pdf", ".zip", ".tar",
    ".gz", ".lock", ".pyc", ".pyo"
}

def get_language_hint(ext: str) -> str:
    """Return markdown code fence language hint for syntax highlighting."""
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".css": "css",
        ".scss": "scss",
        ".html": "html",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".md": "markdown",
        ".sh": "bash",
        ".sql": "sql",
        ".graphql": "graphql",
    }
    return mapping.get(ext, "")

def should_include_file(filepath: Path) -> bool:
    """Check if file should be included in output."""
    if filepath.name in EXCLUDE_FILES:
        return False
    if filepath.suffix in SKIP_EXTENSIONS:
        return False
    if filepath.suffix in INCLUDE_EXTENSIONS:
        return True
    # Include files without extension that might be config (like Dockerfile)
    if not filepath.suffix and filepath.name in {"Dockerfile", "Makefile", "Procfile"}:
        return True
    return False

def should_include_dir(dirpath: Path) -> bool:
    """Check if directory should be traversed."""
    return dirpath.name not in EXCLUDE_DIRS

def get_file_tree(root: Path, prefix: str = "") -> list[str]:
    """Generate a tree structure for the directory."""
    lines = []
    entries = sorted(root.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))

    dirs = [e for e in entries if e.is_dir() and should_include_dir(e)]
    files = [e for e in entries if e.is_file() and should_include_file(e)]

    all_entries = dirs + files

    for i, entry in enumerate(all_entries):
        is_last = i == len(all_entries) - 1
        connector = "└── " if is_last else "├── "

        if entry.is_dir():
            lines.append(f"{prefix}{connector}{entry.name}/")
            extension = "    " if is_last else "│   "
            lines.extend(get_file_tree(entry, prefix + extension))
        else:
            size = entry.stat().st_size
            size_str = format_size(size)
            lines.append(f"{prefix}{connector}{entry.name} ({size_str})")

    return lines

def format_size(size: int) -> str:
    """Format file size in human readable form."""
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f}KB"
    else:
        return f"{size / (1024 * 1024):.1f}MB"

def count_lines(content: str) -> int:
    """Count lines in content."""
    return len(content.splitlines())

def collect_files(base_path: Path, include_dirs: list[str]) -> list[tuple[Path, str]]:
    """Collect all files to include with their relative paths."""
    files = []

    for dir_name in include_dirs:
        dir_path = base_path / dir_name
        if not dir_path.exists():
            continue

        for root, dirs, filenames in os.walk(dir_path):
            root_path = Path(root)

            # Filter directories in-place to prevent descending into excluded dirs
            dirs[:] = [d for d in dirs if should_include_dir(root_path / d)]

            for filename in filenames:
                filepath = root_path / filename
                if should_include_file(filepath):
                    rel_path = filepath.relative_to(base_path)
                    files.append((filepath, str(rel_path)))

    # Sort by path for consistent ordering
    files.sort(key=lambda x: x[1])
    return files

def flatten_codebase(base_path: Path, output_file: Path):
    """Main function to flatten codebase into markdown."""

    # Collect all files
    files = collect_files(base_path, INCLUDE_DIRS)

    # Calculate stats
    total_files = len(files)
    total_lines = 0
    total_size = 0

    output_lines = []

    # Header
    output_lines.append("# Codebase Flattened for LLM Review")
    output_lines.append("")
    output_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append(f"**Source:** {base_path}")
    output_lines.append(f"**Directories:** {', '.join(INCLUDE_DIRS)}")
    output_lines.append("")

    # Instructions for LLM
    output_lines.append("## Instructions for LLM")
    output_lines.append("")
    output_lines.append("This document contains the flattened source code of a codebase.")
    output_lines.append("Each file is separated by clear delimiters for easy parsing.")
    output_lines.append("")
    output_lines.append("**File delimiter format:**")
    output_lines.append("```")
    output_lines.append("===============================================================================")
    output_lines.append("FILE: <relative_path>")
    output_lines.append("SIZE: <file_size> | LINES: <line_count> | TYPE: <file_extension>")
    output_lines.append("===============================================================================")
    output_lines.append("```")
    output_lines.append("")
    output_lines.append("**End of file marker:** `<<< END OF FILE: <filename> >>>`")
    output_lines.append("")

    # File tree
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## File Tree Overview")
    output_lines.append("")
    output_lines.append("```")
    for dir_name in INCLUDE_DIRS:
        dir_path = base_path / dir_name
        if dir_path.exists():
            output_lines.append(f"{dir_name}/")
            output_lines.extend(get_file_tree(dir_path))
            output_lines.append("")
    output_lines.append("```")
    output_lines.append("")

    # Table of contents
    output_lines.append("## Table of Contents")
    output_lines.append("")
    for i, (filepath, rel_path) in enumerate(files, 1):
        output_lines.append(f"{i}. `{rel_path}`")
    output_lines.append("")

    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## Source Files")
    output_lines.append("")

    # Process each file
    for filepath, rel_path in files:
        try:
            content = filepath.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = f"[Binary or non-UTF-8 file - skipped]"
        except Exception as e:
            content = f"[Error reading file: {e}]"

        line_count = count_lines(content)
        file_size = filepath.stat().st_size
        total_lines += line_count
        total_size += file_size

        ext = filepath.suffix
        lang_hint = get_language_hint(ext)

        # File header with clear delimiters
        output_lines.append("=" * 79)
        output_lines.append(f"FILE: {rel_path}")
        output_lines.append(f"SIZE: {format_size(file_size)} | LINES: {line_count} | TYPE: {ext or 'no extension'}")
        output_lines.append("=" * 79)
        output_lines.append("")

        # File content in code block
        output_lines.append(f"```{lang_hint}")
        output_lines.append(content)
        output_lines.append("```")
        output_lines.append("")
        output_lines.append(f"<<< END OF FILE: {rel_path} >>>")
        output_lines.append("")
        output_lines.append("")

    # Summary at the end
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## Summary Statistics")
    output_lines.append("")
    output_lines.append(f"- **Total Files:** {total_files}")
    output_lines.append(f"- **Total Lines:** {total_lines:,}")
    output_lines.append(f"- **Total Size:** {format_size(total_size)}")
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("*End of flattened codebase*")

    # Write output
    output_content = "\n".join(output_lines)
    output_file.write_text(output_content, encoding='utf-8')

    print(f"Flattened codebase written to: {output_file}")
    print(f"  - Files: {total_files}")
    print(f"  - Lines: {total_lines:,}")
    print(f"  - Size: {format_size(total_size)}")
    print(f"  - Output size: {format_size(len(output_content.encode('utf-8')))}")

def main():
    base_path = Path(__file__).parent.resolve()

    if len(sys.argv) > 1:
        output_file = Path(sys.argv[1])
    else:
        output_file = base_path / "CODEBASE_FLATTENED.md"

    flatten_codebase(base_path, output_file)

if __name__ == "__main__":
    main()
