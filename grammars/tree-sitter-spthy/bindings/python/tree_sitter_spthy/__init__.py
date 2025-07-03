"Spthy grammar for tree-sitter"

from tree_sitter import Language
from ._binding import language as _language

def language():
    """Get the tree-sitter language for Spthy."""
    return Language(_language())

__all__ = ["language"]
