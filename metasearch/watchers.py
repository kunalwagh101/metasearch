# metasearch/watchers.py

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .scanner import scan_directory
from .engine import Engine

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def on_created(self, event):
        if not event.is_directory:
            self.engine.process_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.engine.process_file(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.engine.remove_file(event.src_path)

class Watcher:
    def __init__(self, paths, engine: Engine):
        self.paths = paths
        self.engine = engine
        self.observer = Observer()

    def start(self):
        handler = FileChangeHandler(self.engine)
        for path in self.paths:
            self.observer.schedule(handler, path, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
