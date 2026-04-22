"""
AST Parser Module
Parses Python source code into an Abstract Syntax Tree.
"""

import ast
import json
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ASTNode:
    id: str
    label: str
    node_type: str
    details: Dict[str, Any]
    children: List[str] = field(default_factory=list)
    parent: Optional[str] = None
    depth: int = 0


def get_node_label(node: ast.AST) -> str:
    """Generate a concise, informative label for an AST node."""
    node_type = type(node).__name__

    label_map = {
        'FunctionDef': lambda n: f"def {n.name}()",
        'AsyncFunctionDef': lambda n: f"async def {n.name}()",
        'ClassDef': lambda n: f"class {n.name}",
        'Name': lambda n: f"Name: {n.id}",
        'Constant': lambda n: f"Const: {repr(n.value)}" if len(repr(n.value)) < 20 else f"Const: {repr(n.value)[:18]}…",
        'Attribute': lambda n: f".{n.attr}",
        'Import': lambda n: f"import {', '.join(a.name for a in n.names[:2])}{'…' if len(n.names) > 2 else ''}",
        'ImportFrom': lambda n: f"from {n.module or '.'} import",
        'Assign': lambda _: "=  Assign",
        'AugAssign': lambda n: f"{ast.dump(n.op)[:3]}= AugAssign",
        'AnnAssign': lambda _: ": AnnAssign",
        'Return': lambda _: "return",
        'Delete': lambda _: "del",
        'If': lambda _: "if",
        'While': lambda _: "while",
        'For': lambda _: "for … in",
        'With': lambda _: "with",
        'Try': lambda _: "try",
        'ExceptHandler': lambda n: f"except {n.type.id if isinstance(n.type, ast.Name) else ''}",
        'Raise': lambda _: "raise",
        'Assert': lambda _: "assert",
        'Pass': lambda _: "pass",
        'Break': lambda _: "break",
        'Continue': lambda _: "continue",
        'BinOp': lambda n: f"BinOp {get_op_symbol(n.op)}",
        'UnaryOp': lambda n: f"UnaryOp {get_op_symbol(n.op)}",
        'BoolOp': lambda n: f"BoolOp {get_op_symbol(n.op)}",
        'Compare': lambda n: f"Compare {' '.join(get_op_symbol(o) for o in n.ops)}",
        'Call': lambda _: "Call ()",
        'Subscript': lambda _: "Subscript []",
        'Starred': lambda _: "*Starred",
        'Lambda': lambda _: "λ lambda",
        'IfExp': lambda _: "x if y else z",
        'ListComp': lambda _: "[…]  ListComp",
        'SetComp': lambda _: "{…}  SetComp",
        'DictComp': lambda _: "{k:v}  DictComp",
        'GeneratorExp': lambda _: "(…)  GeneratorExp",
        'Yield': lambda _: "yield",
        'YieldFrom': lambda _: "yield from",
        'Await': lambda _: "await",
        'List': lambda _: "[ ]  List",
        'Tuple': lambda _: "( )  Tuple",
        'Set': lambda _: "{ }  Set",
        'Dict': lambda _: "{ }  Dict",
        'Global': lambda n: f"global {', '.join(n.names)}",
        'Nonlocal': lambda n: f"nonlocal {', '.join(n.names)}",
        'Module': lambda _: "Module",
    }

    if node_type in label_map:
        try:
            return label_map[node_type](node)
        except (AttributeError, TypeError):
            pass
    return node_type


def get_op_symbol(op: ast.AST) -> str:
    """Convert AST operator node to symbol string."""
    op_map = {
        'Add': '+', 'Sub': '-', 'Mult': '*', 'Div': '/', 'FloorDiv': '//',
        'Mod': '%', 'Pow': '**', 'MatMult': '@',
        'BitAnd': '&', 'BitOr': '|', 'BitXor': '^', 'LShift': '<<', 'RShift': '>>',
        'And': 'and', 'Or': 'or',
        'Not': 'not', 'Invert': '~', 'UAdd': '+', 'USub': '-',
        'Eq': '==', 'NotEq': '!=', 'Lt': '<', 'LtE': '<=', 'Gt': '>', 'GtE': '>=',
        'Is': 'is', 'IsNot': 'is not', 'In': 'in', 'NotIn': 'not in',
    }
    return op_map.get(type(op).__name__, type(op).__name__)


def get_node_details(node: ast.AST) -> Dict[str, Any]:
    """Extract meaningful attributes from an AST node for display."""
    details = {'type': type(node).__name__}

    skip_fields = {'body', 'orelse', 'handlers', 'finalbody', 'elts',
                   'args', 'keywords', 'decorator_list', 'bases', 'values',
                   'targets', 'keys', 'generators', 'comparators', 'ops'}

    for field_name, value in ast.iter_fields(node):
        if field_name in skip_fields:
            continue
        if isinstance(value, list):
            if all(isinstance(v, ast.AST) for v in value):
                continue
            details[field_name] = str(value)[:100]
        elif isinstance(value, ast.AST):
            details[field_name] = type(value).__name__
        elif value is not None:
            details[field_name] = value

    # Add line info if available
    if hasattr(node, 'lineno'):
        details['line'] = node.lineno
    if hasattr(node, 'col_offset'):
        details['col'] = node.col_offset

    return details


def get_node_color_category(node_type: str) -> str:
    """Map node types to color categories."""
    categories = {
        'statement': {'Module', 'FunctionDef', 'AsyncFunctionDef', 'ClassDef',
                      'Return', 'Delete', 'Assign', 'AugAssign', 'AnnAssign',
                      'Pass', 'Break', 'Continue', 'Global', 'Nonlocal',
                      'Import', 'ImportFrom'},
        'control': {'If', 'For', 'While', 'With', 'Try', 'ExceptHandler',
                    'Raise', 'Assert'},
        'expression': {'BinOp', 'UnaryOp', 'BoolOp', 'Compare', 'Call',
                       'IfExp', 'Attribute', 'Subscript', 'Starred',
                       'Lambda', 'Await', 'Yield', 'YieldFrom'},
        'comprehension': {'ListComp', 'SetComp', 'DictComp', 'GeneratorExp',
                          'comprehension'},
        'literal': {'Constant', 'List', 'Tuple', 'Set', 'Dict', 'JoinedStr'},
        'name': {'Name', 'arg', 'alias'},
        'operator': {'Add', 'Sub', 'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow',
                     'And', 'Or', 'Not', 'Eq', 'NotEq', 'Lt', 'LtE', 'Gt',
                     'GtE', 'Is', 'IsNot', 'In', 'NotIn'},
    }
    for cat, types in categories.items():
        if node_type in types:
            return cat
    return 'other'


_node_counter = 0


def parse_ast(source_code: str) -> Tuple[Optional[ast.AST], Optional[str]]:
    """Parse Python source code into an AST."""
    try:
        tree = ast.parse(source_code)
        return tree, None
    except SyntaxError as e:
        return None, f"Syntax error at line {e.lineno}, col {e.offset}: {e.msg}"
    except Exception as e:
        return None, f"Parse error: {str(e)}"


def ast_to_nodes_edges(tree: ast.AST) -> Tuple[List[Dict], List[Dict]]:
    """
    Convert AST to lists of nodes and edges for visualization.
    Returns (nodes, edges) where each is a list of dicts.
    """
    nodes = []
    edges = []
    counter = [0]

    def visit(node: ast.AST, parent_id: Optional[str] = None, depth: int = 0):
        node_id = f"n{counter[0]}"
        counter[0] += 1

        node_type = type(node).__name__
        label = get_node_label(node)
        details = get_node_details(node)
        category = get_node_color_category(node_type)

        nodes.append({
            'id': node_id,
            'label': label,
            'type': node_type,
            'category': category,
            'details': details,
            'depth': depth,
        })

        if parent_id is not None:
            edges.append({'from': parent_id, 'to': node_id})

        for child in ast.iter_child_nodes(node):
            visit(child, node_id, depth + 1)

    visit(tree)
    return nodes, edges


def ast_to_json(tree: ast.AST) -> str:
    """Export AST as a JSON string."""

    def node_to_dict(node: ast.AST) -> Dict:
        result = {'_type': type(node).__name__}
        for field_name, value in ast.iter_fields(node):
            if isinstance(value, list):
                result[field_name] = [
                    node_to_dict(v) if isinstance(v, ast.AST) else v
                    for v in value
                ]
            elif isinstance(value, ast.AST):
                result[field_name] = node_to_dict(value)
            else:
                result[field_name] = value
        if hasattr(node, 'lineno'):
            result['lineno'] = node.lineno
        return result

    return json.dumps(node_to_dict(tree), indent=2, default=str)
