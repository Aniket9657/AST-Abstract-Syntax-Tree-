"""
AST Visualizer Module
Renders AST nodes and edges as visual trees using graphviz and pyvis.
"""

import graphviz
from typing import List, Dict, Optional
import html


# Color palette per node category
CATEGORY_COLORS = {
    'statement':     {'bg': '#2D4B8E', 'border': '#5B8DEF', 'font': '#FFFFFF'},
    'control':       {'bg': '#7B2D8E', 'border': '#C45CF5', 'font': '#FFFFFF'},
    'expression':    {'bg': '#1A6B4A', 'border': '#3DD68C', 'font': '#FFFFFF'},
    'comprehension': {'bg': '#5C4A1A', 'border': '#F5C542', 'font': '#FFFFFF'},
    'literal':       {'bg': '#8E2D2D', 'border': '#F56E6E', 'font': '#FFFFFF'},
    'name':          {'bg': '#1A4A6B', 'border': '#42A5F5', 'font': '#FFFFFF'},
    'operator':      {'bg': '#4A4A4A', 'border': '#AAAAAA', 'font': '#FFFFFF'},
    'other':         {'bg': '#2A2A3E', 'border': '#6666AA', 'font': '#CCCCCC'},
}


def build_graphviz_tree(
    nodes: List[Dict],
    edges: List[Dict],
    max_nodes: int = 150,
    engine: str = 'dot'
) -> graphviz.Digraph:
    """
    Build a Graphviz Digraph from nodes and edges.
    Returns a graphviz.Digraph object.
    """
    dot = graphviz.Digraph(
        name='AST',
        graph_attr={
            'bgcolor': '#0D0D1A',
            'rankdir': 'TB',
            'splines': 'curved',
            'nodesep': '0.4',
            'ranksep': '0.6',
            'fontname': 'Courier New',
            'pad': '0.5',
        },
        node_attr={
            'shape': 'box',
            'style': 'filled,rounded',
            'fontname': 'Courier New',
            'fontsize': '10',
            'margin': '0.15,0.08',
            'penwidth': '1.5',
        },
        edge_attr={
            'color': '#444466',
            'arrowsize': '0.6',
            'penwidth': '1.2',
        }
    )

    # Limit nodes for performance
    visible_nodes = nodes[:max_nodes]
    visible_ids = {n['id'] for n in visible_nodes}

    for node in visible_nodes:
        cat = node.get('category', 'other')
        colors = CATEGORY_COLORS.get(cat, CATEGORY_COLORS['other'])

        label = html.escape(node['label'])
        dot.node(
            node['id'],
            label=label,
            fillcolor=colors['bg'],
            color=colors['border'],
            fontcolor=colors['font'],
        )

    for edge in edges:
        if edge['from'] in visible_ids and edge['to'] in visible_ids:
            dot.edge(edge['from'], edge['to'])

    if len(nodes) > max_nodes:
        dot.node(
            '_overflow',
            label=f'… +{len(nodes) - max_nodes} more nodes',
            shape='note',
            fillcolor='#1A1A2E',
            color='#666688',
            fontcolor='#999999',
        )

    return dot


def build_pyvis_html(
    nodes: List[Dict],
    edges: List[Dict],
    max_nodes: int = 300,
) -> str:
    """
    Build an interactive pyvis network HTML string.
    Falls back to a simple SVG message if pyvis isn't available.
    """
    try:
        from pyvis.network import Network
    except ImportError:
        return "<p>pyvis not installed. Using Graphviz view instead.</p>"

    net = Network(
        height='600px',
        width='100%',
        directed=True,
        bgcolor='#0D0D1A',
        font_color='#FFFFFF',
    )
    net.set_options("""
    {
      "nodes": {
        "font": {"size": 11, "face": "Courier New"},
        "borderWidth": 2,
        "shadow": {"enabled": true, "color": "rgba(0,0,0,0.5)", "size": 8}
      },
      "edges": {
        "color": {"color": "#444466", "highlight": "#8888FF"},
        "arrows": {"to": {"enabled": true, "scaleFactor": 0.6}},
        "smooth": {"type": "cubicBezier"}
      },
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "UD",
          "sortMethod": "directed",
          "nodeSpacing": 120,
          "levelSeparation": 80
        }
      },
      "physics": {"enabled": false},
      "interaction": {
        "hover": true,
        "tooltipDelay": 200,
        "navigationButtons": true,
        "keyboard": {"enabled": true}
      }
    }
    """)

    visible_nodes = nodes[:max_nodes]
    visible_ids = {n['id'] for n in visible_nodes}

    for node in visible_nodes:
        cat = node.get('category', 'other')
        colors = CATEGORY_COLORS.get(cat, CATEGORY_COLORS['other'])

        detail_lines = '\n'.join(
            f"{k}: {v}" for k, v in node.get('details', {}).items()
        )
        tooltip = f"{node['type']}\n{detail_lines}"

        net.add_node(
            node['id'],
            label=node['label'],
            title=tooltip,
            color={
                'background': colors['bg'],
                'border': colors['border'],
                'highlight': {'background': colors['border'], 'border': '#FFFFFF'},
            },
            font={'color': colors['font']},
            shape='box',
        )

    for edge in edges:
        if edge['from'] in visible_ids and edge['to'] in visible_ids:
            net.add_edge(edge['from'], edge['to'])

    return net.generate_html()


def get_legend_html() -> str:
    """Generate an HTML legend for node categories."""
    items = []
    labels = {
        'statement':     'Statement / Definition',
        'control':       'Control Flow',
        'expression':    'Expression',
        'comprehension': 'Comprehension',
        'literal':       'Literal / Value',
        'name':          'Name / Identifier',
        'operator':      'Operator',
        'other':         'Other',
    }
    for cat, label in labels.items():
        c = CATEGORY_COLORS[cat]
        items.append(
            f'<span style="display:inline-flex;align-items:center;margin:4px 8px;">'
            f'<span style="width:14px;height:14px;border-radius:3px;'
            f'background:{c["bg"]};border:2px solid {c["border"]};'
            f'display:inline-block;margin-right:6px;"></span>'
            f'<span style="font-size:12px;color:#CCCCCC;">{label}</span>'
            f'</span>'
        )
    return '<div style="display:flex;flex-wrap:wrap;gap:2px;">' + ''.join(items) + '</div>'
