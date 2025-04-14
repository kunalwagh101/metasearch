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
        Compares each directory in config.scan_paths (normalized) with those in the indexed_dirs table.
        Indexes any directory that is not already marked as 'completed'.
        """
       
        normalized_paths = {str(Path(directory).resolve()) for directory in self.config.scan_paths} 
        indexed_dirs = self.storage.get_indexed_directories()
        
        for norm_dir in normalized_paths:
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
        """
        First, check the database for results matching the query.
        If results exist, return them immediately.
        Otherwise, trigger indexing for new/incomplete directories and then re-run the query.
        """
        results = self.query_engine.search(query_str)
        if results and len(results) > 0:
            ans  = []
            for contain in results :
                ans.append(contain['file_path'])
            return ans
        
        self._trigger_index_for_new_dirs()
        finally_results = []
        for contain in  self.query_engine.search(query_str) :
                finally_results.append(contain['file_path'])
        return finally_results
    
    def search_first_match(self, query_str):
        """
        First checks the database for a matching file.
        If none are found, it then triggers incremental indexing of directories,
        and after each file is processed, it tests if that file matches the query.
        As soon as a match is found, it returns that file's metadata.
        """
        results = self.query_engine.search(query_str)
        if results and len(results) > 0:
            return results[0]['file_path']
        
        
        for directory in self.config.scan_paths:
            norm_dir = str(Path(directory).resolve())
            for file_path in scan_directory(norm_dir):
                try:
                    metadata = get_extractor_for(file_path)(file_path)
                    self.storage.save_metadata(metadata)
                   
                    test_query = f'file_name:"{os.path.basename(file_path)}" AND {query_str}'
                    res = self.storage.search_sql(test_query)
                    if res and len(res) > 0:
                        print(f"Early match found: {file_path}")
                        return res[0]['file_path']
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
           
            self.storage.add_indexed_directory(norm_dir, status="completed")
        return None

    def get_metadata(self, file_path):
        """
        Returns the metadata stored in the database for the given file_path.
        """
        return self.storage.get_metadata(os.path.abspath(file_path))
    
    def annotate(self, file_path, metadata_dict):
        """
        Annotate a file with user-supplied metadata.
        1. If the file exists, extract its metadata (or retrieve from DB) and update it.
        2. If the file does not exist, create it, generate minimal metadata, and then update.
        After updating, ensure custom annotations are appended to the "full_text" field.
        """
        import datetime
        from pathlib import Path

        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            parent_dir = os.path.dirname(file_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            Path(file_path).touch()
            print(f"File did not exist; created empty file at: {file_path}")
        
    
        existing_metadata = self.storage.get_metadata(file_path)
        if existing_metadata is None:
            try:
                extractor = get_extractor_for(file_path)
                metadata = extractor(file_path)
            except Exception as e:
                print(f"Metadata extraction failed; using fallback. Reason: {e}")
                now = datetime.datetime.now().isoformat()
                metadata = {
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "size_bytes": os.path.getsize(file_path),
                    "created": now,
                    "modified": now,
                    "access_time": now,
                    "owner_uid": 0,
                    "group_gid": 0,
                    "permissions": oct(os.stat(file_path).st_mode),
                    "file_type": "text",
                    "full_text": ""
                }
        else:
            metadata = existing_metadata

        metadata.update(metadata_dict)
        current_text = metadata.get("full_text", "")
        for key, value in metadata_dict.items():
            pair = f"{key}:{value}"
          
            if pair.lower() not in current_text.lower():
                if current_text:
                    current_text += " " + pair
                else:
                    current_text = pair
        metadata["full_text"] = current_text.strip()

       
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
