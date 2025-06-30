"""Tree-sitter parser for Spthy language."""

try:
    from tree_sitter_spthy import language
    def get_language():
        """Get the tree-sitter language for Spthy."""
        return language()
    __all__ = ['get_language', 'language']
except ImportError:
    # Fallback during build
    __all__ = []