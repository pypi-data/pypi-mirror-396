"""
Test Lean 4 AST extraction to JSON format.

TDD approach: Write tests first, then implement extractors.
"""
import pytest
from pathlib import Path
import json

from warpdata.recipes.mathlib4 import (
    extract_declarations_ast,
    parse_theorem_signature,
    parse_proof_structure,
    extract_proof_dependencies,
)


class TestTheoremSignatureExtraction:
    """Test parsing theorem/lemma signatures into structured format."""

    def test_parse_simple_theorem_signature(self):
        """Parse a simple theorem with basic signature."""
        # From Fermat.lean: theorem fermatNumber_strictMono : StrictMono fermatNumber
        signature = "StrictMono fermatNumber"

        result = parse_theorem_signature(signature)

        assert result['return_type'] == "StrictMono fermatNumber"
        assert result['params'] == []
        assert result['constraints'] == []

    def test_parse_theorem_with_forall(self):
        """Parse theorem with universal quantifiers."""
        # From Fermat.lean: theorem coprime_fermatNumber_fermatNumber {m n : ℕ} (hmn : m ≠ n)
        signature = "{m n : ℕ} (hmn : m ≠ n) : Coprime (fermatNumber m) (fermatNumber n)"

        result = parse_theorem_signature(signature)

        assert len(result['params']) == 3
        assert {'name': 'm', 'type': 'ℕ', 'implicit': True} in result['params']
        assert {'name': 'n', 'type': 'ℕ', 'implicit': True} in result['params']
        assert {'name': 'hmn', 'type': 'm ≠ n', 'implicit': False} in result['params']
        assert result['return_type'] == "Coprime (fermatNumber m) (fermatNumber n)"

    def test_parse_definition_signature(self):
        """Parse definition signature."""
        # def fermatNumber (n : ℕ) : ℕ := 2 ^ (2 ^ n) + 1
        signature = "(n : ℕ) : ℕ"

        result = parse_theorem_signature(signature)

        assert len(result['params']) == 1
        assert result['params'][0] == {'name': 'n', 'type': 'ℕ', 'implicit': False}
        assert result['return_type'] == 'ℕ'

    def test_parse_typeclass_constrained_signature(self):
        """Parse signature with typeclass constraints."""
        # variable [Monoid M] {a b : M}
        signature = "[Monoid M] {a b : M} : a * b = b * a"

        result = parse_theorem_signature(signature)

        # Should extract typeclass constraint
        assert any(p['name'] == 'Monoid' for p in result['constraints'])
        assert len([p for p in result['params'] if p['name'] in ['a', 'b']]) == 2


class TestProofStructureExtraction:
    """Test parsing proof bodies into structured tactics/terms."""

    def test_parse_simple_tactic_proof(self):
        """Parse a simple by-tactic proof."""
        proof_text = "by simp [mul_assoc]"

        result = parse_proof_structure(proof_text)

        assert result['style'] == 'tactic'
        assert len(result['tactics']) == 1
        assert result['tactics'][0] == {'name': 'simp', 'args': ['mul_assoc']}
        assert result['has_calc'] is False

    def test_parse_multi_tactic_proof(self):
        """Parse proof with multiple tactics."""
        proof_text = """by
  intro m n
  simp only [fermatNumber, add_lt_add_iff_right]
  ring_nf"""

        result = parse_proof_structure(proof_text)

        assert result['style'] == 'tactic'
        assert len(result['tactics']) == 3
        assert result['tactics'][0] == {'name': 'intro', 'args': ['m', 'n']}
        assert result['tactics'][1]['name'] == 'simp'
        assert 'only' in result['tactics'][1]['args']
        assert result['tactics'][2] == {'name': 'ring_nf', 'args': []}

    def test_parse_calc_proof(self):
        """Parse calculational proof style."""
        proof_text = """calc 0 < 1 - x ^ 2 / 2 := sub_pos.2 <| ...
    _ ≤ cos x := ...
    _ < 1 := ..."""

        result = parse_proof_structure(proof_text)

        assert result['style'] == 'calc'
        assert result['has_calc'] is True
        assert len(result['calc_steps']) >= 2

    def test_parse_term_mode_proof(self):
        """Parse term-mode proof (no 'by' keyword)."""
        proof_text = "⟨mul_assoc⟩"

        result = parse_proof_structure(proof_text)

        assert result['style'] == 'term'
        assert result['term_proof'] == "⟨mul_assoc⟩"

    def test_parse_proof_with_have(self):
        """Parse proof with 'have' statements."""
        proof_text = """by
  have h := three_le_fermatNumber n
  exact h"""

        result = parse_proof_structure(proof_text)

        assert result['style'] == 'tactic'
        assert any(t['name'] == 'have' for t in result['tactics'])
        assert result['has_forward_reasoning'] is True

    def test_parse_proof_with_induction(self):
        """Parse inductive proof."""
        proof_text = """by
  induction n with
  | zero => rfl
  | succ n hn => rw [prod_range_succ, hn]"""

        result = parse_proof_structure(proof_text)

        assert any(t['name'] == 'induction' for t in result['tactics'])
        assert result['has_induction'] is True
        assert len(result['induction_cases']) == 2  # zero, succ


class TestDependencyExtraction:
    """Test extracting theorem/lemma dependencies from proofs."""

    def test_extract_simple_dependencies(self):
        """Extract dependencies from simple proof."""
        proof_text = "by simp using mul_assoc"

        deps = extract_proof_dependencies(proof_text)

        assert 'mul_assoc' in deps

    def test_extract_rw_dependencies(self):
        """Extract dependencies from rewrite tactics."""
        proof_text = "by rw [prod_fermatNumber, Nat.sub_add_cancel]"

        deps = extract_proof_dependencies(proof_text)

        assert 'prod_fermatNumber' in deps
        assert 'Nat.sub_add_cancel' in deps

    def test_extract_exact_dependencies(self):
        """Extract dependencies from exact/refine."""
        proof_text = "exact le_of_lt <| two_lt_fermatNumber _"

        deps = extract_proof_dependencies(proof_text)

        assert 'le_of_lt' in deps
        assert 'two_lt_fermatNumber' in deps


class TestFullDeclarationExtraction:
    """Test extracting complete declarations to JSON AST."""

    def test_extract_simple_theorem(self):
        """Extract a simple theorem to JSON AST."""
        fermat_file = Path("recipes_raw_data/mathlib4/Mathlib/NumberTheory/Fermat.lean")
        if not fermat_file.exists():
            pytest.skip("Fermat.lean not available")

        declarations = extract_declarations_ast(fermat_file, limit=5)

        assert len(declarations) > 0

        # Find fermatNumber definition
        fermat_def = next((d for d in declarations if d['name'] == 'fermatNumber'), None)
        assert fermat_def is not None
        assert fermat_def['type'] == 'def'
        assert fermat_def['signature']['return_type'] == 'ℕ'

    def test_extract_theorem_with_proof(self):
        """Extract theorem with complete proof structure."""
        fermat_file = Path("recipes_raw_data/mathlib4/Mathlib/NumberTheory/Fermat.lean")
        if not fermat_file.exists():
            pytest.skip("Fermat.lean not available")

        declarations = extract_declarations_ast(fermat_file)

        # Find a theorem with proof
        theorem = next((d for d in declarations if d['type'] == 'theorem' and 'proof' in d), None)
        assert theorem is not None
        assert 'signature' in theorem
        assert 'proof' in theorem
        assert 'tactics' in theorem['proof'] or 'term_proof' in theorem['proof']

    def test_json_serialization(self):
        """Ensure extracted AST is JSON-serializable."""
        fermat_file = Path("recipes_raw_data/mathlib4/Mathlib/NumberTheory/Fermat.lean")
        if not fermat_file.exists():
            pytest.skip("Fermat.lean not available")

        declarations = extract_declarations_ast(fermat_file, limit=3)

        # Should be able to serialize to JSON
        json_str = json.dumps(declarations, indent=2)
        assert json_str is not None

        # Should be able to deserialize
        roundtrip = json.loads(json_str)
        assert roundtrip == declarations

    def test_extract_instance_declaration(self):
        """Extract instance declaration."""
        group_file = Path("recipes_raw_data/mathlib4/Mathlib/Algebra/Group/Basic.lean")
        if not group_file.exists():
            pytest.skip("Group/Basic.lean not available")

        declarations = extract_declarations_ast(group_file, limit=10)

        # Find an instance
        instance = next((d for d in declarations if d['type'] == 'instance'), None)
        assert instance is not None
        assert 'signature' in instance


class TestStructuralMetadata:
    """Test extracting structural metadata (sections, opens, etc.)."""

    def test_extract_open_statements(self):
        """Extract open namespace statements."""
        fermat_file = Path("recipes_raw_data/mathlib4/Mathlib/NumberTheory/Fermat.lean")
        if not fermat_file.exists():
            pytest.skip("Fermat.lean not available")

        from warpdata.recipes.mathlib4 import extract_open_statements

        opens = extract_open_statements(fermat_file)

        assert 'namespaces' in opens
        assert 'Function' in opens['namespaces']
        assert 'scoped' in opens
        assert 'BigOperators' in opens['scoped']

    def test_extract_sections(self):
        """Extract section names."""
        group_file = Path("recipes_raw_data/mathlib4/Mathlib/Algebra/Group/Basic.lean")
        if not group_file.exists():
            pytest.skip("Group/Basic.lean not available")

        from warpdata.recipes.mathlib4 import extract_sections

        sections = extract_sections(group_file)

        assert 'Semigroup' in sections
        assert 'Monoid' in sections

    def test_extract_variables(self):
        """Extract variable declarations with typeclasses."""
        group_file = Path("recipes_raw_data/mathlib4/Mathlib/Algebra/Group/Basic.lean")
        if not group_file.exists():
            pytest.skip("Group/Basic.lean not available")

        from warpdata.recipes.mathlib4 import extract_variable_typeclasses

        vars_tc = extract_variable_typeclasses(group_file)

        assert 'Semigroup' in vars_tc
        assert 'Monoid' in vars_tc
        assert vars_tc['Monoid'] > 0  # Should have count


class TestInlineAttributes:
    """Test extraction of inline attributes like @[simp] theorem."""

    def test_extract_inline_simp_theorem(self):
        """Extract theorem with inline @[simp] attribute."""
        fermat_file = Path("recipes_raw_data/mathlib4/Mathlib/NumberTheory/Fermat.lean")
        if not fermat_file.exists():
            pytest.skip("Fermat.lean not available")

        # fermatNumber_zero, fermatNumber_one, fermatNumber_two have @[simp]
        declarations = extract_declarations_ast(fermat_file)

        simp_decls = [d for d in declarations if 'attributes' in d and 'simp' in d['attributes']]

        assert len(simp_decls) >= 3, f"Expected at least 3 @[simp] declarations, found {len(simp_decls)}"

        # Check specific ones
        names = [d['name'] for d in simp_decls]
        assert 'fermatNumber_zero' in names
        assert 'fermatNumber_one' in names
        assert 'fermatNumber_two' in names

    def test_extract_inline_multiple_attributes(self):
        """Extract declaration with multiple inline attributes."""
        # Create a test case with multiple attributes
        from warpdata.recipes.mathlib4 import extract_declarations_ast
        from pathlib import Path
        import tempfile

        test_lean = """
@[simp, to_additive]
theorem test_theorem : True := trivial

@[instance] def test_instance : Inhabited Nat := ⟨0⟩
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
            f.write(test_lean)
            temp_path = Path(f.name)

        try:
            decls = extract_declarations_ast(temp_path)

            # Find theorem with multiple attributes
            test_thm = next((d for d in decls if d['name'] == 'test_theorem'), None)
            assert test_thm is not None
            assert 'attributes' in test_thm
            assert 'simp' in test_thm['attributes']
            assert 'to_additive' in test_thm['attributes']

            # Find instance with inline attribute
            test_inst = next((d for d in decls if d['name'] == 'test_instance'), None)
            assert test_inst is not None
            assert 'attributes' in test_inst
            assert 'instance' in test_inst['attributes']

        finally:
            temp_path.unlink()


class TestStructureExtraction:
    """Test extraction of structure declarations."""

    def test_extract_simple_structure(self):
        """Extract simple structure with fields."""
        from warpdata.recipes.mathlib4 import extract_declarations_ast
        from pathlib import Path
        import tempfile

        test_lean = """
structure Point where
  x : ℝ
  y : ℝ
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
            f.write(test_lean)
            temp_path = Path(f.name)

        try:
            decls = extract_declarations_ast(temp_path)
            
            point_struct = next((d for d in decls if d['name'] == 'Point'), None)
            assert point_struct is not None
            assert point_struct['type'] == 'structure'
            assert 'fields' in point_struct
            assert len(point_struct['fields']) == 2
            
            # Check fields
            assert any(f['name'] == 'x' and f['type'] == 'ℝ' for f in point_struct['fields'])
            assert any(f['name'] == 'y' and f['type'] == 'ℝ' for f in point_struct['fields'])

        finally:
            temp_path.unlink()

    def test_extract_structure_with_params(self):
        """Extract structure with type parameters."""
        from warpdata.recipes.mathlib4 import extract_declarations_ast
        from pathlib import Path
        import tempfile

        test_lean = """
structure Pair (α β : Type*) where
  fst : α
  snd : β
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
            f.write(test_lean)
            temp_path = Path(f.name)

        try:
            decls = extract_declarations_ast(temp_path)
            
            pair_struct = next((d for d in decls if d['name'] == 'Pair'), None)
            assert pair_struct is not None
            assert pair_struct['type'] == 'structure'
            assert 'type_params' in pair_struct
            assert len(pair_struct['fields']) == 2

        finally:
            temp_path.unlink()

    def test_extract_structure_with_attribute(self):
        """Extract structure with @[ext] attribute."""
        from warpdata.recipes.mathlib4 import extract_declarations_ast
        from pathlib import Path
        import tempfile

        test_lean = """
@[ext]
structure Vec3 where
  x : ℝ
  y : ℝ
  z : ℝ
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
            f.write(test_lean)
            temp_path = Path(f.name)

        try:
            decls = extract_declarations_ast(temp_path)
            
            vec_struct = next((d for d in decls if d['name'] == 'Vec3'), None)
            assert vec_struct is not None
            assert 'attributes' in vec_struct
            assert 'ext' in vec_struct['attributes']

        finally:
            temp_path.unlink()


class TestClassExtraction:
    """Test extraction of class (typeclass) declarations."""

    def test_extract_simple_class(self):
        """Extract simple typeclass."""
        from warpdata.recipes.mathlib4 import extract_declarations_ast
        from pathlib import Path
        import tempfile

        test_lean = """
class Inhabited (α : Type*) where
  default : α
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
            f.write(test_lean)
            temp_path = Path(f.name)

        try:
            decls = extract_declarations_ast(temp_path)
            
            inhab_class = next((d for d in decls if d['name'] == 'Inhabited'), None)
            assert inhab_class is not None
            assert inhab_class['type'] == 'class'
            assert 'fields' in inhab_class
            assert len(inhab_class['fields']) == 1
            assert inhab_class['fields'][0]['name'] == 'default'

        finally:
            temp_path.unlink()

    def test_extract_class_with_extends(self):
        """Extract class with extends clause."""
        from warpdata.recipes.mathlib4 import extract_declarations_ast
        from pathlib import Path
        import tempfile

        test_lean = """
class Monoid (α : Type*) extends Semigroup α, One α where
  mul_one : ∀ a : α, a * 1 = a
  one_mul : ∀ a : α, 1 * a = a
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
            f.write(test_lean)
            temp_path = Path(f.name)

        try:
            decls = extract_declarations_ast(temp_path)
            
            monoid_class = next((d for d in decls if d['name'] == 'Monoid'), None)
            assert monoid_class is not None
            assert monoid_class['type'] == 'class'
            assert 'extends' in monoid_class
            assert 'Semigroup' in monoid_class['extends']
            assert 'One' in monoid_class['extends']

        finally:
            temp_path.unlink()

    def test_extract_class_from_real_file(self):
        """Extract class from actual mathlib4 file."""
        fermat_file = Path("recipes_raw_data/mathlib4/Mathlib/Dynamics/Minimal.lean")
        if not fermat_file.exists():
            pytest.skip("Minimal.lean not available")

        declarations = extract_declarations_ast(fermat_file)

        # Should find classes
        classes = [d for d in declarations if d['type'] == 'class']
        assert len(classes) >= 1, f"Expected at least 1 class, found {len(classes)}"


class TestInductiveExtraction:
    """Test extraction of inductive type declarations."""

    def test_extract_simple_inductive(self):
        """Extract simple inductive type with constructors."""
        from warpdata.recipes.mathlib4 import extract_declarations_ast
        from pathlib import Path
        import tempfile

        test_lean = """
inductive Bool where
  | false : Bool
  | true : Bool
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
            f.write(test_lean)
            temp_path = Path(f.name)

        try:
            decls = extract_declarations_ast(temp_path)

            bool_ind = next((d for d in decls if d['name'] == 'Bool'), None)
            assert bool_ind is not None
            assert bool_ind['type'] == 'inductive'
            assert 'constructors' in bool_ind
            assert len(bool_ind['constructors']) == 2

            # Check constructors
            assert any(c['name'] == 'false' for c in bool_ind['constructors'])
            assert any(c['name'] == 'true' for c in bool_ind['constructors'])

        finally:
            temp_path.unlink()

    def test_extract_inductive_with_params(self):
        """Extract inductive type with type parameters."""
        from warpdata.recipes.mathlib4 import extract_declarations_ast
        from pathlib import Path
        import tempfile

        test_lean = """
inductive List (α : Type u) where
  | nil : List α
  | cons (head : α) (tail : List α) : List α
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
            f.write(test_lean)
            temp_path = Path(f.name)

        try:
            decls = extract_declarations_ast(temp_path)

            list_ind = next((d for d in decls if d['name'] == 'List'), None)
            assert list_ind is not None
            assert list_ind['type'] == 'inductive'
            assert 'type_params' in list_ind
            assert '(α : Type u)' in list_ind['type_params']
            assert len(list_ind['constructors']) == 2

            # Check constructor with params
            cons = next((c for c in list_ind['constructors'] if c['name'] == 'cons'), None)
            assert cons is not None
            assert 'List α' in cons['type']

        finally:
            temp_path.unlink()

    def test_extract_inductive_with_deriving(self):
        """Extract inductive with deriving clause."""
        from warpdata.recipes.mathlib4 import extract_declarations_ast
        from pathlib import Path
        import tempfile

        test_lean = """
inductive Ordering where
  | lt : Ordering
  | eq : Ordering
  | gt : Ordering
deriving Repr, DecidableEq
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
            f.write(test_lean)
            temp_path = Path(f.name)

        try:
            decls = extract_declarations_ast(temp_path)

            ord_ind = next((d for d in decls if d['name'] == 'Ordering'), None)
            assert ord_ind is not None
            assert ord_ind['type'] == 'inductive'
            assert 'deriving' in ord_ind
            assert 'Repr' in ord_ind['deriving']
            assert 'DecidableEq' in ord_ind['deriving']

        finally:
            temp_path.unlink()
