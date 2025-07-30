from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tree_sitter import Language

def get_language() -> "Language": ...
def language() -> "Language": ...

__all__ = ["get_language", "language"]
