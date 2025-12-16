"""
Test conversion utilities from JSON AST to other symbolic formats.

TDD approach: Write tests first, then implement converters.
"""
import pytest
import json

from warpdata.formats.lean_conversions import (
    to_sexpr,
    to_proof_term,
    to_coq_statement,
    ast_to_symbolic,
)


class TestSExpressionConversion:
    """Test JSON AST → S-expression conversion."""

    def test_convert_simple_definition(self):
        """Convert simple definition to S-expr."""
        ast = {
            'type': 'def',
            'name': 'fermatNumber',
            'signature': {
                'params': [{'name': 'n', 'type': 'ℕ', 'implicit': False}],
                'return_type': 'ℕ',
                'constraints': []
            }
        }

        sexpr = to_sexpr(ast)

        assert sexpr == '(def fermatNumber ((n ℕ)) ℕ)'

    def test_convert_theorem_with_params(self):
        """Convert theorem with parameters to S-expr."""
        ast = {
            'type': 'theorem',
            'name': 'add_comm',
            'signature': {
                'params': [
                    {'name': 'a', 'type': 'ℕ', 'implicit': False},
                    {'name': 'b', 'type': 'ℕ', 'implicit': False}
                ],
                'return_type': 'a + b = b + a',
                'constraints': []
            }
        }

        sexpr = to_sexpr(ast)

        assert sexpr == '(theorem add_comm ((a ℕ) (b ℕ)) (= (+ a b) (+ b a)))'

    def test_convert_theorem_with_implicit_params(self):
        """Convert theorem with implicit parameters."""
        ast = {
            'type': 'theorem',
            'name': 'coprime_fermatNumber',
            'signature': {
                'params': [
                    {'name': 'm', 'type': 'ℕ', 'implicit': True},
                    {'name': 'n', 'type': 'ℕ', 'implicit': True},
                    {'name': 'hmn', 'type': 'm ≠ n', 'implicit': False}
                ],
                'return_type': 'Coprime (fermatNumber m) (fermatNumber n)',
                'constraints': []
            }
        }

        sexpr = to_sexpr(ast)

        # Implicit params should be marked with {}
        assert '{m' in sexpr
        assert '{n' in sexpr
        assert '(hmn' in sexpr

    def test_convert_with_proof_structure(self):
        """Convert theorem with proof tactics to S-expr."""
        ast = {
            'type': 'theorem',
            'name': 'simple_theorem',
            'signature': {
                'params': [],
                'return_type': '1 + 1 = 2',
                'constraints': []
            },
            'proof': {
                'style': 'tactic',
                'tactics': [
                    {'name': 'rfl', 'args': []}
                ]
            }
        }

        sexpr = to_sexpr(ast)

        # Should include proof section
        assert '(proof (tactic rfl))' in sexpr

    def test_convert_calc_proof(self):
        """Convert calc-style proof to S-expr."""
        ast = {
            'type': 'theorem',
            'name': 'chain_theorem',
            'signature': {
                'params': [],
                'return_type': 'a < c',
                'constraints': []
            },
            'proof': {
                'style': 'calc',
                'has_calc': True,
                'calc_steps': ['a < b', 'b < c']
            }
        }

        sexpr = to_sexpr(ast)

        assert '(proof (calc' in sexpr
        assert 'a < b' in sexpr or '(< a b)' in sexpr


class TestProofTermConversion:
    """Test JSON AST → λ-calculus proof term conversion."""

    def test_convert_simple_proof_term(self):
        """Convert simple proof to λ-term."""
        ast = {
            'type': 'theorem',
            'name': 'id_theorem',
            'signature': {
                'params': [{'name': 'a', 'type': 'Prop', 'implicit': False}],
                'return_type': 'a → a',
                'constraints': []
            },
            'proof': {
                'style': 'term',
                'term_proof': 'λ x, x'
            }
        }

        term = to_proof_term(ast)

        assert term == 'λ (a : Prop), (λ x, x)'

    def test_convert_tactic_to_proof_sketch(self):
        """Convert tactic proof to proof sketch."""
        ast = {
            'type': 'theorem',
            'name': 'assoc_theorem',
            'signature': {
                'params': [],
                'return_type': '(a + b) + c = a + (b + c)',
                'constraints': []
            },
            'proof': {
                'style': 'tactic',
                'tactics': [
                    {'name': 'simp', 'args': ['add_assoc']}
                ]
            }
        }

        term = to_proof_term(ast)

        # Should generate proof sketch
        assert 'simp' in term or 'add_assoc' in term


class TestCoqConversion:
    """Test JSON AST → Coq vernacular conversion."""

    def test_convert_to_coq_theorem(self):
        """Convert theorem to Coq syntax."""
        ast = {
            'type': 'theorem',
            'name': 'add_comm',
            'signature': {
                'params': [
                    {'name': 'n', 'type': 'nat', 'implicit': False},
                    {'name': 'm', 'type': 'nat', 'implicit': False}
                ],
                'return_type': 'n + m = m + n',
                'constraints': []
            },
            'proof': {
                'style': 'tactic',
                'tactics': [{'name': 'ring', 'args': []}]
            }
        }

        coq = to_coq_statement(ast)

        assert 'Theorem add_comm' in coq
        assert 'forall n m : nat' in coq
        assert 'n + m = m + n' in coq
        assert 'Proof.' in coq
        assert 'ring.' in coq
        assert 'Qed.' in coq

    def test_convert_definition_to_coq(self):
        """Convert definition to Coq."""
        ast = {
            'type': 'def',
            'name': 'double',
            'signature': {
                'params': [{'name': 'n', 'type': 'nat', 'implicit': False}],
                'return_type': 'nat',
                'constraints': []
            },
            'body': '2 * n'
        }

        coq = to_coq_statement(ast)

        assert 'Definition double' in coq
        assert '(n : nat) : nat' in coq


class TestSymbolicFormats:
    """Test generic symbolic format converter."""

    def test_ast_to_symbolic_dispatch(self):
        """Test that ast_to_symbolic dispatches correctly."""
        ast = {
            'type': 'theorem',
            'name': 'test',
            'signature': {
                'params': [],
                'return_type': 'True',
                'constraints': []
            }
        }

        # Should support multiple formats
        sexpr = ast_to_symbolic(ast, format='sexpr')
        assert sexpr.startswith('(theorem')

        term = ast_to_symbolic(ast, format='proof_term')
        assert term is not None

        coq = ast_to_symbolic(ast, format='coq')
        assert 'Theorem' in coq or 'Lemma' in coq

    def test_roundtrip_json(self):
        """Test that JSON roundtrip preserves structure."""
        ast = {
            'type': 'theorem',
            'name': 'test_theorem',
            'signature': {
                'params': [{'name': 'x', 'type': 'ℕ', 'implicit': False}],
                'return_type': 'x = x',
                'constraints': []
            },
            'proof': {
                'style': 'term',
                'term_proof': 'rfl'
            }
        }

        # JSON roundtrip
        json_str = json.dumps(ast)
        roundtrip = json.loads(json_str)

        assert roundtrip == ast

        # Converting roundtripped AST should work
        sexpr = to_sexpr(roundtrip)
        assert sexpr is not None


class TestBatchConversion:
    """Test converting multiple declarations efficiently."""

    def test_convert_declaration_list(self):
        """Convert list of declarations to S-expressions."""
        from warpdata.formats.lean_conversions import convert_declarations

        declarations = [
            {
                'type': 'def',
                'name': 'id',
                'signature': {
                    'params': [{'name': 'x', 'type': 'α', 'implicit': False}],
                    'return_type': 'α',
                    'constraints': []
                }
            },
            {
                'type': 'theorem',
                'name': 'id_id',
                'signature': {
                    'params': [{'name': 'x', 'type': 'α', 'implicit': False}],
                    'return_type': 'id (id x) = x',
                    'constraints': []
                }
            }
        ]

        results = convert_declarations(declarations, format='sexpr')

        assert len(results) == 2
        assert '(def id' in results[0]
        assert '(theorem id_id' in results[1]

    def test_convert_to_multiple_formats(self):
        """Convert same declarations to multiple formats."""
        from warpdata.formats.lean_conversions import convert_to_all_formats

        ast = {
            'type': 'theorem',
            'name': 'simple',
            'signature': {
                'params': [],
                'return_type': 'True',
                'constraints': []
            }
        }

        all_formats = convert_to_all_formats(ast)

        assert 'sexpr' in all_formats
        assert 'proof_term' in all_formats
        assert 'coq' in all_formats
        assert all(v is not None for v in all_formats.values())
