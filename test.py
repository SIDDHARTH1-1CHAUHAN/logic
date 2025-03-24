import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import random
from PIL import Image

# Extended component library
component_data = {
    # Combinational
    "AND": {"symbol": "&", "shape": "square", "inputs": 2},
    "OR": {"symbol": "≥1", "shape": "square", "inputs": 2},
    "XOR": {"symbol": "=1", "shape": "square", "inputs": 2},
    "NOT": {"symbol": "△", "shape": "triangle-right", "inputs": 1},
    
    # Sequential
    "DFF": {"symbol": "D", "shape": "hexagon", "inputs": 2},
    "JKFF": {"symbol": "JK", "shape": "hexagon", "inputs": 3},
    "COUNTER": {"symbol": "⏲", "shape": "circle", "inputs": 1},
    
    # I/O
    "INPUT": {"symbol": "◁", "shape": "triangle-right", "inputs": 0},
    "OUTPUT": {"symbol": "▷", "shape": "triangle-left", "inputs": 1},
    "7SEG": {"symbol": "7S", "shape": "square", "inputs": 4}
}

# Sequential components classes
class DFlipFlop:
    def __init__(self):
        self.state = 0
        self.prev_clk = 0
    
    def update(self, D, clk):
        if clk > self.prev_clk and clk == 1:
            self.state = D
        self.prev_clk = clk
        return self.state

class Counter:
    def __init__(self):
        self.count = 0
    
    def update(self, clk):
        if clk:
            self.count = (self.count + 1) % 16
        return bin(self.count)[2:].zfill(4)

# Initialize session state
if "components" not in st.session_state:
    st.session_state.components = {
        "seq": {},
        "values": {},
        "clock": 0
    }

# Circuit simulation logic
def compute_circuit():
    graph = st.session_state.circuit_graph
    values = st.session_state.components["values"].copy()
    
    for node in nx.topological_sort(graph):
        if node in values: continue
        
        comp_type = st.session_state.nodes[node]
        preds = list(graph.predecessors(node))
        
        # Handle sequential components
        if comp_type in ["DFF", "JKFF", "COUNTER"]:
            if comp_type == "DFF" and len(preds) >= 2:
                D, clk = values[preds[0]], values[preds[1]]
                values[node] = st.session_state.components["seq"][node].update(D, clk)
        
        # Handle combinational logic
        else:
            inputs = [values[p] for p in preds]
            if comp_type == "AND": values[node] = int(all(inputs))
            elif comp_type == "OR": values[node] = int(any(inputs))
            elif comp_type == "NOT": values[node] = int(not inputs[0])
    
    st.session_state.components["values"] = values

# Enhanced visualization
def draw_circuit():
    graph = st.session_state.circuit_graph
    pos = nx.spring_layout(graph, seed=42)
    
    fig = go.Figure()
    
    # Edges
    edge_x, edge_y = [], []
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(color='black', width=2),
        hoverinfo='none'
    ))
    
    # Nodes
    node_shapes = []
    for node in graph.nodes():
        comp_type = st.session_state.nodes[node]
        info = component_data.get(comp_type, {})
        
        fig.add_trace(go.Scatter(
            x=[pos[node][0]],
            y=[pos[node][1]],
            mode='markers+text',
            marker=dict(
                size=40,
                symbol=info.get("shape", "circle"),
                color='lightblue',
                line=dict(width=2, color='darkblue')
            ),
            text=info.get("symbol", "?"),
            textfont=dict(size=20, color='black'),
            name=node
        ))
    
    fig.update_layout(
        showlegend=False,
        height=600,
        margin=dict(l=20, r=20, b=20, t=40),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig)

# UI Components
st.title("🔌 Advanced Circuit Simulator")
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Circuit Design")
    
    # Component selection
    comp_type = st.selectbox("Component Type", ["Combinational", "Sequential", "I/O"])
    component = st.selectbox("Select Component", {
        "Combinational": ["AND", "OR", "NOT", "XOR"],
        "Sequential": ["DFF", "JKFF", "COUNTER"],
        "I/O": ["INPUT", "OUTPUT", "7SEG"]
    }[comp_type])
    
    if st.button("Add Component"):
        node_id = f"{component}_{random.randint(1000,9999)}"
        st.session_state.nodes[node_id] = component
        st.session_state.circuit_graph.add_node(node_id)
        
        if component in ["DFF", "JKFF", "COUNTER"]:
            st.session_state.components["seq"][node_id] = eval({
                "DFF": "DFlipFlop",
                "COUNTER": "Counter"
            }.get(component, "DFlipFlop"))()

    # Connections
    st.subheader("Wiring")
    nodes = list(st.session_state.nodes.keys())
    source = st.selectbox("From", nodes)
    targets = st.multiselect("To", nodes)
    if st.button("Connect"):
        for target in targets:
            st.session_state.circuit_graph.add_edge(source, target)
    
    # Clock control
    st.subheader("Simulation")
    if st.button("⏲ Clock Cycle"):
        st.session_state.components["clock"] += 1
        compute_circuit()

with col2:
    st.header("Visualization")
    draw_circuit()
    
    # Display values
    st.subheader("Measurements")
    for node, value in st.session_state.components["values"].items():
        st.write(f"{node}: {value}")

# Input controls
st.sidebar.header("Input Management")
for node in st.session_state.nodes:
    if st.session_state.nodes[node] == "INPUT":
        st.session_state.components["values"][node] = st.sidebar.checkbox(node)