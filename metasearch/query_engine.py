# metasearch/query_engine.py

from .storage import Storage

class QueryEngine:
    def __init__(self, storage: Storage):
        self.storage = storage

    def search(self, query_str):
        return self.storage.search(query_str)
