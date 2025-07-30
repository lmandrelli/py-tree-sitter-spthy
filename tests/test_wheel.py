"""
Pytest tests for py-tree-sitter-spthy wheel functionality.
Tests basic import and functionality for cibuildwheel testing.
"""

import pytest


def test_import_py_tree_sitter_spthy():
    """Test that py_tree_sitter_spthy can be imported successfully."""
    import py_tree_sitter_spthy
    assert py_tree_sitter_spthy is not None


def test_get_language():
    """Test that we can get the language from py_tree_sitter_spthy."""
    import py_tree_sitter_spthy
    from tree_sitter import Language

    language = py_tree_sitter_spthy.get_language()
    assert language is not None
    assert isinstance(language, Language)


def test_tree_sitter_spthy_direct_import():
    """Test that tree_sitter_spthy module is available and functional."""
    import tree_sitter_spthy
    from tree_sitter import Language

    lang_direct = tree_sitter_spthy.language()
    assert lang_direct is not None
    assert isinstance(lang_direct, Language)


def test_language_consistency():
    """Test that both ways of getting the language return the same type."""
    import py_tree_sitter_spthy
    import tree_sitter_spthy

    lang1 = py_tree_sitter_spthy.get_language()
    lang2 = tree_sitter_spthy.language()

    assert type(lang1) == type(lang2)
    # Both should be Language instances
    assert str(type(lang1)) == "<class 'tree_sitter.Language'>"
