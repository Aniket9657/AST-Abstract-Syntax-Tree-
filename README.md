# 🌳 AST Explorer

An interactive Python code analysis and visualization tool built with Streamlit.
Understand how Python parses your code — from raw characters to a structured Abstract Syntax Tree.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Lexical Analysis** | Tokenizes code using `tokenize`; displays tokens with type, value, position |
| **Token Highlighting** | Color-coded categories: keywords, identifiers, operators, literals, comments |
| **AST Generation** | Parses Python via `ast.parse()` into a full AST |
| **AST Visualization** | Graphviz static tree **or** interactive PyVis network with zoom/pan |
| **Node Details** | Click nodes to inspect type, attributes, line numbers |
| **AST Differ** | Side-by-side structural diff of two code snippets |
| **Export** | Download AST as JSON, tokens as CSV, or raw `ast.dump()` text |
| **Error Handling** | Graceful syntax/tokenization errors with line-level messages |

---

## 🚀 Quick Start

```bash
# 1. Clone / copy the project
cd ast_explorer

# 2. Install dependencies
pip install -r requirements.txt

# On some systems you may also need the graphviz system package:
#   macOS:  brew install graphviz
#   Ubuntu: sudo apt install graphviz

# 3. Run the app
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Project Structure

```
ast_explorer/
├── app.py                   # Main Streamlit application
├── requirements.txt
├── README.md
└── modules/
    ├── __init__.py
    ├── tokenizer.py         # Lexical analysis (tokenize module)
    ├── parser.py            # AST parsing, node labels, JSON export
    ├── visualizer.py        # Graphviz + PyVis rendering
    └── differ.py            # Structural AST diff between two snippets
```

---

## 🎓 Learning: Compilation Stages

```
Source Code  →  Tokenize  →  Parse AST  →  Compile  →  Execute
     ①              ②            ③            ④           ⑤
```

This tool visualizes stages **① → ③**:

1. **Lexical Analysis** — The source string is scanned character by character and grouped into *tokens* (keywords, identifiers, operators, literals, …).
2. **Syntax Analysis** — Tokens are fed into a parser that checks grammatical rules and builds the *Abstract Syntax Tree* (AST).
3. **Visualization** — The tree structure reveals how Python "thinks" about your code — which nodes are expressions, statements, control flow, etc.

---

## 🎨 Node Color Guide

| Color | Category |
|-------|----------|
| 🔵 Blue | Statement / Definition (`FunctionDef`, `ClassDef`, `Assign`) |
| 🟣 Purple | Control Flow (`If`, `For`, `While`, `Try`) |
| 🟢 Green | Expression (`BinOp`, `Call`, `BoolOp`) |
| 🟡 Yellow | Comprehension (`ListComp`, `DictComp`) |
| 🔴 Red | Literal / Value (`Constant`, `List`, `Dict`) |
| 🔷 Light Blue | Name / Identifier (`Name`, `arg`) |
| ⚪ Gray | Operator (`Add`, `Eq`, `And`) |

---

## 🛠 Configuration

In the sidebar you can:

- Switch between **Graphviz** (fast, static) and **PyVis** (interactive, zoomable) engines
- Select Graphviz layout algorithm: `dot` (top-down), `neato`, `circo`, `twopi`
- Adjust **max nodes** rendered (performance vs. completeness)
- Toggle whitespace tokens in the token table

---

## 📤 Export Options

From the **Export** tab:

- **AST JSON** — Full recursive tree suitable for further processing
- **Tokens CSV** — Flat token list with types, values, positions  
- **AST Dump** — Python's own `ast.dump()` text format

---

## 🔧 Extending

The modular architecture makes it easy to extend:

- **Add a language**: Implement a new `tokenizer_X.py` and `parser_X.py` with the same interface
- **Add a visualizer**: Drop a new backend in `visualizer.py` following the `build_*` naming convention
- **Add analysis passes**: Extend `parser.py` to annotate nodes with type inference, scope info, etc.

---

## 📦 Dependencies

| Library | Use |
|---------|-----|
| `streamlit` | Web UI framework |
| `graphviz` | Static tree rendering |
| `pyvis` | Interactive network graph |
| `pandas` | Token table display |
| `ast` *(stdlib)* | Python AST parsing |
| `tokenize` *(stdlib)* | Lexical analysis |
