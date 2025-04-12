# metasearch/config.py

class Config:
    def __init__(self, storage_backend="sqlite", scan_paths=None, enable_watchdog=False, db_path="metasearch.db", lazy_indexing=True):
        """
        storage_backend: Currently only "sqlite" is supported.
        scan_paths: A list of directories to scan recursively.
        enable_watchdog: If True, enable file system monitoring.
        db_path: Path to the SQLite database file.
        lazy_indexing: When True, automatically trigger full indexing if no metadata is found.
        """
        self.storage_backend = storage_backend
        self.scan_paths = scan_paths or []
        self.enable_watchdog = enable_watchdog
        self.db_path = db_path
        self.lazy_indexing = lazy_indexing
