"""
AST Explorer — Interactive Python Code Analysis & Visualization
A Streamlit application for lexical analysis and AST visualization.
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from modules.tokenizer import tokenize_code, tokens_to_display
from modules.parser import parse_ast, ast_to_nodes_edges, ast_to_json
from modules.visualizer import build_graphviz_tree, build_pyvis_html, get_legend_html
from modules.differ import diff_asts

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AST Explorer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

/* Global dark theme */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #080810;
    color: #C8D0E8;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* App header */
.ast-header {
    background: linear-gradient(135deg, #0F0F25 0%, #1A1040 50%, #0F2030 100%);
    border: 1px solid #2A2A55;
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.ast-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, #3B1FCC33 0%, transparent 70%);
    pointer-events: none;
}
.ast-header h1 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #7B6EF6, #42C3F5, #3DD68C);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 8px 0;
}
.ast-header p {
    color: #888AAA;
    font-size: 0.95rem;
    margin: 0;
}

/* Stage badges */
.stage-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #1A1A3A, #252545);
    border: 1px solid #3A3A66;
    border-radius: 24px;
    padding: 6px 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #8888CC;
    margin-bottom: 16px;
}

/* Section headers */
.section-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6666AA;
    border-bottom: 1px solid #1E1E3A;
    padding-bottom: 8px;
    margin: 20px 0 14px 0;
}

/* Token table styling */
.token-table-wrapper {
    background: #0C0C1E;
    border: 1px solid #1E1E3A;
    border-radius: 10px;
    padding: 12px;
}

/* Category color tags */
.cat-keyword       { background:#1E2A5E; color:#7B9EF5; border:1px solid #3B5EC0; border-radius:4px; padding:2px 8px; font-size:11px; }
.cat-identifier    { background:#1A3A2A; color:#5DD890; border:1px solid #2E7A50; border-radius:4px; padding:2px 8px; font-size:11px; }
.cat-literal-number{ background:#3A1A1A; color:#F58E7B; border:1px solid #883030; border-radius:4px; padding:2px 8px; font-size:11px; }
.cat-literal-string{ background:#3A2A1A; color:#F5C87B; border:1px solid #88601A; border-radius:4px; padding:2px 8px; font-size:11px; }
.cat-operator      { background:#2A2A2A; color:#AAAAAA; border:1px solid #555555; border-radius:4px; padding:2px 8px; font-size:11px; }
.cat-comment       { background:#1E1E1E; color:#666666; border:1px solid #333333; border-radius:4px; padding:2px 8px; font-size:11px; }
.cat-delimiter     { background:#2A2040; color:#AA99FF; border:1px solid #6644AA; border-radius:4px; padding:2px 8px; font-size:11px; }

/* Error box */
.error-box {
    background: #1F0A0A;
    border: 1px solid #8B2020;
    border-left: 4px solid #EE4444;
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875rem;
    color: #FF8888;
    margin: 12px 0;
}

/* Info box */
.info-box {
    background: #0A1A2F;
    border: 1px solid #1B4A7A;
    border-left: 4px solid #42A5F5;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 0.875rem;
    color: #90CAF9;
    margin: 12px 0;
}

/* Stats row */
.stat-card {
    background: linear-gradient(135deg, #10102A, #181830);
    border: 1px solid #2A2A50;
    border-radius: 10px;
    padding: 14px 20px;
    text-align: center;
}
.stat-card .val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #7B9EF5;
}
.stat-card .lbl {
    font-size: 0.75rem;
    color: #666688;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 2px;
}

/* Flow pipeline */
.pipeline {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin: 16px 0;
}
.pipe-step {
    background: #12122A;
    border: 1px solid #2A2A55;
    border-radius: 8px;
    padding: 10px 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #9999CC;
}
.pipe-step.active {
    background: linear-gradient(135deg, #1E1870, #0E2850);
    border-color: #5B5EEF;
    color: #AABBFF;
}
.pipe-arrow {
    color: #3A3A60;
    font-size: 1.2rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0A0A1A;
    border-right: 1px solid #1A1A35;
}
[data-testid="stSidebar"] .css-1d391kg {
    padding-top: 16px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #0C0C1E;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #1E1E3A;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    border-radius: 8px;
    color: #666688;
    padding: 6px 18px;
}
.stTabs [aria-selected="true"] {
    background: #1E1E4A !important;
    color: #AABBFF !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2B1FCC, #1A4FCC);
    border: none;
    border-radius: 8px;
    color: white;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    padding: 10px 24px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #3B2FEC, #2A5FEC);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(80, 100, 255, 0.3);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
}

/* Code area */
.stTextArea textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.875rem !important;
    background: #0C0C20 !important;
    border: 1px solid #2A2A50 !important;
    color: #C8D0E8 !important;
    border-radius: 8px !important;
    line-height: 1.6 !important;
}

/* Diff cards */
.diff-added   { background:#0A2A0A; border:1px solid #1E6B1E; border-radius:6px; padding:8px 14px; margin:4px 0; color:#5DD890; }
.diff-removed { background:#2A0A0A; border:1px solid #6B1E1E; border-radius:6px; padding:8px 14px; margin:4px 0; color:#F56E6E; }
.diff-changed { background:#2A2A0A; border:1px solid #6B6B1E; border-radius:6px; padding:8px 14px; margin:4px 0; color:#F5D142; }
</style>
""", unsafe_allow_html=True)

# ── Sample Code ────────────────────────────────────────────────────────────────
SAMPLE_CODE = '''def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

# Demonstrate list comprehension
squares = [x ** 2 for x in range(10) if x % 2 == 0]

class Calculator:
    def __init__(self, value: float = 0):
        self.value = value

    def add(self, x):
        return Calculator(self.value + x)

    def __repr__(self):
        return f"Calculator({self.value})"

result = fibonacci(10)
print(f"fib(10) = {result}")
'''

DIFF_SAMPLE_A = '''def greet(name):
    msg = "Hello, " + name
    print(msg)
    return msg

x = 42
'''

DIFF_SAMPLE_B = '''def greet(name, greeting="Hello"):
    msg = f"{greeting}, {name}!"
    print(msg)
    return msg.upper()

x = 42
y = x * 2
'''

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family:JetBrains Mono,monospace;font-size:1.1rem;
         font-weight:700;color:#7B9EF5;margin-bottom:4px;'>🌳 AST Explorer</div>
    <div style='font-size:0.75rem;color:#555577;margin-bottom:20px;'>
    Python Code Analysis Toolkit</div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Settings")

    viz_engine = st.selectbox(
        "Visualization Engine",
        ["Graphviz (Static)", "PyVis (Interactive)"],
        index=0,
    )

    graphviz_engine = st.selectbox(
        "Graphviz Layout",
        ["dot", "neato", "circo", "twopi"],
        index=0,
        disabled=(viz_engine != "Graphviz (Static)"),
    )

    max_nodes = st.slider("Max Nodes Rendered", 20, 400, 150, 10)

    show_whitespace = st.toggle("Show Whitespace Tokens", value=False)

    st.markdown("---")
    st.markdown("### 📘 Node Categories")
    st.markdown(get_legend_html(), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem;color:#44446A;line-height:1.7;'>
    <b style='color:#55557A;'>Compilation Stages</b><br>
    1. Source → Tokens (lexical)<br>
    2. Tokens → AST (parse)<br>
    3. AST → Bytecode (compile)<br>
    4. Bytecode → Execution<br>
    <br>
    <b style='color:#55557A;'>Built with</b><br>
    ast · tokenize · graphviz · pyvis · streamlit
    </div>
    """, unsafe_allow_html=True)

# ── Main Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ast-header">
  <h1>🌳 AST Explorer</h1>
  <p>Interactive Python Lexical Analysis &amp; Abstract Syntax Tree Visualizer —
     understand how your code is parsed, token by token, node by node.</p>
</div>
""", unsafe_allow_html=True)

# ── Pipeline Flow ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="pipeline">
  <div class="pipe-step active">① Source Code</div>
  <div class="pipe-arrow">→</div>
  <div class="pipe-step active">② Tokenize</div>
  <div class="pipe-arrow">→</div>
  <div class="pipe-step active">③ Parse AST</div>
  <div class="pipe-arrow">→</div>
  <div class="pipe-step active">④ Visualize</div>
</div>
""", unsafe_allow_html=True)

# ── Main Tabs ──────────────────────────────────────────────────────────────────
tab_main, tab_diff, tab_export = st.tabs(["🔍 Analyze", "⚖️ Compare", "📤 Export"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: MAIN ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_main:
    col_input, col_right = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown('<div class="section-header">① Source Code Input</div>', unsafe_allow_html=True)

        use_sample = st.button("Load Sample Code", key="sample_btn")
        if use_sample:
            st.session_state['code_input'] = SAMPLE_CODE

        code = st.text_area(
            "Paste or type Python code here:",
            value=st.session_state.get('code_input', SAMPLE_CODE),
            height=340,
            key="code_area",
            label_visibility="collapsed",
            placeholder="# Enter Python code…",
        )
        st.session_state['code_input'] = code

        col_a, col_b = st.columns(2)
        with col_a:
            analyze_btn = st.button("▶ Analyze Code", type="primary", use_container_width=True)
        with col_b:
            clear_btn = st.button("✕ Clear", use_container_width=True)
            if clear_btn:
                st.session_state['code_input'] = ''
                st.rerun()

    with col_right:
        st.markdown('<div class="section-header">② Lexical Analysis — Tokens</div>', unsafe_allow_html=True)

        if code.strip():
            tokens, tok_error = tokenize_code(code)

            if tok_error:
                st.markdown(f'<div class="error-box">🔴 {tok_error}</div>', unsafe_allow_html=True)
            else:
                # Stats
                visible_tokens = [t for t in tokens if show_whitespace or t.category not in {'whitespace'}]
                by_cat = {}
                for t in visible_tokens:
                    by_cat[t.category] = by_cat.get(t.category, 0) + 1

                c1, c2, c3, c4 = st.columns(4)
                for col, (label, val) in zip(
                    [c1, c2, c3, c4],
                    [
                        ("Tokens", len(visible_tokens)),
                        ("Keywords", by_cat.get('keyword', 0)),
                        ("Identifiers", by_cat.get('identifier', 0)),
                        ("Literals", by_cat.get('literal_number', 0) + by_cat.get('literal_string', 0)),
                    ]
                ):
                    with col:
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="val">{val}</div>
                            <div class="lbl">{label}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                rows = tokens_to_display(tokens)
                if not show_whitespace:
                    rows = [r for r in rows if r['Category'] not in {'Whitespace', 'Endmarker', 'Encoding'}]

                if rows:
                    df = pd.DataFrame(rows)
                    st.dataframe(
                        df,
                        use_container_width=True,
                        height=240,
                        column_config={
                            'Token Type': st.column_config.TextColumn('Type', width='small'),
                            'Value':      st.column_config.TextColumn('Value', width='medium'),
                            'Category':   st.column_config.TextColumn('Category', width='medium'),
                            'Line':       st.column_config.NumberColumn('Line', width='small'),
                            'Col Start':  st.column_config.NumberColumn('Col↑', width='small'),
                            'Col End':    st.column_config.NumberColumn('Col↓', width='small'),
                        }
                    )
        else:
            st.markdown('<div class="info-box">👆 Enter code on the left to begin analysis.</div>', unsafe_allow_html=True)

    # ── AST Section ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">③ + ④ Abstract Syntax Tree — Parse &amp; Visualize</div>', unsafe_allow_html=True)

    if code.strip():
        tree, parse_error = parse_ast(code)

        if parse_error:
            st.markdown(f'<div class="error-box">🔴 {parse_error}</div>', unsafe_allow_html=True)
        else:
            ast_nodes, ast_edges = ast_to_nodes_edges(tree)

            # AST stats
            node_types = {}
            for n in ast_nodes:
                t = n['type']
                node_types[t] = node_types.get(t, 0) + 1

            ca, cb, cc = st.columns(3)
            with ca:
                st.markdown(f"""<div class="stat-card"><div class="val">{len(ast_nodes)}</div>
                <div class="lbl">AST Nodes</div></div>""", unsafe_allow_html=True)
            with cb:
                st.markdown(f"""<div class="stat-card"><div class="val">{len(ast_edges)}</div>
                <div class="lbl">Edges</div></div>""", unsafe_allow_html=True)
            with cc:
                max_depth = max((n['depth'] for n in ast_nodes), default=0)
                st.markdown(f"""<div class="stat-card"><div class="val">{max_depth}</div>
                <div class="lbl">Tree Depth</div></div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if viz_engine == "Graphviz (Static)":
                with st.spinner("Rendering AST…"):
                    dot = build_graphviz_tree(ast_nodes, ast_edges, max_nodes=max_nodes, engine=graphviz_engine)
                    st.graphviz_chart(dot, use_container_width=True)
                if len(ast_nodes) > max_nodes:
                    st.markdown(f'<div class="info-box">⚡ Showing first {max_nodes} of {len(ast_nodes)} nodes. Increase "Max Nodes" in the sidebar to see more.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Building interactive graph…"):
                    try:
                        html_content = build_pyvis_html(ast_nodes, ast_edges, max_nodes=max_nodes)
                        st.components.v1.html(html_content, height=620, scrolling=True)
                    except Exception as e:
                        st.warning(f"PyVis error: {e}. Falling back to Graphviz.")
                        dot = build_graphviz_tree(ast_nodes, ast_edges, max_nodes=max_nodes)
                        st.graphviz_chart(dot, use_container_width=True)

            # Node type breakdown
            with st.expander("📊 Node Type Breakdown"):
                if node_types:
                    sorted_types = sorted(node_types.items(), key=lambda x: -x[1])
                    df_types = pd.DataFrame(sorted_types, columns=["Node Type", "Count"])
                    c_left, c_right = st.columns([1, 1])
                    with c_left:
                        st.dataframe(df_types, use_container_width=True, height=280)
                    with c_right:
                        st.bar_chart(df_types.set_index("Node Type"), use_container_width=True, color='#5B8DEF')

            # Node details explorer
            with st.expander("🔎 Node Detail Explorer"):
                st.markdown("Select a node type to inspect individual nodes:")
                node_type_options = sorted(set(n['type'] for n in ast_nodes))
                selected_type = st.selectbox("Node Type", node_type_options)
                filtered = [n for n in ast_nodes if n['type'] == selected_type]
                for fn in filtered[:10]:
                    st.json(fn['details'], expanded=False)

        # Store for export tab
        if tree is not None:
            st.session_state['_tree'] = tree
            st.session_state['_code'] = code
    else:
        st.markdown('<div class="info-box">👆 Enter code above to generate the AST.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: DIFF / COMPARE
# ══════════════════════════════════════════════════════════════════════════════
with tab_diff:
    st.markdown('<div class="section-header">Compare Two Code Snippets via AST</div>', unsafe_allow_html=True)

    if st.button("Load Diff Samples"):
        st.session_state['diff_a'] = DIFF_SAMPLE_A
        st.session_state['diff_b'] = DIFF_SAMPLE_B

    col_da, col_db = st.columns(2, gap="large")
    with col_da:
        st.markdown("**Snippet A (Before)**")
        code_a = st.text_area("Code A", value=st.session_state.get('diff_a', ''), height=220,
                              key="diff_a_area", label_visibility="collapsed")
    with col_db:
        st.markdown("**Snippet B (After)**")
        code_b = st.text_area("Code B", value=st.session_state.get('diff_b', ''), height=220,
                              key="diff_b_area", label_visibility="collapsed")

    if st.button("⚖️ Compare ASTs", type="primary"):
        if not code_a.strip() or not code_b.strip():
            st.warning("Please enter code in both panels.")
        else:
            tree_a, err_a = parse_ast(code_a)
            tree_b, err_b = parse_ast(code_b)

            if err_a:
                st.markdown(f'<div class="error-box">🔴 Snippet A: {err_a}</div>', unsafe_allow_html=True)
            elif err_b:
                st.markdown(f'<div class="error-box">🔴 Snippet B: {err_b}</div>', unsafe_allow_html=True)
            else:
                diff = diff_asts(tree_a, tree_b)

                st.markdown("---")
                ca, cb, cc, cd = st.columns(4)
                with ca:
                    st.markdown(f"""<div class="stat-card"><div class="val">{diff['stats']['nodes_before']}</div><div class="lbl">Nodes A</div></div>""", unsafe_allow_html=True)
                with cb:
                    st.markdown(f"""<div class="stat-card"><div class="val">{diff['stats']['nodes_after']}</div><div class="lbl">Nodes B</div></div>""", unsafe_allow_html=True)
                with cc:
                    delta = diff['stats']['delta']
                    sign = '+' if delta >= 0 else ''
                    st.markdown(f"""<div class="stat-card"><div class="val" style="color:{'#5DD890' if delta>=0 else '#F56E6E'}">{sign}{delta}</div><div class="lbl">Node Delta</div></div>""", unsafe_allow_html=True)
                with cd:
                    identical = diff['structurally_identical']
                    st.markdown(f"""<div class="stat-card"><div class="val" style="color:{'#5DD890' if identical else '#F5C87B'}">{'✓' if identical else '✗'}</div><div class="lbl">Identical</div></div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**🟢 Node Types Added**")
                    if diff['added']:
                        for t, cnt in diff['added'].items():
                            st.markdown(f'<div class="diff-added">+ {t} &nbsp;×{cnt}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color:#444466;font-size:0.85rem;">None</div>', unsafe_allow_html=True)

                with c2:
                    st.markdown("**🔴 Node Types Removed**")
                    if diff['removed']:
                        for t, cnt in diff['removed'].items():
                            st.markdown(f'<div class="diff-removed">− {t} &nbsp;×{cnt}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color:#444466;font-size:0.85rem;">None</div>', unsafe_allow_html=True)

                with c3:
                    st.markdown("**🟡 Node Types Changed**")
                    if diff['changed']:
                        for t, info in diff['changed'].items():
                            sign = '+' if info['delta'] >= 0 else ''
                            st.markdown(f'<div class="diff-changed">~ {t}: {info["before"]}→{info["after"]} ({sign}{info["delta"]})</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color:#444466;font-size:0.85rem;">None</div>', unsafe_allow_html=True)

                # Side-by-side AST
                st.markdown("---")
                st.markdown('<div class="section-header">Side-by-Side AST Visualization</div>', unsafe_allow_html=True)
                vcol_a, vcol_b = st.columns(2)
                with vcol_a:
                    st.markdown("**AST — Snippet A**")
                    nodes_a, edges_a = ast_to_nodes_edges(tree_a)
                    dot_a = build_graphviz_tree(nodes_a, edges_a, max_nodes=80)
                    st.graphviz_chart(dot_a, use_container_width=True)
                with vcol_b:
                    st.markdown("**AST — Snippet B**")
                    nodes_b, edges_b = ast_to_nodes_edges(tree_b)
                    dot_b = build_graphviz_tree(nodes_b, edges_b, max_nodes=80)
                    st.graphviz_chart(dot_b, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: EXPORT
# ══════════════════════════════════════════════════════════════════════════════
with tab_export:
    st.markdown('<div class="section-header">Export AST Data</div>', unsafe_allow_html=True)

    tree = st.session_state.get('_tree')
    code_src = st.session_state.get('_code', '')

    if tree is None:
        st.markdown('<div class="info-box">👆 Analyze some code in the "Analyze" tab first.</div>', unsafe_allow_html=True)
    else:
        st.markdown("**Export the full AST as JSON:**")
        json_str = ast_to_json(tree)

        st.download_button(
            label="⬇ Download AST JSON",
            data=json_str,
            file_name="ast_export.json",
            mime="application/json",
            type="primary",
        )

        with st.expander("Preview JSON (first 4000 chars)"):
            st.code(json_str[:4000] + ('\n…' if len(json_str) > 4000 else ''), language='json')

        st.markdown("---")
        st.markdown("**Export token list as CSV:**")
        if code_src.strip():
            tokens, _ = tokenize_code(code_src)
            rows = tokens_to_display(tokens)
            df = pd.DataFrame(rows)
            csv_str = df.to_csv(index=False)
            st.download_button(
                label="⬇ Download Tokens CSV",
                data=csv_str,
                file_name="tokens.csv",
                mime="text/csv",
            )

        st.markdown("---")
        st.markdown("**Compact AST dump (ast.dump):**")
        import ast as _ast
        dump_str = _ast.dump(tree, indent=2)
        st.download_button(
            label="⬇ Download AST Dump (txt)",
            data=dump_str,
            file_name="ast_dump.txt",
            mime="text/plain",
        )
        with st.expander("Preview AST dump"):
            st.code(dump_str[:3000] + ('\n…' if len(dump_str) > 3000 else ''), language='python')
