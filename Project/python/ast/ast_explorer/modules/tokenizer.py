"""
Lexical Analysis Module
Tokenizes Python source code using the built-in tokenize module.
"""

import tokenize
import io
import token as token_module
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Token:
    type_id: int
    type_name: str
    value: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    category: str  # keyword, identifier, operator, literal, comment, other


# Python keywords
KEYWORDS = {
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
    'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
    'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
    'while', 'with', 'yield'
}

OPERATORS = {
    '+', '-', '*', '/', '//', '%', '**', '@',
    '=', '+=', '-=', '*=', '/=', '//=', '%=', '**=', '@=',
    '==', '!=', '<', '>', '<=', '>=',
    '&', '|', '^', '~', '<<', '>>', '&=', '|=', '^=', '<<=', '>>=',
    '->', ':=', '.', ',', ':', ';', '(', ')', '[', ']', '{', '}', '...'
}


def categorize_token(tok_type: int, tok_value: str) -> str:
    """Categorize a token into a semantic group."""
    if tok_type == token_module.NAME:
        if tok_value in KEYWORDS:
            return 'keyword'
        return 'identifier'
    elif tok_type == token_module.NUMBER:
        return 'literal_number'
    elif tok_type == token_module.STRING:
        return 'literal_string'
    elif tok_type == token_module.COMMENT:
        return 'comment'
    elif tok_type == token_module.OP:
        if tok_value in {'(', ')', '[', ']', '{', '}'}:
            return 'delimiter'
        return 'operator'
    elif tok_type in {token_module.NEWLINE, token_module.NL, token_module.INDENT, token_module.DEDENT}:
        return 'whitespace'
    elif tok_type == token_module.ENCODING:
        return 'encoding'
    elif tok_type == token_module.ENDMARKER:
        return 'endmarker'
    return 'other'


def tokenize_code(source_code: str) -> tuple[List[Token], Optional[str]]:
    """
    Tokenize Python source code.
    Returns (tokens, error_message). error_message is None on success.
    """
    tokens = []
    error = None

    try:
        # Ensure the code ends with a newline
        if source_code and not source_code.endswith('\n'):
            source_code += '\n'

        readline = io.StringIO(source_code).readline
        for tok in tokenize.generate_tokens(readline):
            tok_type = tok.type
            tok_value = tok.string
            start = tok.start
            end = tok.end

            type_name = token_module.tok_name.get(tok_type, 'UNKNOWN')
            category = categorize_token(tok_type, tok_value)

            # Skip ENDMARKER and encoding for cleaner display
            if tok_type in {token_module.ENDMARKER, token_module.ENCODING}:
                continue

            tokens.append(Token(
                type_id=tok_type,
                type_name=type_name,
                value=repr(tok_value) if tok_type == token_module.STRING else tok_value,
                start_line=start[0],
                start_col=start[1],
                end_line=end[0],
                end_col=end[1],
                category=category
            ))

    except tokenize.TokenError as e:
        error = f"Tokenization error: {e}"
    except IndentationError as e:
        error = f"Indentation error at line {e.lineno}: {e.msg}"

    return tokens, error


def tokens_to_display(tokens: List[Token]) -> List[dict]:
    """Convert tokens to a list of dicts for DataFrame display."""
    return [
        {
            'Token Type': t.type_name,
            'Value': t.value,
            'Category': t.category.replace('_', ' ').title(),
            'Line': t.start_line,
            'Col Start': t.start_col,
            'Col End': t.end_col,
        }
        for t in tokens
        if t.category not in {'whitespace', 'endmarker', 'encoding'}
    ]
