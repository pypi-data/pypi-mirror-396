"""
Test enhanced mathlib4 metadata extraction.
"""
import pytest
from pathlib import Path
from warpdata.recipes.mathlib4 import (
    extract_docstring_metadata,
    extract_named_declarations,
    extract_namespace,
    count_attributes,
)


def test_extract_docstring_metadata_fermat():
    """Test docstring extraction on Fermat.lean."""
    fermat_file = Path("recipes_raw_data/mathlib4/Mathlib/NumberTheory/Fermat.lean")
    if not fermat_file.exists():
        pytest.skip("Fermat.lean not available")

    metadata = extract_docstring_metadata(fermat_file)

    # Should extract authors
    assert "authors" in metadata
    assert "Moritz Firsching" in metadata["authors"]

    # Should extract copyright year
    assert metadata["copyright_year"] == "2024"

    # Should find main theorems section
    assert metadata["has_main_theorems"] is True
    assert "coprime_fermatNumber_fermatNumber" in metadata["main_theorems_text"]
    assert "pepin_primality" in metadata["main_theorems_text"]

    # Should extract title
    assert "Fermat numbers" in metadata["title"]

    # No references in this file
    assert metadata["has_references"] is False


def test_extract_docstring_metadata_periodic_pts():
    """Test docstring extraction on PeriodicPts/Defs.lean."""
    periodic_file = Path("recipes_raw_data/mathlib4/Mathlib/Dynamics/PeriodicPts/Defs.lean")
    if not periodic_file.exists():
        pytest.skip("PeriodicPts/Defs.lean not available")

    metadata = extract_docstring_metadata(periodic_file)

    # Should extract multiple authors
    assert "Yury Kudryashov" in metadata["authors"]
    assert metadata["copyright_year"] == "2020"

    # Should have main statements section
    assert metadata["has_main_statements"] is True

    # Should have references
    assert metadata["has_references"] is True
    assert "wikipedia.org" in metadata["references_text"].lower()

    # Should have main definitions
    assert metadata["has_main_definitions"] is True
    assert "IsPeriodicPt" in metadata["main_definitions_text"]


def test_extract_named_declarations_fermat():
    """Test theorem/def extraction on Fermat.lean."""
    fermat_file = Path("recipes_raw_data/mathlib4/Mathlib/NumberTheory/Fermat.lean")
    if not fermat_file.exists():
        pytest.skip("Fermat.lean not available")

    decls = extract_named_declarations(fermat_file)

    # Should find the main definition
    assert "fermatNumber" in decls["definitions"]

    # Should find theorems
    assert "coprime_fermatNumber_fermatNumber" in decls["theorems"] or \
           "prod_fermatNumber" in decls["theorems"]

    # Should find lemmas
    assert "three_le_fermatNumber" in decls["lemmas"] or \
           "fermatNumber_mono" in decls["lemmas"]


def test_extract_namespace():
    """Test namespace extraction."""
    fermat_file = Path("recipes_raw_data/mathlib4/Mathlib/NumberTheory/Fermat.lean")
    if not fermat_file.exists():
        pytest.skip("Fermat.lean not available")

    namespace = extract_namespace(fermat_file)
    assert namespace == "Nat"


def test_count_attributes_group_basic():
    """Test attribute counting on Group/Basic.lean."""
    group_file = Path("recipes_raw_data/mathlib4/Mathlib/Algebra/Group/Basic.lean")
    if not group_file.exists():
        pytest.skip("Group/Basic.lean not available")

    attrs = count_attributes(group_file)

    # This file has many @[to_additive] attributes
    assert attrs["to_additive"] > 5

    # Should have @[simp] attributes
    assert attrs["simp"] > 0


def test_full_extraction_pipeline():
    """Test that all extractors work together."""
    fermat_file = Path("recipes_raw_data/mathlib4/Mathlib/NumberTheory/Fermat.lean")
    if not fermat_file.exists():
        pytest.skip("Fermat.lean not available")

    # All extractors should run without error
    metadata = extract_docstring_metadata(fermat_file)
    decls = extract_named_declarations(fermat_file)
    namespace = extract_namespace(fermat_file)
    attrs = count_attributes(fermat_file)

    assert metadata is not None
    assert decls is not None
    assert namespace is not None
    assert attrs is not None
