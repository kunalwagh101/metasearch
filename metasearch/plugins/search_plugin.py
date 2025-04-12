# metasearch/plugins/search_plugin.py
"""
Abstract search plugin interface.
"""
_SEARCH_PLUGIN_REGISTRY = []

def register_search_plugin(plugin):
    _SEARCH_PLUGIN_REGISTRY.append(plugin)

def get_search_plugins():
    return _SEARCH_PLUGIN_REGISTRY

def run_search_plugins(query_str):
    results = []
    for plugin in _SEARCH_PLUGIN_REGISTRY:
        try:
            plugin_results = plugin.search(query_str)
            if plugin_results:
                results.extend(plugin_results)
        except Exception as e:
            print(f"Plugin {plugin.__class__.__name__} error: {e}")
    return results

class SearchPlugin:
    def search(self, query_str):
        raise NotImplementedError("search() must be implemented by the plugin.")
