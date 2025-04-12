# metasearch/plugins/image_search.py
"""
A stub for an image search plugin.
"""
from .search_plugin import SearchPlugin, register_search_plugin

class ImageSearchPlugin(SearchPlugin):
    def __init__(self):
        self._index = []
    def index_file(self, metadata):
        if metadata.get("file_type") == "image":
            self._index.append(metadata)
    def search(self, query_str):
        results = []
        query_lower = query_str.lower()
        for meta in self._index:
            ocr_text = meta.get("ocr_text", "").lower()
            if query_lower in ocr_text:
                results.append(meta)
        return results

image_search_plugin = ImageSearchPlugin()
register_search_plugin(image_search_plugin)
