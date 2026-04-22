"""
AST Differ Module
Compare two Python ASTs and highlight structural differences.
"""

import ast
from typing import Dict, List, Tuple, Set


def ast_signature(node: ast.AST, depth: int = 0, max_depth: int = 10) -> str:
    """Generate a structural signature string for an AST subtree."""
    if depth > max_depth:
        return '...'
    parts = [type(node).__name__]
    for child in ast.iter_child_nodes(node):
        parts.append(ast_signature(child, depth + 1, max_depth))
    return '(' + ','.join(parts) + ')'


def collect_node_types(tree: ast.AST) -> Dict[str, int]:
    """Count occurrences of each node type in the AST."""
    counts: Dict[str, int] = {}
    for node in ast.walk(tree):
        t = type(node).__name__
        counts[t] = counts.get(t, 0) + 1
    return counts


def diff_asts(tree1: ast.AST, tree2: ast.AST) -> Dict:
    """
    Compute a high-level structural diff between two ASTs.
    Returns a dict with 'added', 'removed', 'changed', and 'stats'.
    """
    counts1 = collect_node_types(tree1)
    counts2 = collect_node_types(tree2)

    all_types: Set[str] = set(counts1) | set(counts2)

    added = {}
    removed = {}
    changed = {}
    same = {}

    for t in sorted(all_types):
        c1 = counts1.get(t, 0)
        c2 = counts2.get(t, 0)
        if c1 == 0 and c2 > 0:
            added[t] = c2
        elif c2 == 0 and c1 > 0:
            removed[t] = c1
        elif c1 != c2:
            changed[t] = {'before': c1, 'after': c2, 'delta': c2 - c1}
        else:
            same[t] = c1

    sig1 = ast_signature(tree1)
    sig2 = ast_signature(tree2)

    total1 = sum(counts1.values())
    total2 = sum(counts2.values())

    return {
        'added': added,
        'removed': removed,
        'changed': changed,
        'same': same,
        'structurally_identical': sig1 == sig2,
        'stats': {
            'nodes_before': total1,
            'nodes_after': total2,
            'delta': total2 - total1,
        }
    }
