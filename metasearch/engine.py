# metasearch/engine.py

import os
import datetime
from pathlib import Path
from .config import Config
from .scanner import scan_directory
from .extractors import get_extractor_for
from .storage import Storage
from .query_engine import QueryEngine

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
    
    def _trigger_index_for_new_dirs(self):
        """
        Normalize each directory in config.scan_paths and compare to indexed_dirs.
        If a directory is not indexed (status == 'completed'), index it.
        """
        indexed_dirs = self.storage.get_indexed_directories()
        for directory in self.config.scan_paths:
            norm_dir = str(Path(directory).resolve())
            if norm_dir not in indexed_dirs:
                print(f"New or incomplete directory detected: {norm_dir}. Indexing...")
                self.index_directory(norm_dir)
                self.storage.add_indexed_directory(norm_dir, status="completed")
    
    def index_directory(self, directory):
        for file_path in scan_directory(directory):
            self.process_file(file_path)
    
    def index_all_directories(self):
        for directory in self.config.scan_paths:
            norm_dir = str(Path(directory).resolve())
            self.index_directory(norm_dir)
            self.storage.add_indexed_directory(norm_dir, status="completed")
    
    def process_file(self, file_path):
        extractor = get_extractor_for(file_path)
        try:
            metadata = extractor(file_path)
            self.storage.save_metadata(metadata)
            print(f"Indexed: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def search(self, query_str):
        if self.config.lazy_indexing:
            if self._is_metadata_empty():
                print("Metadata store is empty. Triggering full indexing...")
                self.index_all_directories()
            else:
                self._trigger_index_for_new_dirs()
        result =[]
        for contain in self.query_engine.search(query_str) :
            result.append(contain["file_path"])

        return result
    
    def search_first_match(self, query_str):
        """
        Incrementally index files and stop when a match is found.
        For each file in every configured directory (if not yet fully indexed),
        index the file and then restrict the search to that file only.
        As soon as a match is found, return that file's metadata.
        """
        # Ensure directories are processed incrementally.
        if self.config.lazy_indexing:
            if self._is_metadata_empty():
                # If no files are indexed, process each directory one-by-one.
                for directory in self.config.scan_paths:
                    norm_dir = str(Path(directory).resolve())
                    for file_path in scan_directory(norm_dir):
                        try:
                            metadata = get_extractor_for(file_path)(file_path)
                            self.storage.save_metadata(metadata)
                            # Check if this file matches the query by restricting to its file_path.
                            test_query = f'file_name:"{os.path.basename(file_path)}" AND {query_str}'
                            res = self.storage.search_sql(test_query)
                            if res:
                                print(f"Early match found: {file_path}")
                                return res[0]
                        except Exception as e:
                            print(f"Error processing {file_path}: {e}")
                    self.storage.add_indexed_directory(norm_dir, status="completed")
            else:
                for directory in self.config.scan_paths:
                    norm_dir = str(Path(directory).resolve())
                    for file_path in scan_directory(norm_dir):
                        try:
                            metadata = get_extractor_for(file_path)(file_path)
                            self.storage.save_metadata(metadata)
                            test_query = f'file_name:"{os.path.basename(file_path)}" AND {query_str}'
                            res = self.storage.search_sql(test_query)
                            if res:
                                print(f"Early match found: {file_path}")
                                return res[0]
                        except Exception as e:
                            print(f"Error processing {file_path}: {e}")
                    self.storage.add_indexed_directory(norm_dir, status="completed")
        return None

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
        norm_dir = str(Path(directory).resolve())
        print(f"Updating index for directory: {norm_dir}")
        self.index_directory(norm_dir)
        self.storage.add_indexed_directory(norm_dir, status="completed")
    
    def remove_file(self, file_path):
        try:
            self.storage.remove_metadata(file_path)
            print(f"File removed from index: {file_path}")
        except Exception as e:
            print(f"Error removing file {file_path} from index: {e}")
    
    def shutdown(self):
        if self._watcher:
            self._watcher.stop()
