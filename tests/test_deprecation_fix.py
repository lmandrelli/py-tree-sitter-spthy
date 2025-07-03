"""
Test script to verify that the tree-sitter deprecation warning is fixed
"""

import warnings
import pytest

import tree_sitter_spthy as ts_spthy
from tree_sitter import Language, Parser


def test_no_deprecation_warning():
    """Test that using ts_spthy.language() doesn't generate deprecation warnings"""
    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # This should NOT generate a deprecation warning anymore
        language = ts_spthy.language()
        parser = Parser(language)

        # Simple test parsing
        test_code = "rule test: [In(x)] --[Test(x)]--> [Out(x)]"
        tree = parser.parse(bytes(test_code, "utf8"))

        # Verify basic functionality
        assert isinstance(language, Language)
        assert isinstance(parser, Parser)
        assert tree is not None

        # Check for deprecation warnings
        deprecation_warnings = [
            warning
            for warning in w
            if issubclass(warning.category, DeprecationWarning)
            and "int argument support is deprecated" in str(warning.message)
        ]

        assert (
            len(deprecation_warnings) == 0
        ), f"Found {len(deprecation_warnings)} deprecation warning(s): {[str(w.message) for w in deprecation_warnings]}"


def test_api_compatibility():
    """Test that the new API returns the expected Language object"""
    # Get language object
    lang = ts_spthy.language()

    # Verify it's a Language instance
    assert isinstance(lang, Language), f"Expected Language object, got {type(lang)}"


def test_language_object_type():
    """Test that ts_spthy.language() returns the correct type"""
    language = ts_spthy.language()
    assert type(language).__name__ == "Language"
    assert hasattr(language, "query")  # Language objects should have a query method


def test_parser_creation():
    """Test that Parser can be created with the language object"""
    language = ts_spthy.language()
    parser = Parser(language)

    assert isinstance(parser, Parser)
    assert parser.language == language


def test_basic_parsing():
    """Test that basic parsing works without errors"""
    language = ts_spthy.language()
    parser = Parser(language)

    # Test with a simple spthy rule
    test_code = "rule test: [In(x)] --[Test(x)]--> [Out(x)]"
    tree = parser.parse(bytes(test_code, "utf8"))

    assert tree is not None
    assert tree.root_node is not None
    assert hasattr(tree.root_node, "type")
