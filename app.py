import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import random
from PIL import Image

# Load logic gate images
gate_images = {
    "AND": "and.png",
    "OR": "or.png",
    "XOR": "xor.png",
    "NAND": "nand.png",
    "NOR": "nor.png",
    "XNOR": "xnor.png",
    "NOT": "not.png"
}

# Logic Gate Functions
def AND(a, b): return int(a and b)
def OR(a, b): return int(a or b)
def XOR(a, b): return int(a ^ b)
def NAND(a, b): return int(not (a and b))
def NOR(a, b): return int(not (a or b))
def XNOR(a, b): return int(not (a ^ b))
def NOT(a): return int(not a)

gate_functions = {"AND": AND, "OR": OR, "XOR": XOR, "NAND": NAND, "NOR": NOR, "XNOR": XNOR, "NOT": NOT}

# Initialize Session State
if "circuit_graph" not in st.session_state:
    st.session_state.circuit_graph = nx.DiGraph()
if "nodes" not in st.session_state:
    st.session_state.nodes = {}
if "input_values" not in st.session_state:
    st.session_state.input_values = {}

# UI Layout
st.title("🔌 Interactive Logic Circuit Simulator")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("🛠️ Build Your Circuit")
    
    # Select Logic Gate
    selected_gate = st.selectbox("Select Logic Gate", list(gate_functions.keys()))
    add_gate = st.button("➕ Add Gate")

    # Add Inputs
    input_options = [f"Input {i}" for i in range(1, 6)]
    selected_input = st.selectbox("Select Input", input_options)
    add_input = st.button("➕ Add Input")

    # Define Connections
    st.subheader("🔗 Define Connections")
    node1 = st.selectbox("From", list(st.session_state.nodes.keys()), key="node1")
    node2 = st.selectbox("To", list(st.session_state.nodes.keys()), key="node2")
    add_connection = st.button("🔗 Connect Nodes")

    # Clear Circuit
    if st.button("🗑️ Clear Circuit"):
        st.session_state.circuit_graph.clear()
        st.session_state.nodes = {}
        st.session_state.input_values = {}

# Handle Adding Components
if add_gate:
    node_id = f"{selected_gate}_{random.randint(100, 999)}"
    st.session_state.nodes[node_id] = selected_gate
    st.session_state.circuit_graph.add_node(node_id, label=selected_gate)

if add_input:
    node_id = f"{selected_input}_{random.randint(100, 999)}"
    st.session_state.nodes[node_id] = "Input"
    st.session_state.circuit_graph.add_node(node_id, label="Input")
    st.session_state.input_values[node_id] = 0  # Default input is 0

if add_connection:
    if node1 != node2:
        st.session_state.circuit_graph.add_edge(node1, node2)

# Sidebar Input Controls
st.sidebar.header("🎛️ Input Controls")
for input_node in [node for node in st.session_state.nodes if "Input" in node]:
    st.session_state.input_values[input_node] = st.sidebar.checkbox(input_node, value=False)

# **Logic Propagation Function**
def compute_output(graph, inputs):
    node_values = inputs.copy()

    for node in nx.topological_sort(graph):
        if node in node_values:
            continue  # Skip inputs

        predecessors = list(graph.predecessors(node))
        gate_type = st.session_state.nodes[node]

        if gate_type == "NOT" and len(predecessors) == 1:
            node_values[node] = NOT(node_values[predecessors[0]])
        elif len(predecessors) == 2:
            a, b = node_values[predecessors[0]], node_values[predecessors[1]]
            node_values[node] = gate_functions[gate_type](a, b)
        else:
            node_values[node] = 0  # Default value if invalid

    return node_values

# Compute Circuit Output
output_values = compute_output(st.session_state.circuit_graph, st.session_state.input_values)

# **Graph Visualization with Gate Images**
with col2:
    st.header("📡 Circuit Diagram")

    pos = nx.spring_layout(st.session_state.circuit_graph, seed=42)
    edge_x, edge_y, node_x, node_y, node_labels, node_colors = [], [], [], [], [], []

    # **Edges Styling**
    for edge in st.session_state.circuit_graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # **Nodes Styling**
    for node in st.session_state.circuit_graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_labels.append(f"{node} ({output_values[node]})")
        node_colors.append("#4CAF50" if output_values[node] == 1 else "#FF5252")  # Green for 1, Red for 0

    # **Create Figure**
    fig = go.Figure()

    # **Edges**
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y, mode='lines',
        line=dict(color='black', width=2), hoverinfo='none'
    ))

    # **Nodes**
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        marker=dict(size=30, color=node_colors, line=dict(width=2, color="black")),
        text=node_labels, textposition="top center"
    ))

    fig.update_layout(
        showlegend=False, height=500,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white", plot_bgcolor="white"
    )

    st.plotly_chart(fig)

    # **Display Gate Images**
    for node in st.session_state.nodes:
        if st.session_state.nodes[node] in gate_images:
            st.image(gate_images[st.session_state.nodes[node]], caption=f"{node}")

# **Display Circuit Output**
st.subheader("🖥️ Circuit Output")
st.write(output_values)
