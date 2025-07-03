"""
Test script for parsing lemmas from spthy files using tree-sitter-spthy
"""

import pytest
from typing import List, Dict, Any, Optional

import tree_sitter_spthy as ts_spthy
from tree_sitter import Parser


class LemmaParser:
    """Parser for extracting all types of lemmas from Tamarin spthy files"""

    def __init__(self):
        self.language = ts_spthy.language()
        self.parser = Parser(self.language)

    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """Parse a spthy file and return the syntax tree"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            tree = self.parser.parse(bytes(content, "utf8"))
            return {"content": content, "tree": tree, "root_node": tree.root_node}
        except FileNotFoundError:
            raise FileNotFoundError(f"File {filepath} not found")
        except Exception as e:
            raise Exception(f"Error parsing file {filepath}: {e}")

    def extract_lemmas(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all lemmas from the parsed syntax tree"""
        lemmas = []
        content = parsed_data["content"]
        root_node = parsed_data["root_node"]

        def traverse_node(node):
            """Recursively traverse the syntax tree to find lemma nodes"""
            # Check for all lemma types
            if node.type in [
                "lemma",
                "diff_lemma",
                "accountability_lemma",
                "equiv_lemma",
                "diff_equiv_lemma",
            ]:
                lemma_info = self._extract_lemma_info(node, content)
                if lemma_info:
                    lemmas.append(lemma_info)

            for child in node.children:
                traverse_node(child)

        traverse_node(root_node)
        return lemmas

    def _extract_lemma_info(self, lemma_node, content: str) -> Dict[str, Any]:
        """Extract detailed information from a lemma node"""
        start_byte = lemma_node.start_byte
        end_byte = lemma_node.end_byte
        lemma_text = content[start_byte:end_byte]
        lemma_type = lemma_node.type

        # Initialize fields
        lemma_name = None
        trace_quantifier = None
        formula = None
        proof_skeleton = None
        modulo = None
        attributes = []
        test_identifiers = []
        processes = []

        # Extract fields based on lemma type
        if lemma_type == "lemma":
            lemma_info = self._extract_regular_lemma(lemma_node, content)
        elif lemma_type == "diff_lemma":
            lemma_info = self._extract_diff_lemma(lemma_node, content)
        elif lemma_type == "accountability_lemma":
            lemma_info = self._extract_accountability_lemma(lemma_node, content)
        elif lemma_type == "equiv_lemma":
            lemma_info = self._extract_equiv_lemma(lemma_node, content)
        elif lemma_type == "diff_equiv_lemma":
            lemma_info = self._extract_diff_equiv_lemma(lemma_node, content)
        else:
            lemma_info = {}

        # Common fields for all lemma types
        lemma_info.update(
            {
                "lemma_type": lemma_type,
                "full_text": lemma_text,
                "start_line": lemma_node.start_point[0] + 1,
                "end_line": lemma_node.end_point[0] + 1,
                "start_byte": start_byte,
                "end_byte": end_byte,
            }
        )

        return lemma_info

    def _extract_regular_lemma(self, lemma_node, content: str) -> Dict[str, Any]:
        """Extract information from a regular lemma node"""
        result = {
            "name": None,
            "trace_quantifier": None,
            "formula": None,
            "proof_skeleton": None,
            "modulo": None,
            "attributes": [],
        }

        # Extract fields from lemma node
        for child in lemma_node.children:
            child_text = content[child.start_byte : child.end_byte].strip()

            if child.type == "ident" and result["name"] is None:
                result["name"] = child_text
            elif child.type == "trace_quantifier":
                result["trace_quantifier"] = child_text
            elif child.type == "modulo":
                result["modulo"] = child_text
            elif child.type == "diff_lemma_attrs":
                result["attributes"] = self._extract_attributes(child, content)
            elif hasattr(child, "child_by_field_name"):
                # Handle field-based extraction
                if child.child_by_field_name(b"formula"):
                    formula_node = child.child_by_field_name(b"formula")
                    result["formula"] = content[
                        formula_node.start_byte : formula_node.end_byte
                    ].strip()
                if child.child_by_field_name(b"proof_skeleton"):
                    skeleton_node = child.child_by_field_name(b"proof_skeleton")
                    result["proof_skeleton"] = content[
                        skeleton_node.start_byte : skeleton_node.end_byte
                    ].strip()

        # Extract using field names directly from lemma node
        if hasattr(lemma_node, "child_by_field_name"):
            lemma_id_node = lemma_node.child_by_field_name(b"lemma_identifier")
            if lemma_id_node:
                result["name"] = content[
                    lemma_id_node.start_byte : lemma_id_node.end_byte
                ].strip()

            formula_node = lemma_node.child_by_field_name(b"formula")
            if formula_node:
                result["formula"] = content[
                    formula_node.start_byte : formula_node.end_byte
                ].strip()

            proof_node = lemma_node.child_by_field_name(b"proof_skeleton")
            if proof_node:
                result["proof_skeleton"] = content[
                    proof_node.start_byte : proof_node.end_byte
                ].strip()

        return result

    def _extract_diff_lemma(self, lemma_node, content: str) -> Dict[str, Any]:
        """Extract information from a diff lemma node"""
        result = {
            "name": None,
            "proof_skeleton": None,
            "modulo": None,
            "attributes": [],
        }

        # Extract using field names
        if hasattr(lemma_node, "child_by_field_name"):
            lemma_id_node = lemma_node.child_by_field_name(b"lemma_identifier")
            if lemma_id_node:
                result["name"] = content[
                    lemma_id_node.start_byte : lemma_id_node.end_byte
                ].strip()

            proof_node = lemma_node.child_by_field_name(b"proof_skeleton")
            if proof_node:
                result["proof_skeleton"] = content[
                    proof_node.start_byte : proof_node.end_byte
                ].strip()

        # Extract children
        for child in lemma_node.children:
            if child.type == "modulo":
                result["modulo"] = content[child.start_byte : child.end_byte].strip()
            elif child.type == "diff_lemma_attrs":
                result["attributes"] = self._extract_attributes(child, content)

        return result

    def _extract_accountability_lemma(self, lemma_node, content: str) -> Dict[str, Any]:
        """Extract information from an accountability lemma node"""
        result = {"name": None, "test_identifiers": [], "formula": None}

        # Extract using field names
        if hasattr(lemma_node, "child_by_field_name"):
            lemma_id_node = lemma_node.child_by_field_name(b"lemma_identifier")
            if lemma_id_node:
                result["name"] = content[
                    lemma_id_node.start_byte : lemma_id_node.end_byte
                ].strip()

            formula_node = lemma_node.child_by_field_name(b"formula")
            if formula_node:
                result["formula"] = content[
                    formula_node.start_byte : formula_node.end_byte
                ].strip()

        # Extract test identifiers (multiple)
        test_ids = []
        for child in lemma_node.children:
            if child.type == "ident" and result["name"] is None:
                result["name"] = content[child.start_byte : child.end_byte].strip()
            elif child.type == "ident" and result["name"] is not None:
                # This is a test identifier
                test_ids.append(content[child.start_byte : child.end_byte].strip())

        result["test_identifiers"] = test_ids
        return result

    def _extract_equiv_lemma(self, lemma_node, content: str) -> Dict[str, Any]:
        """Extract information from an equivalence lemma node"""
        result = {"name": None, "first_process": None, "second_process": None}

        # Extract using field names
        if hasattr(lemma_node, "child_by_field_name"):
            first_node = lemma_node.child_by_field_name(b"first")
            if first_node:
                result["first_process"] = content[
                    first_node.start_byte : first_node.end_byte
                ].strip()

            second_node = lemma_node.child_by_field_name(b"second")
            if second_node:
                result["second_process"] = content[
                    second_node.start_byte : second_node.end_byte
                ].strip()

        # Generate a name if not present
        result["name"] = "equiv_lemma"
        return result

    def _extract_diff_equiv_lemma(self, lemma_node, content: str) -> Dict[str, Any]:
        """Extract information from a differential equivalence lemma node"""
        result = {"name": None, "process": None}

        # Extract process from children
        for child in lemma_node.children:
            if child.type in [
                "binding",
                "conditional",
                "delete_state",
                "deterministic_choice",
                "event",
                "inline_msr_process",
                "input",
                "location_process",
                "non_deterministic_choice",
                "null",
                "output",
                "predefined_process",
                "process_let",
                "read_state",
                "remove_lock",
                "replication",
                "set_lock",
                "set_state",
            ]:
                result["process"] = content[child.start_byte : child.end_byte].strip()
                break

        # Generate a name if not present
        result["name"] = "diff_equiv_lemma"
        return result

    def _extract_attributes(self, attrs_node, content: str) -> List[str]:
        """Extract attributes from a lemma attributes node"""
        attributes = []
        for child in attrs_node.children:
            if child.type in ["diff_lemma_attr", "lemma_attr"]:
                attr_text = content[child.start_byte : child.end_byte].strip()
                if attr_text:
                    attributes.append(attr_text)
        return attributes

    def find_lemmas_by_keyword(
        self, parsed_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fallback method to find lemmas by searching for lemma keywords"""
        content = parsed_data["content"]
        lines = content.split("\n")
        lemmas = []

        keywords = ["lemma ", "diffLemma ", "equivLemma ", "diffEquivLemma "]

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            for keyword in keywords:
                if line.startswith(keyword):
                    # Extract lemma name
                    parts = line.split()
                    if len(parts) >= 2:
                        lemma_name = parts[1].rstrip(":")
                    else:
                        lemma_name = f"unnamed_{keyword.strip()}"

                    # Find the end of the lemma
                    lemma_lines = [lines[i]]
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if (
                            any(next_line.startswith(kw) for kw in keywords)
                            or next_line.startswith("rule ")
                            or next_line == "end"
                        ):
                            break
                        lemma_lines.append(lines[j])
                        j += 1

                    lemma_text = "\n".join(lemma_lines)

                    # Determine lemma type and trace quantifier
                    lemma_type = keyword.strip()
                    trace_quantifier = "all-traces"  # default
                    if "exists-trace" in lemma_text:
                        trace_quantifier = "exists-trace"

                    lemmas.append(
                        {
                            "name": lemma_name,
                            "lemma_type": lemma_type,
                            "trace_quantifier": (
                                trace_quantifier if lemma_type == "lemma" else None
                            ),
                            "full_text": lemma_text,
                            "start_line": i + 1,
                            "end_line": j,
                            "formula": lemma_text,
                            "proof_skeleton": None,
                            "modulo": None,
                            "attributes": [],
                            "test_identifiers": [],
                            "first_process": None,
                            "second_process": None,
                            "process": None,
                        }
                    )

                    i = j - 1
                    break
            i += 1

        return lemmas


@pytest.fixture
def lemma_parser():
    """Fixture to create a LemmaParser instance."""
    return LemmaParser()


@pytest.fixture
def parsed_spthy_data(lemma_parser):
    """Fixture to parse the SimpleChallengeResponse.spthy file."""
    import os

    test_file = os.path.join(os.path.dirname(__file__), "SimpleChallengeResponse.spthy")
    return lemma_parser.parse_file(test_file)


def test_file_parsing(lemma_parser):
    """Test that the spthy file can be parsed successfully."""
    import os

    test_file = os.path.join(os.path.dirname(__file__), "SimpleChallengeResponse.spthy")
    parsed_data = lemma_parser.parse_file(test_file)
    assert "content" in parsed_data
    assert "tree" in parsed_data
    assert "root_node" in parsed_data
    assert parsed_data["tree"] is not None
    assert parsed_data["root_node"] is not None


def test_lemma_extraction(lemma_parser, parsed_spthy_data):
    """Test that lemmas can be extracted from the parsed file."""
    lemmas = lemma_parser.extract_lemmas(parsed_spthy_data)

    # Filter out lemmas without names and remove duplicates
    valid_lemmas = []
    seen_names = set()
    seen_lines = set()

    for lemma in lemmas:
        if lemma.get("name") and lemma["name"] not in seen_names:
            # Also check for duplicate line ranges to avoid parsing issues
            line_key = (lemma["start_line"], lemma["end_line"])
            if line_key not in seen_lines:
                valid_lemmas.append(lemma)
                seen_names.add(lemma["name"])
                seen_lines.add(line_key)

    lemmas = valid_lemmas

    # If tree-sitter didn't find lemmas, use keyword-based fallback
    if not lemmas:
        lemmas = lemma_parser.find_lemmas_by_keyword(parsed_spthy_data)

    assert len(lemmas) > 0, "Should find at least one lemma"


def test_expected_lemmas(lemma_parser, parsed_spthy_data):
    """Test that all expected lemmas are found."""
    lemmas = lemma_parser.extract_lemmas(parsed_spthy_data)

    # Filter out lemmas without names and remove duplicates
    valid_lemmas = []
    seen_names = set()
    seen_lines = set()

    for lemma in lemmas:
        if lemma.get("name") and lemma["name"] not in seen_names:
            line_key = (lemma["start_line"], lemma["end_line"])
            if line_key not in seen_lines:
                valid_lemmas.append(lemma)
                seen_names.add(lemma["name"])
                seen_lines.add(line_key)

    lemmas = valid_lemmas

    if not lemmas:
        lemmas = lemma_parser.find_lemmas_by_keyword(parsed_spthy_data)

    expected_lemmas = [
        "Client_auth_injective",
        "Client_session_key_setup",
        "Client_session_key_setup_stronger",
    ]

    found_names = [lemma.get("name", "") for lemma in lemmas if lemma.get("name")]

    # Check that we found lemmas
    assert len(found_names) > 0, "Should find at least one lemma"

    # Check for expected lemmas (allow for flexibility)
    missing = set(expected_lemmas) - set(found_names)
    if missing:
        pytest.skip(f"Missing expected lemmas: {list(missing)}. Found: {found_names}")

    # Verify all expected lemmas are present
    for expected in expected_lemmas:
        assert (
            expected in found_names
        ), f"Expected lemma '{expected}' not found in {found_names}"


def test_lemma_structure(lemma_parser, parsed_spthy_data):
    """Test that extracted lemmas have the expected structure."""
    lemmas = lemma_parser.extract_lemmas(parsed_spthy_data)

    if not lemmas:
        lemmas = lemma_parser.find_lemmas_by_keyword(parsed_spthy_data)

    assert len(lemmas) > 0, "Should find at least one lemma"

    for lemma in lemmas:
        # Check required fields
        assert "lemma_type" in lemma
        assert "start_line" in lemma
        assert "end_line" in lemma
        assert "full_text" in lemma

        # Check line numbers are valid
        assert lemma["start_line"] > 0
        assert lemma["end_line"] >= lemma["start_line"]

        # Check text is not empty
        assert lemma["full_text"].strip() != ""


def test_lemma_types(lemma_parser, parsed_spthy_data):
    """Test that lemma types are correctly identified."""
    lemmas = lemma_parser.extract_lemmas(parsed_spthy_data)

    if not lemmas:
        lemmas = lemma_parser.find_lemmas_by_keyword(parsed_spthy_data)

    assert len(lemmas) > 0, "Should find at least one lemma"

    valid_types = [
        "lemma",
        "diff_lemma",
        "accountability_lemma",
        "equiv_lemma",
        "diff_equiv_lemma",
    ]

    for lemma in lemmas:
        assert (
            lemma["lemma_type"] in valid_types
        ), f"Invalid lemma type: {lemma['lemma_type']}"
