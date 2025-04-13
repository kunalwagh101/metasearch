# metasearch/engine.py

import os
from .config import Config
from .scanner import scan_directory
from .extractors import get_extractor_for
from .storage import Storage
from .query_engine import QueryEngine
import datetime

try:
    from .watchers import Watcher
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

class Engine:
    def __init__(self, config: Config):
        self.config = config
        self.storage = Storage(config.db_path)
        self.query_engine = QueryEngine(self.storage)
        self._watcher = None
        if self.config.enable_watchdog and WATCHDOG_AVAILABLE:
            self._watcher = Watcher(self.config.scan_paths, self)
            self._watcher.start()

    def _is_metadata_empty(self):
        try:
            cur = self.storage.conn.execute("SELECT COUNT(*) FROM files")
            count = cur.fetchone()[0]
            return count == 0
        except Exception as e:
            print(f"Error checking metadata count: {e}")
            return True

    def index_directory(self, directory):
        for file_path in scan_directory(directory):
            self.process_file(file_path)

    def index_all_directories(self):
        for directory in self.config.scan_paths:
            self.index_directory(directory)

    def process_file(self, file_path):
        extractor = get_extractor_for(file_path)
        try:
            metadata = extractor(file_path)
            self.storage.save_metadata(metadata)
            print(f"Indexed: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def search(self, query_str):
        if self.config.lazy_indexing and self._is_metadata_empty():
            print("Metadata store is empty. Triggering lazy indexing...")
            self.index_all_directories()
        return self.query_engine.search(query_str)

    def get_metadata(self, file_path):
        extractor = get_extractor_for(file_path)
        return extractor(file_path)

    def annotate(self, file_path, metadata_dict):
        if not os.path.exists(file_path):
            metadata = {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "size_bytes": 0,
                "created": datetime.datetime.now().isoformat(),
                "modified": datetime.datetime.now().isoformat(),
                "extension": str(os.path.splitext(file_path)[1]).lower(),
                "full_text": ""
            }
        else:
            extractor = get_extractor_for(file_path)
            metadata = extractor(file_path)
        metadata.update(metadata_dict)
        self.storage.save_metadata(metadata)
        print(f"Annotated: {file_path}")

    def update_index(self, directory):
        print(f"Updating index for directory: {directory}")
        self.index_directory(directory)

    def remove_file(self, file_path):
        try:
            self.storage.remove_metadata(file_path)
            print(f"File removed from index: {file_path}")
        except Exception as e:
            print(f"Error removing file {file_path} from index: {e}")

    def shutdown(self):
        if self._watcher:
            self._watcher.stop()
