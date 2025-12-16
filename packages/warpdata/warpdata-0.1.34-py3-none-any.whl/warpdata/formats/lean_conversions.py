"""
Convert Lean 4 JSON AST to various symbolic formats.

Supports conversion to:
- S-expressions (Lisp-style)
- Proof terms (λ-calculus)
- Coq vernacular
"""
from typing import Dict, List, Any, Optional


def to_sexpr(decl: Dict[str, Any]) -> str:
    """
    Convert JSON AST declaration to S-expression format.

    Args:
        decl: Declaration dict with type, name, signature, proof fields

    Returns:
        S-expression string

    Example:
        >>> decl = {'type': 'def', 'name': 'id', ...}
        >>> to_sexpr(decl)
        '(def id ((x α)) α)'
    """
    decl_type = decl['type']
    name = decl['name']
    sig = decl.get('signature', {})

    # Build parameter list
    params_sexpr = _params_to_sexpr(sig.get('params', []))

    # Build return type
    ret_type = sig.get('return_type', '')
    ret_sexpr = _type_to_sexpr(ret_type)

    # Base declaration
    base = f"({decl_type} {name} {params_sexpr} {ret_sexpr})"

    # Add proof if present
    if 'proof' in decl:
        proof_sexpr = _proof_to_sexpr(decl['proof'])
        return f"({decl_type} {name} {params_sexpr} {ret_sexpr} {proof_sexpr})"

    return base


def _params_to_sexpr(params: List[Dict[str, Any]]) -> str:
    """Convert parameter list to S-expression."""
    if not params:
        return "()"

    param_strs = []
    for p in params:
        name = p['name']
        typ = p['type']

        if p.get('implicit', False):
            param_strs.append(f"{{{name} {typ}}}")
        else:
            param_strs.append(f"({name} {typ})")

    return f"({' '.join(param_strs)})"


def _type_to_sexpr(type_expr: str) -> str:
    """Convert type expression to S-expression (simplified)."""
    import re

    # Simple infix-to-prefix converter for common operators
    # Handle: =, +, -, *, /, <, >, ≤, ≥, ≠, etc.

    expr = type_expr.strip()

    # Operators with precedence (lower number = lower precedence, evaluated last)
    operators = [
        ('=', 1), ('≠', 1), ('≤', 1), ('≥', 1), ('<', 1), ('>', 1),  # Comparisons
        ('+', 2), ('-', 2),  # Addition/subtraction
        ('*', 3), ('/', 3), ('×', 3),  # Multiplication/division
    ]

    # Find lowest-precedence operator (rightmost if tied)
    lowest_op = None
    lowest_prec = float('inf')
    lowest_pos = -1

    depth = 0  # Track parentheses depth
    for i in range(len(expr) - 1, -1, -1):  # Scan right-to-left
        if expr[i] == ')':
            depth += 1
        elif expr[i] == '(':
            depth -= 1
        elif depth == 0:  # Only consider operators outside parens
            for op, prec in operators:
                if expr[i:i+len(op)] == op:
                    if prec <= lowest_prec:  # <= for right-associativity
                        lowest_prec = prec
                        lowest_op = op
                        lowest_pos = i
                    break

    # If operator found, recursively convert
    if lowest_op and lowest_pos >= 0:
        left = expr[:lowest_pos].strip()
        right = expr[lowest_pos + len(lowest_op):].strip()

        # Recursively convert sub-expressions
        left_sexpr = _type_to_sexpr(left)
        right_sexpr = _type_to_sexpr(right)

        return f"({lowest_op} {left_sexpr} {right_sexpr})"

    # No operator found - return as atomic expression
    return expr


def _proof_to_sexpr(proof: Dict[str, Any]) -> str:
    """Convert proof structure to S-expression."""
    style = proof.get('style', 'unknown')

    if style == 'tactic':
        tactics = proof.get('tactics', [])
        tactic_sexprs = []
        for t in tactics:
            args = t.get('args', [])
            if args:
                tactic_sexprs.append(f"({t['name']} {' '.join(str(a) for a in args)})")
            else:
                tactic_sexprs.append(t['name'])
        return f"(proof (tactic {' '.join(tactic_sexprs)}))"

    elif style == 'calc':
        steps = proof.get('calc_steps', [])
        steps_str = ' '.join(f'"{step}"' for step in steps)
        return f"(proof (calc {steps_str}))"

    elif style == 'term':
        term = proof.get('term_proof', '')
        return f"(proof (term {term}))"

    return "(proof unknown)"


def to_proof_term(decl: Dict[str, Any]) -> str:
    """
    Convert JSON AST to λ-calculus proof term (sketch).

    Args:
        decl: Declaration dict

    Returns:
        Proof term string

    Example:
        >>> to_proof_term({'type': 'theorem', 'name': 'id', ...})
        'λ (a : Prop), (λ x, x)'
    """
    sig = decl.get('signature', {})
    params = sig.get('params', [])

    # Build λ-abstraction for parameters
    lambda_prefix = ""
    for p in params:
        name = p['name']
        typ = p['type']
        lambda_prefix += f"λ ({name} : {typ}), "

    # Handle proof
    proof = decl.get('proof', {})
    style = proof.get('style', 'unknown')

    if style == 'term':
        term = proof.get('term_proof', '?')
        return f"{lambda_prefix}({term})" if lambda_prefix else term

    elif style == 'tactic':
        # Generate proof sketch from tactics
        tactics = proof.get('tactics', [])
        tactic_names = ', '.join(t['name'] for t in tactics)
        return f"{lambda_prefix}<proof by {tactic_names}>"

    return f"{lambda_prefix}?"


def to_coq_statement(decl: Dict[str, Any]) -> str:
    """
    Convert JSON AST to Coq vernacular.

    Args:
        decl: Declaration dict

    Returns:
        Coq statement string

    Example:
        >>> to_coq_statement({'type': 'theorem', 'name': 'add_comm', ...})
        'Theorem add_comm : forall n m : nat, n + m = m + n.\\nProof.\\n  ring.\\nQed.'
    """
    decl_type = decl['type']
    name = decl['name']
    sig = decl.get('signature', {})

    # Map Lean types to Coq
    if decl_type in ['theorem', 'lemma']:
        coq_keyword = 'Theorem' if decl_type == 'theorem' else 'Lemma'
        use_forall = True
    elif decl_type == 'def':
        coq_keyword = 'Definition'
        use_forall = False  # Definitions use direct params
    elif decl_type == 'instance':
        coq_keyword = 'Instance'
        use_forall = True
    else:
        coq_keyword = 'Definition'
        use_forall = False

    # Build parameter list - group params by type for compact forall syntax
    params = sig.get('params', [])
    if params:
        if use_forall:
            # Group consecutive params with same type
            grouped = []
            i = 0
            while i < len(params):
                current_type = _lean_type_to_coq(params[i]['type'])
                names = [params[i]['name']]
                j = i + 1
                # Collect consecutive params with same type
                while j < len(params) and _lean_type_to_coq(params[j]['type']) == current_type:
                    names.append(params[j]['name'])
                    j += 1
                # Format: "n m : nat" or just "n : nat"
                grouped.append(f"{' '.join(names)} : {current_type}")
                i = j
            param_part = f"forall {', '.join(grouped)}, "
        else:
            # Direct params for definitions
            param_strs = [f"({p['name']} : {_lean_type_to_coq(p['type'])})" for p in params]
            param_part = f"{' '.join(param_strs)} : "
    else:
        param_part = ""

    # Return type
    ret_type = sig.get('return_type', '')
    coq_ret = _lean_type_to_coq(ret_type)

    # Build statement
    if use_forall or not params:
        statement = f"{coq_keyword} {name} : {param_part}{coq_ret}."
    else:
        # Definition with direct params
        statement = f"{coq_keyword} {name} {param_part}{coq_ret}."

    # Add proof if present
    proof = decl.get('proof', {})
    if proof:
        proof_body = _proof_to_coq(proof)
        return f"{statement}\nProof.\n{proof_body}\nQed."

    # Definition body
    if 'body' in decl:
        body = _lean_expr_to_coq(decl['body'])
        return f"{statement} := {body}."

    return statement


def _lean_type_to_coq(lean_type: str) -> str:
    """Convert Lean type to Coq type (basic mapping)."""
    # Basic type mappings
    mappings = {
        'ℕ': 'nat',
        'ℤ': 'Z',
        'ℚ': 'Q',
        'ℝ': 'R',
        'Bool': 'bool',
        'Prop': 'Prop',
    }

    result = lean_type
    for lean, coq in mappings.items():
        result = result.replace(lean, coq)

    return result


def _lean_expr_to_coq(lean_expr: str) -> str:
    """Convert Lean expression to Coq expression (basic mapping)."""
    return _lean_type_to_coq(lean_expr)


def _proof_to_coq(proof: Dict[str, Any]) -> str:
    """Convert proof to Coq tactics."""
    style = proof.get('style', 'unknown')

    if style == 'tactic':
        tactics = proof.get('tactics', [])
        tactic_lines = []
        for t in tactics:
            name = t['name']
            args = t.get('args', [])

            # Map Lean tactics to Coq
            coq_tactic = _lean_tactic_to_coq(name, args)
            tactic_lines.append(f"  {coq_tactic}.")

        return '\n'.join(tactic_lines)

    elif style == 'term':
        term = proof.get('term_proof', 'admit')
        return f"  exact {term}."

    return "  admit."


def _lean_tactic_to_coq(tactic: str, args: List[str]) -> str:
    """Map Lean tactic to Coq equivalent."""
    # Basic tactic mappings
    mappings = {
        'rfl': 'reflexivity',
        'simp': 'simpl',
        'ring': 'ring',
        'ring_nf': 'ring',
        'linarith': 'lia',
        'omega': 'lia',
        'intro': 'intro',
        'apply': 'apply',
        'exact': 'exact',
        'rw': 'rewrite',
        'induction': 'induction',
        'cases': 'destruct',
    }

    coq_tactic = mappings.get(tactic, tactic)

    if args:
        return f"{coq_tactic} {' '.join(args)}"
    return coq_tactic


def ast_to_symbolic(decl: Dict[str, Any], format: str = 'sexpr') -> str:
    """
    Convert JSON AST to symbolic format (dispatcher).

    Args:
        decl: Declaration dict
        format: Target format ('sexpr', 'proof_term', 'coq')

    Returns:
        Symbolic representation in requested format
    """
    if format == 'sexpr':
        return to_sexpr(decl)
    elif format == 'proof_term':
        return to_proof_term(decl)
    elif format == 'coq':
        return to_coq_statement(decl)
    else:
        raise ValueError(f"Unknown format: {format}")


def convert_declarations(declarations: List[Dict[str, Any]], format: str = 'sexpr') -> List[str]:
    """
    Convert list of declarations to symbolic format.

    Args:
        declarations: List of declaration dicts
        format: Target format

    Returns:
        List of symbolic representations
    """
    return [ast_to_symbolic(decl, format) for decl in declarations]


def convert_to_all_formats(decl: Dict[str, Any]) -> Dict[str, str]:
    """
    Convert declaration to all supported formats.

    Args:
        decl: Declaration dict

    Returns:
        Dict mapping format name to symbolic representation
    """
    return {
        'sexpr': to_sexpr(decl),
        'proof_term': to_proof_term(decl),
        'coq': to_coq_statement(decl),
    }
