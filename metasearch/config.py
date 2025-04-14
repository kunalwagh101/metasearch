# metasearch/config.py

class Config:
    def __init__(self, storage_backend="sqlite", scan_paths=None, enable_watchdog=False, db_path="metasearch.db", lazy_indexing=True):
        """
        storage_backend: Only "sqlite" is supported here.
        scan_paths: List of directory paths to scan (e.g., ["H:\\exam", "H:\\trail", "C:\\abc", "M:\\value"]).
        enable_watchdog: If True, enables real‐time filesystem monitoring.
        db_path: Path for the SQLite database file.
        lazy_indexing: If True, triggers indexing for directories not yet indexed or marked as incomplete.
        """
        self.storage_backend = storage_backend
        self.scan_paths = scan_paths or []
        self.enable_watchdog = enable_watchdog
        self.db_path = db_path
        self.lazy_indexing = lazy_indexing
