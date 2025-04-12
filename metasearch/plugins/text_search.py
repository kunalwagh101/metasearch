# metasearch/plugins/text_search.py
"""
A sample text search plugin.
"""
from .search_plugin import SearchPlugin, register_search_plugin

class TextSearchPlugin(SearchPlugin):
    def __init__(self):
        self._index = []
    def index_file(self, metadata):
        self._index.append(metadata)
    def search(self, query_str):
        results = []
        query_lower = query_str.lower()
        for meta in self._index:
            text = meta.get("full_text", "").lower()
            if query_lower in text:
                results.append(meta)
        return results

text_search_plugin = TextSearchPlugin()
register_search_plugin(text_search_plugin)

def add_file_to_text_index(metadata):
    text_search_plugin.index_file(metadata)
