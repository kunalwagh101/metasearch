# metasearch/scanner.py
from pathlib import Path

def scan_directory(directory):
    """
    Recursively scans a directory and yields full file paths.
    """
    directory = Path(directory)
    for filepath in directory.rglob("*"):
        if filepath.is_file():
            yield str(filepath.resolve())
