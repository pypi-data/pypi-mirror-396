"""MCP Toolbox - Unified interface to data adapters"""

class Toolbox:
    """Middleware layer providing unified interface to data stores"""
    
    def __init__(self):
        self.adapters = {}
    
    def register_adapter(self, name, adapter):
        """Register a data adapter"""
        self.adapters[name] = adapter
    
    def get_adapter(self, name):
        """Get a registered adapter"""
        return self.adapters.get(name)
