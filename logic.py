import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from PIL import Image
import base64
import serial
import time
import os
import networkx as nx
import random

# Set page configuration
st.set_page_config(
    page_title="Digital Logic Lab Simulator",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 4px 4px 0px 0px; padding: 10px 16px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #4e8df5; color: white; }
    .experiment-card { background-color: #f9f9f9; border-radius: 10px; padding: 20px; margin-bottom: 20px; border-left: 5px solid #4e8df5; }
    .output-card { background-color: #f0f7ff; border-radius: 10px; padding: 15px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# 🔌 Available COM ports (for hardware mode)
available_ports = ['COM3', 'COM4', 'COM5', 'COM6']
selected_port = st.sidebar.selectbox("Select COM Port:", available_ports)

# 📡 Serial Communication Setup (for hardware mode)
ser = None
try:
    ser = serial.Serial(selected_port, 9600, timeout=1)
    time.sleep(2)
    st.sidebar.success(f"Connected to {selected_port}")
except Exception as e:
    st.sidebar.error(f"Error connecting to Arduino: {e}")

# Session State Initialization
if "history_data" not in st.session_state:
    st.session_state.history_data = []

if "waveform_data" not in st.session_state:
    st.session_state.waveform_data = {"Time": [], "Input 1": [], "Input 2": [], "Output": []}

if "current_experiment" not in st.session_state:
    st.session_state.current_experiment = "Basic Logic Gates"

# 🎛️ Logic Gate Functions
def AND_gate(a, b): return a and b
def OR_gate(a, b): return a or b
def XOR_gate(a, b): return a ^ b
def NAND_gate(a, b): return not (a and b)
def NOR_gate(a, b): return not (a or b)
def XNOR_gate(a, b): return not (a ^ b)
def NOT_gate(a): return not a

gate_functions = {
    "AND": AND_gate, "OR": OR_gate, "XOR": XOR_gate,
    "NAND": NAND_gate, "NOR": NOR_gate, "XNOR": XNOR_gate, "NOT": NOT_gate
}

# 📝 Gate Descriptions
gate_descriptions = {
    "AND": "Outputs **1** if **both inputs** are 1.",
    "OR": "Outputs **1** if **at least one input** is 1.",
    "XOR": "Outputs **1** if the inputs are **different**.",
    "NAND": "Outputs **0** only if **both inputs** are 1.",
    "NOR": "Outputs **1** only if **both inputs** are 0.",
    "XNOR": "Outputs **1** if the inputs are **the same**.",
    "NOT": "Outputs the **inverse** of the input."
}

# Application Title
st.title("🔌 Digital Logic Lab Simulator")

# Main Experiment Categories
experiment_categories = [
    "Basic Logic Gates",
    "Combinational Circuits",
    "Sequential Circuits",
    "Timers and Multivibrators",
    "Counters and Registers",
    "Decoders and Display Circuits"
]

# All experiments
all_experiments = {
    "Basic Logic Gates": [
        "AND Gate", "OR Gate", "NOT Gate", "NAND Gate", "NOR Gate", "XOR Gate", "XNOR Gate"
    ],
    "Combinational Circuits": [
        "Half Adder", "Full Adder", "Half Subtractor", "Full Subtractor", "Multiplexer (MUX)", "Demultiplexer (DEMUX)",
        "Magnitude Comparator", "Binary Addition", "Address Decoder"
    ],
    "Sequential Circuits": [
        "SR Latch using NAND Gates", "SR Latch using NOR Gates", "D Flip-Flop", "Master-Slave JK Flip-Flop", "Shift Register"
    ],
    "Timers and Multivibrators": [
        "Astable Multivibrator using 555 IC", "Monostable Multivibrator using 555 IC", "Bistable Multivibrator using Timer IC",
        "Monostable Multivibrator using Digital IC", "Monostable Multivibrator with Retriggable using Digital IC"
    ],
    "Counters and Registers": [
        "Binary Up/Down Counter", "Decade or BCD Up/Down Counter", "Frequency Divider/Counter"
    ],
    "Decoders and Display Circuits": [
        "BCD Decoder with 7-Segment Display"
    ]
}

# Sidebar Navigation
st.sidebar.title("🧪 Experiment Navigation")
selected_category = st.sidebar.selectbox("Select Experiment Category:", experiment_categories)
selected_experiment = st.sidebar.selectbox("Select Experiment:", all_experiments[selected_category])
st.session_state.current_experiment = selected_experiment

# Mode Selection
mode = st.sidebar.radio("Mode Selection", ["🔴 Hardware Mode", "🟢 Simulation Mode", "🎓 Learning Mode"])

# 📈 Data Logging Function
def log_data(inputs, outputs, experiment_name):
    """Logs experiment data dynamically."""
    entry = {**inputs, **outputs, "Experiment": experiment_name, "Timestamp": pd.Timestamp.now()}
    st.session_state.history_data.append(entry)
    
    # Update waveform data
    if len(inputs) >= 2 and len(outputs) >= 1:
        st.session_state.waveform_data["Time"].append(len(st.session_state.waveform_data["Time"]))
        st.session_state.waveform_data["Input 1"].append(list(inputs.values())[0])
        st.session_state.waveform_data["Input 2"].append(list(inputs.values())[1] if len(inputs) > 1 else 0)
        st.session_state.waveform_data["Output"].append(list(outputs.values())[0])

# 🌊 Interactive Timing Diagram
def plot_logic_wave():
    """Generate an interactive timing diagram with Plotly."""
    fig = go.Figure()
    time_steps = st.session_state.waveform_data["Time"]

    if len(time_steps) > 0:
        fig.add_trace(go.Scatter(x=time_steps, y=st.session_state.waveform_data["Input 1"], 
                               mode="lines+markers", name="Input 1", line=dict(shape="hv", width=2)))
        fig.add_trace(go.Scatter(x=time_steps, y=st.session_state.waveform_data["Input 2"], 
                               mode="lines+markers", name="Input 2", line=dict(shape="hv", width=2)))
        fig.add_trace(go.Scatter(x=time_steps, y=st.session_state.waveform_data["Output"], 
                               mode="lines+markers", name="Output", line=dict(shape="hv", width=3, dash="dash")))

        fig.update_layout(
            title=f"⏳ Timing Diagram - {selected_experiment}",
            xaxis_title="Time Steps",
            yaxis_title="Logic State (0/1)",
            yaxis=dict(tickmode="array", tickvals=[0, 1]),
            height=300,
            template="plotly_white"
        )

    return fig

# Logic Gate Simulator Function
def basic_logic_gate_simulator(gate_name):
    st.write(f"### {gate_name}")
    st.info(gate_descriptions.get(gate_name.split()[0], ""))
    
    # Display gate diagram
    logic_image_path = f"{gate_name.split()[0].lower()}.png"
    ic_image_path = f"images/{gate_name.split()[0].lower()}_ic.png"

    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists(logic_image_path):
            st.image(logic_image_path, caption="Logic Gate Diagram")
        else:
            st.warning("⚠️ Logic gate diagram not found.")
            
    with col2:
        if os.path.exists(ic_image_path):
            st.image(ic_image_path, caption="IC Diagram")
        else:
            st.warning("⚠️ IC diagram not found.")
    
    # Truth Table
    st.write("### Truth Table")
    input_names = ["A", "B"] if gate_name != "NOT Gate" else ["A"]
    output_name = "Y"
    
    truth_table_data = []
    if gate_name != "NOT Gate":
        for a in [0, 1]:
            for b in [0, 1]:
                result = gate_functions[gate_name.split()[0]](a, b)
                truth_table_data.append([a, b, result])
    else:
        for a in [0, 1]:
            result = gate_functions[gate_name.split()[0]](a)
            truth_table_data.append([a, result])
    
    truth_df = pd.DataFrame(truth_table_data, columns=input_names + [output_name])
    st.table(truth_df)
    
    # Interactive Simulation
    st.write("### Interactive Simulation")
    if mode == "🟢 Simulation Mode":
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            if gate_name != "NOT Gate":
                in1 = st.toggle("Input A", value=False)
                in2 = st.toggle("Input B", value=False)
                result = gate_functions[gate_name.split()[0]](int(in1), int(in2))
                inputs = {"Input A": int(in1), "Input B": int(in2)}
            else:
                in1 = st.toggle("Input A", value=False)
                result = gate_functions[gate_name.split()[0]](int(in1))
                inputs = {"Input A": int(in1)}
                
            st.metric("Output Y", result)
            outputs = {"Output": result}
            log_data(inputs, outputs, gate_name)
            
        with sim_col2:
            st.plotly_chart(plot_logic_wave(), use_container_width=True)
            
    elif mode == "🔴 Hardware Mode":
        st.write("Connect the appropriate IC and pins as shown in the diagram")
        start_hardware = st.button("Start Hardware Test")
        
        if start_hardware and ser:
            st.write("Reading from hardware...")
            # Placeholder for hardware communication
            # In a real implementation, this would send commands to Arduino
            # and read back the results
            
    elif mode == "🎓 Learning Mode":
        st.write("### How This Gate Works")
        
        if gate_name == "AND Gate":
            st.markdown("""
            The AND gate is a basic digital logic gate that implements logical conjunction.
            - Output is HIGH (1) only when all inputs are HIGH (1)
            - It's like a series connection of switches - all must be ON for the circuit to work
            - Used in systems that require all conditions to be met
            """)
        elif gate_name == "OR Gate":
            st.markdown("""
            The OR gate implements logical disjunction.
            - Output is HIGH (1) when at least one input is HIGH (1)
            - It's like a parallel connection of switches - if any is ON, the circuit works
            - Used when you need to detect if any condition is true
            """)
        # Add similar explanations for other gates

# Run the selected experiment
if selected_experiment in all_experiments["Basic Logic Gates"]:
    basic_logic_gate_simulator(selected_experiment)

# Combinational Circuit Functions
import streamlit as st
import pandas as pd

# Assuming XOR_gate and AND_gate are defined elsewhere
def XOR_gate(a, b):
    return a ^ b

def AND_gate(a, b):
    return a & b

def half_adder_simulator():
    st.write("### Half Adder Circuit")
    st.info("A half adder adds two binary digits and produces a sum and carry output.")
    
    # Display the circuit diagram image
    st.write("#### Circuit Diagram")
    st.image("half_adder_diagram.png", caption="Half Adder Circuit Diagram", use_column_width=True)
    
    # Truth Table
    st.write("### Truth Table")
    truth_table_data = []
    for a in [0, 1]:
        for b in [0, 1]:
            sum_bit = XOR_gate(a, b)
            carry = AND_gate(a, b)
            truth_table_data.append([a, b, sum_bit, carry])
    
    truth_df = pd.DataFrame(truth_table_data, columns=["A", "B", "Sum", "Carry"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            in1 = st.toggle("Input A", value=False)
            in2 = st.toggle("Input B", value=False)
            
            sum_result = XOR_gate(int(in1), int(in2))
            carry_result = AND_gate(int(in1), int(in2))
            
            st.metric("Sum", sum_result)
            st.metric("Carry", carry_result)
            
            inputs = {"Input A": int(in1), "Input B": int(in2)}
            outputs = {"Sum": sum_result, "Carry": carry_result}
            log_data(inputs, outputs, "Half Adder")
            
        with sim_col2:
            # Display the implementation diagram image
            st.write("#### Half Adder Implementation")
            st.image("half_adder_diagram.png", caption="Half Adder Implementation", use_column_width=True)


import streamlit as st
import pandas as pd

# Assuming XOR_gate, AND_gate, and OR_gate are defined elsewhere
def XOR_gate(a, b):
    return a ^ b

def AND_gate(a, b):
    return a & b

def OR_gate(a, b):
    return a | b

def full_adder_simulator():
    st.write("### Full Adder Circuit")
    st.info("A full adder adds three binary digits (including a carry-in) and produces a sum and carry output.")
    
    # Display the circuit diagram image
    st.write("#### Circuit Diagram")
    st.image("full_adder_circuit.jpg", caption="Full Adder Circuit Diagram",use_column_width=True)  # Adjust width as needed
    
    # Truth Table
    st.write("### Truth Table")
    truth_table_data = []
    for a in [0, 1]:
        for b in [0, 1]:
            for c_in in [0, 1]:
                # First half adder
                sum1 = XOR_gate(a, b)
                carry1 = AND_gate(a, b)
                
                # Second half adder
                sum_final = XOR_gate(sum1, c_in)
                carry2 = AND_gate(sum1, c_in)
                
                # Final carry
                carry_final = OR_gate(carry1, carry2)
                
                truth_table_data.append([a, b, c_in, sum_final, carry_final])
    
    truth_df = pd.DataFrame(truth_table_data, columns=["A", "B", "Cin", "Sum", "Cout"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            in1 = st.toggle("Input A", value=False)
            in2 = st.toggle("Input B", value=False)
            c_in = st.toggle("Carry In", value=False)
            
            # Calculate using the same logic as for the truth table
            sum1 = XOR_gate(int(in1), int(in2))
            carry1 = AND_gate(int(in1), int(in2))
            
            sum_final = XOR_gate(sum1, int(c_in))
            carry2 = AND_gate(sum1, int(c_in))
            
            carry_final = OR_gate(carry1, carry2)
            
            st.metric("Sum", sum_final)
            st.metric("Carry Out", carry_final)
            
            inputs = {"Input A": int(in1), "Input B": int(in2), "Carry In": int(c_in)}
            outputs = {"Sum": sum_final, "Carry Out": carry_final}
            log_data(inputs, outputs, "Full Adder")
            
        with sim_col2:
            # Display the implementation diagram image
            st.write("#### Full Adder Implementation")
            st.image("full_adder_circuit.jpg", caption="Full Adder Implementation", use_column_width=True)  # Adjust width as needed

import streamlit as st
import pandas as pd

# Assuming XOR_gate, AND_gate, and NOT_gate are defined elsewhere
def XOR_gate(a, b):
    return a ^ b

def AND_gate(a, b):
    return a & b

def NOT_gate(a):
    return 1 - a

def half_subtractor_simulator():
    st.write("### Half Subtractor Circuit")
    st.info("A half subtractor subtracts two binary digits and produces a difference and borrow output.")
    
    # Display the circuit diagram image
    st.write("#### Circuit Diagram")
    st.image("half_subtractor_diagram.png", caption="Half Subtractor Circuit Diagram", use_column_width=True)
    
    # Truth Table
    st.write("### Truth Table")
    truth_table_data = []
    for a in [0, 1]:
        for b in [0, 1]:
            difference = XOR_gate(a, b)
            borrow = AND_gate(NOT_gate(a), b)
            truth_table_data.append([a, b, difference, borrow])
    
    truth_df = pd.DataFrame(truth_table_data, columns=["A", "B", "Difference", "Borrow"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            in1 = st.toggle("Input A", value=False)
            in2 = st.toggle("Input B", value=False)
            
            difference = XOR_gate(int(in1), int(in2))
            borrow = AND_gate(NOT_gate(int(in1)), int(in2))
            
            st.metric("Difference", difference)
            st.metric("Borrow", borrow)
            
            inputs = {"Input A": int(in1), "Input B": int(in2)}
            outputs = {"Difference": difference, "Borrow": borrow}
            log_data(inputs, outputs, "Half Subtractor")
            
        with sim_col2:
            # Display the implementation diagram image
            st.write("#### Half Subtractor Implementation")
            st.image("half_subtractor_diagram.png", caption="Half Subtractor Implementation", use_column_width=True)



import streamlit as st
import pandas as pd

# Assuming XOR_gate, AND_gate, OR_gate, and NOT_gate are defined elsewhere
def XOR_gate(a, b):
    return a ^ b

def AND_gate(a, b):
    return a & b

def OR_gate(a, b):
    return a | b

def NOT_gate(a):
    return 1 - a

def full_subtractor_simulator():
    st.write("### Full Subtractor Circuit")
    st.info("A full subtractor subtracts three binary digits (including a borrow-in) and produces a difference and borrow output.")
    
    # Display the circuit diagram image
    st.write("#### Circuit Diagram")
    st.image("full_subtractor_diagram.png", caption="Full Subtractor Circuit Diagram", use_column_width=True)
    
    # Truth Table
    st.write("### Truth Table")
    truth_table_data = []
    for a in [0, 1]:
        for b in [0, 1]:
            for borrow_in in [0, 1]:
                difference = XOR_gate(XOR_gate(a, b), borrow_in)
                borrow = OR_gate(AND_gate(NOT_gate(a), b), AND_gate(NOT_gate(XOR_gate(a, b)), borrow_in))
                truth_table_data.append([a, b, borrow_in, difference, borrow])
    
    truth_df = pd.DataFrame(truth_table_data, columns=["A", "B", "Borrow In", "Difference", "Borrow Out"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            in1 = st.toggle("Input A", value=False)
            in2 = st.toggle("Input B", value=False)
            borrow_in = st.toggle("Borrow In", value=False)
            
            difference = XOR_gate(XOR_gate(int(in1), int(in2)), int(borrow_in))
            borrow = OR_gate(AND_gate(NOT_gate(int(in1)), int(in2)), AND_gate(NOT_gate(XOR_gate(int(in1), int(in2))), int(borrow_in)))
            
            st.metric("Difference", difference)
            st.metric("Borrow Out", borrow)
            
            inputs = {"Input A": int(in1), "Input B": int(in2), "Borrow In": int(borrow_in)}
            outputs = {"Difference": difference, "Borrow Out": borrow}
            log_data(inputs, outputs, "Full Subtractor")
            
        with sim_col2:
            # Display the implementation diagram image
            st.write("#### Full Subtractor Implementation")
            st.image("full_subtractor_diagram.png", caption="Full Subtractor Implementation", use_column_width=True)

def multiplexer_simulator():
    st.write("### Multiplexer (MUX) Circuit")
    st.info("A multiplexer selects one of many input signals and forwards it to a single output line based on a select signal.")
    
    # Display the circuit diagram image
    st.write("#### Circuit Diagram")
    st.image("multiplexer_curcuit.jpg", caption="Multiplexer Circuit Diagram", use_column_width=True)
    
    # Truth Table for a 2:1 MUX
    st.write("### Truth Table (2:1 MUX)")
    truth_table_data = []
    for s in [0, 1]:
        for i0 in [0, 1]:
            for i1 in [0, 1]:
                output = i0 if s == 0 else i1
                truth_table_data.append([s, i0, i1, output])
    
    truth_df = pd.DataFrame(truth_table_data, columns=["Select (S)", "Input 0 (I0)", "Input 1 (I1)", "Output"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            s = st.toggle("Select (S)", value=False)
            i0 = st.toggle("Input 0 (I0)", value=False)
            i1 = st.toggle("Input 1 (I1)", value=False)
            
            output = i0 if not s else i1
            
            st.metric("Output", output)
            
            inputs = {"Select (S)": int(s), "Input 0 (I0)": int(i0), "Input 1 (I1)": int(i1)}
            outputs = {"Output": output}
            log_data(inputs, outputs, "Multiplexer")
            
        with sim_col2:
            # Display the implementation diagram image
            st.write("#### Multiplexer Implementation")
            st.image("multiplexer_curcuit.jpg", caption="Multiplexer Implementation", use_column_width=True)

def demultiplexer_simulator():
    st.write("### Demultiplexer (DEMUX) Circuit")
    st.info("A demultiplexer takes a single input and routes it to one of many outputs based on a select signal.")
    
    # Display the circuit diagram image
    st.write("#### Circuit Diagram")
    st.image("demultiplexer_curcuit.jpg", caption="Demultiplexer Circuit Diagram", use_column_width=True)
    
    # Truth Table for a 1:2 DEMUX
    st.write("### Truth Table (1:2 DEMUX)")
    truth_table_data = []
    for s in [0, 1]:
        for i in [0, 1]:
            output0 = i if s == 0 else 0
            output1 = i if s == 1 else 0
            truth_table_data.append([s, i, output0, output1])
    
    truth_df = pd.DataFrame(truth_table_data, columns=["Select (S)", "Input (I)", "Output 0 (O0)", "Output 1 (O1)"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            s = st.toggle("Select (S)", value=False)
            i = st.toggle("Input (I)", value=False)
            
            output0 = i if not s else 0
            output1 = i if s else 0
            
            st.metric("Output 0 (O0)", output0)
            st.metric("Output 1 (O1)", output1)
            
            inputs = {"Select (S)": int(s), "Input (I)": int(i)}
            outputs = {"Output 0 (O0)": output0, "Output 1 (O1)": output1}
            log_data(inputs, outputs, "Demultiplexer")
            
        with sim_col2:
            # Display the implementation diagram image
            st.write("#### Demultiplexer Implementation")
            st.image("demultiplexer_curcuit.jpg", caption="Demultiplexer Implementation", use_column_width=True)
            
def magnitude_comparator_simulator():
    st.write("### Magnitude Comparator Circuit")
    st.info("A magnitude comparator compares two binary numbers and determines if one is greater than, equal to, or less than the other.")
    
    # Display the circuit diagram image
    st.write("#### Circuit Diagram")
    st.image("magnitude_comparator.gif", caption="Magnitude Comparator Circuit Diagram", use_column_width=True)
    
    # Truth Table for a 2-bit comparator
    st.write("### Truth Table (2-bit Comparator)")
    truth_table_data = []
    for a in [0, 1]:
        for b in [0, 1]:
            greater = 1 if a > b else 0
            equal = 1 if a == b else 0
            less = 1 if a < b else 0
            truth_table_data.append([a, b, greater, equal, less])
    
    truth_df = pd.DataFrame(truth_table_data, columns=["A", "B", "A > B", "A == B", "A < B"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            a = st.toggle("Input A", value=False)
            b = st.toggle("Input B", value=False)
            
            greater = 1 if a > b else 0
            equal = 1 if a == b else 0
            less = 1 if a < b else 0
            
            st.metric("A > B", greater)
            st.metric("A == B", equal)
            st.metric("A < B", less)
            
            inputs = {"Input A": int(a), "Input B": int(b)}
            outputs = {"A > B": greater, "A == B": equal, "A < B": less}
            log_data(inputs, outputs, "Magnitude Comparator")
            
        with sim_col2:
            # Display the implementation diagram image
            st.write("#### Magnitude Comparator Implementation")
            st.image("magnitude_comparator.gif", caption="Magnitude Comparator Implementation", use_column_width=True)
            
def binary_addition_simulator():
    st.write("### Binary Addition Circuit")
    st.info("A binary addition circuit adds two binary numbers and produces a sum and carry output.")
    
    # Display the circuit diagram image
    st.write("#### Circuit Diagram")
    st.image("binary_adder.jpg", caption="Binary Addition Circuit Diagram", use_column_width=True)
    
    # Truth Table for a 1-bit adder
    st.write("### Truth Table (1-bit Adder)")
    truth_table_data = []
    for a in [0, 1]:
        for b in [0, 1]:
            sum_bit = XOR_gate(a, b)
            carry = AND_gate(a, b)
            truth_table_data.append([a, b, sum_bit, carry])
    
    truth_df = pd.DataFrame(truth_table_data, columns=["A", "B", "Sum", "Carry"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            a = st.toggle("Input A", value=False)
            b = st.toggle("Input B", value=False)
            
            sum_bit = XOR_gate(int(a), int(b))
            carry = AND_gate(int(a), int(b))
            
            st.metric("Sum", sum_bit)
            st.metric("Carry", carry)
            
            inputs = {"Input A": int(a), "Input B": int(b)}
            outputs = {"Sum": sum_bit, "Carry": carry}
            log_data(inputs, outputs, "Binary Addition")
            
        with sim_col2:
            # Display the implementation diagram image
            st.write("#### Binary Addition Implementation")
            st.image("binary_adder.jpg", caption="Binary Addition Implementation", use_column_width=True)

def address_decoder_simulator():
    st.write("### Address Decoder Circuit")
    st.info("An address decoder decodes a binary address and selects one of many output lines.")
    
    # Display the circuit diagram image
    st.write("#### Circuit Diagram")
    st.image("Address-decoder-curcuit.png", caption="Address Decoder Circuit Diagram", use_column_width=True)
    
    # Truth Table for a 2-to-4 decoder
    st.write("### Truth Table (2-to-4 Decoder)")
    truth_table_data = []
    for a in [0, 1]:
        for b in [0, 1]:
            output0 = 1 if (a == 0 and b == 0) else 0
            output1 = 1 if (a == 0 and b == 1) else 0
            output2 = 1 if (a == 1 and b == 0) else 0
            output3 = 1 if (a == 1 and b == 1) else 0
            truth_table_data.append([a, b, output0, output1, output2, output3])
    
    truth_df = pd.DataFrame(truth_table_data, columns=["A", "B", "Output 0", "Output 1", "Output 2", "Output 3"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            a = st.toggle("Input A", value=False)
            b = st.toggle("Input B", value=False)
            
            output0 = 1 if (not a and not b) else 0
            output1 = 1 if (not a and b) else 0
            output2 = 1 if (a and not b) else 0
            output3 = 1 if (a and b) else 0
            
            st.metric("Output 0", output0)
            st.metric("Output 1", output1)
            st.metric("Output 2", output2)
            st.metric("Output 3", output3)
            
            inputs = {"Input A": int(a), "Input B": int(b)}
            outputs = {"Output 0": output0, "Output 1": output1, "Output 2": output2, "Output 3": output3}
            log_data(inputs, outputs, "Address Decoder")
            
        with sim_col2:
            # Display the implementation diagram image
            st.write("#### Address Decoder Implementation")
            st.image("Address-decoder-curcuit.png", caption="Address Decoder Implementation", use_column_width=True)
                                
# Run the selected experiment
if selected_experiment == "Half Adder":
    half_adder_simulator()
elif selected_experiment == "Full Adder":
    full_adder_simulator()
elif selected_experiment == "Half Subtractor":
    half_subtractor_simulator()
elif selected_experiment == "Full Subtractor":
    full_subtractor_simulator()
elif selected_experiment == "Multiplexer (MUX)":
    multiplexer_simulator()
elif selected_experiment == "Demultiplexer (DEMUX)":
    demultiplexer_simulator()
elif selected_experiment == "Magnitude Comparator":
    magnitude_comparator_simulator()
elif selected_experiment == "Binary Addition":
    binary_addition_simulator()
elif selected_experiment == "Address Decoder":
    address_decoder_simulator()
else:
    st.warning("Please select an experiment from the sidebar.")

# Sequential Circuit Functions
def sr_latch_nand_simulator():
    st.write("### SR Latch using NAND Gates")
    st.info("The SR Latch is a basic memory element built using cross-coupled NAND gates.")
    
    # State tracking
    if "q_state" not in st.session_state:
        st.session_state.q_state = 1
        st.session_state.q_not_state = 0
    
    # Truth Table
    st.write("### Truth Table")
    truth_df = pd.DataFrame([
        ["1", "1", "No change", "No change", "Memory state"],
        ["1", "0", "0", "1", "Reset"],
        ["0", "1", "1", "0", "Set"],
        ["0", "0", "1", "1", "Invalid/Race"]
    ], columns=["S̅", "R̅", "Q", "Q̅", "Operation"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            set_input = st.toggle("S̅ (Set)", value=True)
            reset_input = st.toggle("R̅ (Reset)", value=True)
            
            # Logic for SR Latch using NAND gates
            if not set_input and not reset_input:  # Both 0 -> Invalid
                st.session_state.q_state = 1
                st.session_state.q_not_state = 1
                st.warning("⚠️ Invalid state (S̅=0, R̅=0)")
            elif not set_input and reset_input:  # S̅=0, R̅=1 -> Set
                st.session_state.q_state = 1
                st.session_state.q_not_state = 0
            elif set_input and not reset_input:  # S̅=1, R̅=0 -> Reset
                st.session_state.q_state = 0
                st.session_state.q_not_state = 1
            # If both 1, no change (keep previous state)
            
            st.metric("Q", st.session_state.q_state)
            st.metric("Q̅", st.session_state.q_not_state)
            
            inputs = {"S̅": int(not set_input), "R̅": int(not reset_input)}  # Inverted for NAND
            outputs = {"Q": st.session_state.q_state, "Q̅": st.session_state.q_not_state}
            log_data(inputs, outputs, "SR Latch (NAND)")
            
        with sim_col2:
            # Create a simple diagram
            st.write("#### SR Latch Implementation (NAND gates)")
            st.markdown("""
            ```
            S̅ --->|NAND|---+---> Q
                   |    |   |
                   +----+   |
                   |        |
                   +----+   |
                   |    |   |
            R̅ --->|NAND|---+---> Q̅
            ```
            """)
            st.write("Note: NAND-based SR Latch uses active-low inputs")

def sr_latch_nor_simulator():
    st.write("### SR Latch using NOR Gates")
    st.info("The SR Latch is a basic memory element built using cross-coupled NOR gates.")
    
    # State tracking
    if "q_state" not in st.session_state:
        st.session_state.q_state = 0
        st.session_state.q_not_state = 1
    
    # Truth Table
    st.write("### Truth Table")
    truth_df = pd.DataFrame([
        ["0", "0", "No change", "No change", "Memory state"],
        ["0", "1", "0", "1", "Reset"],
        ["1", "0", "1", "0", "Set"],
        ["1", "1", "0", "0", "Invalid/Race"]
    ], columns=["S", "R", "Q", "Q̅", "Operation"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            set_input = st.toggle("S (Set)", value=False)
            reset_input = st.toggle("R (Reset)", value=False)
            
            # Logic for SR Latch using NOR gates
            if set_input and reset_input:  # Both 1 -> Invalid
                st.session_state.q_state = 0
                st.session_state.q_not_state = 0
                st.warning("⚠️ Invalid state (S=1, R=1)")
            elif set_input and not reset_input:  # S=1, R=0 -> Set
                st.session_state.q_state = 1
                st.session_state.q_not_state = 0
            elif not set_input and reset_input:  # S=0, R=1 -> Reset
                st.session_state.q_state = 0
                st.session_state.q_not_state = 1
            # If both 0, no change (keep previous state)
            
            st.metric("Q", st.session_state.q_state)
            st.metric("Q̅", st.session_state.q_not_state)
            
            inputs = {"S": int(set_input), "R": int(reset_input)}
            outputs = {"Q": st.session_state.q_state, "Q̅": st.session_state.q_not_state}
            log_data(inputs, outputs, "SR Latch (NOR)")
            
        with sim_col2:
            # Create a simple diagram
            st.write("#### SR Latch Implementation (NOR gates)")
            st.markdown("""
            ```
            S --->|NOR|---+---> Q
                  |    |   |
                  +----+   |
                  |        |
                  +----+   |
                  |    |   |
            R --->|NOR|---+---> Q̅
            ```
            """)
            st.write("Note: NOR-based SR Latch uses active-high inputs")

def d_flip_flop_simulator():
    st.write("### D Flip-Flop")
    st.info("The D Flip-Flop stores the state of the D input when triggered by a clock signal.")
    
    # Initialize state if needed
    if "d_ff_q" not in st.session_state:
        st.session_state.d_ff_q = 0
        st.session_state.d_ff_q_not = 1
        st.session_state.prev_clock = 0
    
    # Truth Table
    st.write("### Truth Table")
    truth_df = pd.DataFrame([
        ["Rising Edge", "0", "0", "1"],
        ["Rising Edge", "1", "1", "0"],
        ["Not rising edge", "X", "No change", "No change"]
    ], columns=["Clock", "D", "Q", "Q̅"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            d_input = st.toggle("D Input", value=False)
            clock = st.toggle("Clock", value=False)
            
            # Detect rising edge (0 to 1 transition)
            rising_edge = (not st.session_state.prev_clock) and clock
            
            # Update state on rising edge
            if rising_edge:
                st.session_state.d_ff_q = int(d_input)
                st.session_state.d_ff_q_not = int(not d_input)
                st.success("📈 Rising edge detected - state updated!")
            
            # Store current clock for next comparison
            st.session_state.prev_clock = clock
            
            st.metric("Q", st.session_state.d_ff_q)
            st.metric("Q̅", st.session_state.d_ff_q_not)
            
            inputs = {"D": int(d_input), "Clock": int(clock)}
            outputs = {"Q": st.session_state.d_ff_q, "Q̅": st.session_state.d_ff_q_not}
            log_data(inputs, outputs, "D Flip-Flop")
            
        with sim_col2:
            # Create a simple diagram
            st.write("#### D Flip-Flop Implementation")
            st.markdown("""
            ```
                       +-------------+
                       |             |
            D -------->|D            |
                       |            Q|----> Q
            Clock ---->|CLK          |
                       |            Q̅|----> Q̅
                       |             |
                       +-------------+
            ```
            """)
            st.write("A D flip-flop can be constructed from an SR latch with D connected to S and D̅ to R")

def master_slave_jk_flip_flop_simulator():
    st.write("### Master-Slave JK Flip-Flop")
    st.info("The Master-Slave JK Flip-Flop is a sequential circuit that avoids race conditions by using two stages: Master and Slave.")
    
    # State tracking
    if "q_state" not in st.session_state:
        st.session_state.q_state = 0
        st.session_state.q_not_state = 1
    
    # Truth Table
    st.write("### Truth Table")
    truth_df = pd.DataFrame([
        ["0", "0", "No change", "No change", "Memory state"],
        ["0", "1", "0", "1", "Reset"],
        ["1", "0", "1", "0", "Set"],
        ["1", "1", "Toggle", "Toggle", "Toggle"]
    ], columns=["J", "K", "Q", "Q̅", "Operation"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            j_input = st.toggle("J (Set)", value=False)
            k_input = st.toggle("K (Reset)", value=False)
            clock_input = st.toggle("Clock", value=False)
            
            # Logic for Master-Slave JK Flip-Flop
            if clock_input:  # On rising edge of the clock
                if j_input and not k_input:  # Set
                    st.session_state.q_state = 1
                    st.session_state.q_not_state = 0
                elif not j_input and k_input:  # Reset
                    st.session_state.q_state = 0
                    st.session_state.q_not_state = 1
                elif j_input and k_input:  # Toggle
                    st.session_state.q_state = 1 - st.session_state.q_state
                    st.session_state.q_not_state = 1 - st.session_state.q_not_state
                # If both 0, no change (keep previous state)
            
            st.metric("Q", st.session_state.q_state)
            st.metric("Q̅", st.session_state.q_not_state)
            
            inputs = {"J": int(j_input), "K": int(k_input), "Clock": int(clock_input)}
            outputs = {"Q": st.session_state.q_state, "Q̅": st.session_state.q_not_state}
            log_data(inputs, outputs, "Master-Slave JK Flip-Flop")
            
        with sim_col2:
            # Create a simple diagram
            st.write("#### Master-Slave JK Flip-Flop Implementation")
            st.markdown("""
            ```
            J --->|Master|--->|Slave|---> Q
            K --->|      |   |     |
            Clock --->|      |   |     |---> Q̅
            ```
            """)
            st.write("Note: The Master-Slave JK Flip-Flop avoids race conditions by using two stages.")
            
def shift_register_simulator():
    st.write("### Shift Register")
    st.info("A shift register is a sequential circuit that shifts data in or out one bit at a time.")
    
    # State tracking
    if "shift_register_state" not in st.session_state:
        st.session_state.shift_register_state = [0, 0, 0, 0]  # 4-bit shift register
    
    # Truth Table
    st.write("### Truth Table (4-bit Shift Register)")
    truth_df = pd.DataFrame([
        ["0", "0", "No change", "No change", "No shift"],
        ["1", "0", "Shift right", "Shift right", "Shift data right"],
        ["0", "1", "Shift left", "Shift left", "Shift data left"],
        ["1", "1", "Invalid", "Invalid", "Invalid operation"]
    ], columns=["Shift Right", "Shift Left", "Operation", "Output", "Description"])
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            shift_right = st.toggle("Shift Right", value=False)
            shift_left = st.toggle("Shift Left", value=False)
            data_input = st.toggle("Data Input", value=False)
            
            # Logic for Shift Register
            if shift_right and not shift_left:  # Shift right
                st.session_state.shift_register_state = [data_input] + st.session_state.shift_register_state[:-1]
            elif not shift_right and shift_left:  # Shift left
                st.session_state.shift_register_state = st.session_state.shift_register_state[1:] + [data_input]
            elif shift_right and shift_left:  # Invalid
                st.warning("⚠️ Invalid operation (Shift Right and Shift Left cannot be active simultaneously)")
            
            st.write("### Shift Register State")
            st.write(f"Bit 3: {st.session_state.shift_register_state[0]}")
            st.write(f"Bit 2: {st.session_state.shift_register_state[1]}")
            st.write(f"Bit 1: {st.session_state.shift_register_state[2]}")
            st.write(f"Bit 0: {st.session_state.shift_register_state[3]}")
            
            inputs = {"Shift Right": int(shift_right), "Shift Left": int(shift_left), "Data Input": int(data_input)}
            outputs = {"Bit 3": st.session_state.shift_register_state[0],
                       "Bit 2": st.session_state.shift_register_state[1],
                       "Bit 1": st.session_state.shift_register_state[2],
                       "Bit 0": st.session_state.shift_register_state[3]}
            log_data(inputs, outputs, "Shift Register")
            
        with sim_col2:
            # Create a simple diagram
            st.write("#### Shift Register Implementation")
            st.markdown("""
            ```
            Data Input --->|Bit 3|--->|Bit 2|--->|Bit 1|--->|Bit 0|
            Shift Right --->|      |   |     |   |     |   |     |
            Shift Left --->|      |   |     |   |     |   |     |
            ```
            """)
            st.write("Note: The shift register can shift data left or right based on control signals.")
            
            
if selected_experiment == "SR Latch (NAND)":
    sr_latch_nand_simulator()
elif selected_experiment == "SR Latch (NOR)":
    sr_latch_nor_simulator()
elif selected_experiment == "D Flip-Flop":
    d_flip_flop_simulator()
elif selected_experiment == "Master-Slave JK Flip-Flop":
    master_slave_jk_flip_flop_simulator()
elif selected_experiment == "Shift Register":
    shift_register_simulator()
else:
    st.warning("Please select an experiment from the sidebar.")
    
# Timer and Multivibrator Functions
def astable_multivibrator_555():
    st.write("### Astable Multivibrator using 555 IC")
    st.info("An astable multivibrator generates a continuous square wave without any external trigger.")
    
    # Circuit diagram placeholder
    st.write("#### Circuit Diagram")
    st.write("The 555 IC is configured with two resistors and a capacitor to generate a square wave.")
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            r1 = st.slider("Resistor R1 (kΩ)", 1, 100, 10)
            r2 = st.slider("Resistor R2 (kΩ)", 1, 100, 10)
            c = st.slider("Capacitor C (µF)", 1, 100, 10)
            
            # Calculate frequency and duty cycle
            frequency = 1.44 / ((r1 + 2 * r2) * c)
            duty_cycle = (r1 + r2) / (r1 + 2 * r2) * 100
            
            st.metric("Frequency (Hz)", round(frequency, 2))
            st.metric("Duty Cycle (%)", round(duty_cycle, 2))
            
            inputs = {"R1": r1, "R2": r2, "C": c}
            outputs = {"Frequency": frequency, "Duty Cycle": duty_cycle}
            log_data(inputs, outputs, "Astable Multivibrator using 555 IC")
            
        with sim_col2:
            # Create a simple diagram
            st.write("#### Astable Multivibrator Circuit")
            st.markdown("""
            ```
            +-----+
            | 555 |
            | IC  |
            +-----+
               |
               +---> Output (Square Wave)
            ```
            """)

def monostable_multivibrator_555():
    st.write("### Monostable Multivibrator using 555 IC")
    st.info("A monostable multivibrator generates a single pulse of a specific duration when triggered.")
    
    # Circuit diagram placeholder
    st.write("#### Circuit Diagram")
    st.write("The 555 IC is configured with a resistor and a capacitor to generate a single pulse.")
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            r = st.slider("Resistor R (kΩ)", 1, 100, 10)
            c = st.slider("Capacitor C (µF)", 1, 100, 10)
            
            # Calculate pulse width
            pulse_width = 1.1 * r * c
            
            st.metric("Pulse Width (ms)", round(pulse_width, 2))
            
            inputs = {"R": r, "C": c}
            outputs = {"Pulse Width": pulse_width}
            log_data(inputs, outputs, "Monostable Multivibrator using 555 IC")
            
        with sim_col2:
            # Create a simple diagram
            st.write("#### Monostable Multivibrator Circuit")
            st.markdown("""
            ```
            +-----+
            | 555 |
            | IC  |
            +-----+
               |
               +---> Output (Single Pulse)
            ```
            """)

# Counter and Register Functions
def binary_up_down_counter():
    st.write("### Binary Up/Down Counter")
    st.info("A binary up/down counter can count in both increasing and decreasing order based on a control signal.")
    
    # State tracking
    if "counter_value" not in st.session_state:
        st.session_state.counter_value = 0
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            count_up = st.button("Count Up")
            count_down = st.button("Count Down")
            reset = st.button("Reset")
            
            if count_up:
                st.session_state.counter_value += 1
            if count_down:
                st.session_state.counter_value -= 1
            if reset:
                st.session_state.counter_value = 0
            
            st.metric("Counter Value", st.session_state.counter_value)
            
            inputs = {"Count Up": count_up, "Count Down": count_down, "Reset": reset}
            outputs = {"Counter Value": st.session_state.counter_value}
            log_data(inputs, outputs, "Binary Up/Down Counter")
            
        with sim_col2:
            # Create a simple diagram
            st.write("#### Binary Up/Down Counter Circuit")
            st.markdown("""
            ```
            +-----+
            |Counter|
            +-----+
               |
               +---> Output (Binary Value)
            ```
            """)

def bcd_decoder_7segment():
    st.write("### BCD Decoder with 7-Segment Display")
    st.info("A BCD decoder converts a 4-bit binary input into the appropriate signals for a 7-segment display.")
    
    # Mapping BCD to 7-segment (a,b,c,d,e,f,g)
    segment_patterns = {
        0: [1, 1, 1, 1, 1, 1, 0],  # 0
        1: [0, 1, 1, 0, 0, 0, 0],  # 1
        2: [1, 1, 0, 1, 1, 0, 1],  # 2
        3: [1, 1, 1, 1, 0, 0, 1],  # 3
        4: [0, 1, 1, 0, 0, 1, 1],  # 4
        5: [1, 0, 1, 1, 0, 1, 1],  # 5
        6: [1, 0, 1, 1, 1, 1, 1],  # 6
        7: [1, 1, 1, 0, 0, 0, 0],  # 7
        8: [1, 1, 1, 1, 1, 1, 1],  # 8
        9: [1, 1, 1, 1, 0, 1, 1],  # 9
    }
    
    # Truth Table
    st.write("### Truth Table (BCD to 7-Segment)")
    truth_rows = []
    for i in range(10):  # BCD: 0-9
        binary = format(i, '04b')
        segments = ''.join(map(str, segment_patterns[i]))
        truth_rows.append([*binary, *segments])
    
    truth_df = pd.DataFrame(
        truth_rows, 
        columns=["D", "C", "B", "A", "a", "b", "c", "d", "e", "f", "g"]
    )
    st.table(truth_df)
    
    # Interactive Simulation
    if mode == "🟢 Simulation Mode":
        st.write("### Interactive Simulation")
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            st.write("#### BCD Input")
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                bit_a = st.toggle("A (LSB)", value=False)
            with col_b:
                bit_b = st.toggle("B", value=False)
            with col_c:
                bit_c = st.toggle("C", value=False)
            with col_d:
                bit_d = st.toggle("D (MSB)", value=False)
            
            # Convert binary to decimal
            decimal = bit_a * 1 + bit_b * 2 + bit_c * 4 + bit_d * 8
            
            # Only process valid BCD values (0-9)
            if decimal > 9:
                st.error("⚠️ Invalid BCD input (>9)")
                segments = [0, 0, 0, 0, 0, 0, 0]
            else:
                segments = segment_patterns[decimal]
                st.success(f"Displaying: {decimal}")
            
            inputs = {"D": int(bit_d), "C": int(bit_c), "B": int(bit_b), "A": int(bit_a)}
            outputs = {
                "a": segments[0], "b": segments[1], "c": segments[2], 
                "d": segments[3], "e": segments[4], "f": segments[5], "g": segments[6]
            }
            log_data(inputs, outputs, "BCD Decoder with 7-Segment Display")
            
        with sim_col2:
            # Draw a 7-segment display
            st.write("#### 7-Segment Display")
            
            # Basic 7-segment display rendering
            segments_active = segments
            
            # CSS for 7-segment display
            st.markdown(f"""
            <style>
            .segment-container {{
                width: 100px;
                height: 180px;
                margin: 20px auto;
                position: relative;
            }}
            .segment {{
                position: absolute;
                background-color: #dddddd;
            }}
            .segment.horizontal {{
                height: 10px;
                width: 60px;
                left: 20px;
            }}
            .segment.vertical {{
                width: 10px;
                height: 60px;
            }}
            .segment.active {{
                background-color: #ff0000;
            }}
            
            /* Segment positions */
            .segment-a {{ top: 0; }}
            .segment-b {{ top: 10px; right: 20px; }}
            .segment-c {{ top: 80px; right: 20px; }}
            .segment-d {{ top: 150px; }}
            .segment-e {{ top: 80px; left: 20px; }}
            .segment-f {{ top: 10px; left: 20px; }}
            .segment-g {{ top: 75px; }}
            </style>
            
            <div class="segment-container">
                <div class="segment horizontal segment-a {'active' if segments_active[0] else ''}"></div>
                <div class="segment vertical segment-b {'active' if segments_active[1] else ''}"></div>
                <div class="segment vertical segment-c {'active' if segments_active[2] else ''}"></div>
                <div class="segment horizontal segment-d {'active' if segments_active[3] else ''}"></div>
                <div class="segment vertical segment-e {'active' if segments_active[4] else ''}"></div>
                <div class="segment vertical segment-f {'active' if segments_active[5] else ''}"></div>
                <div class="segment horizontal segment-g {'active' if segments_active[6] else ''}"></div>
            </div>
            """, unsafe_allow_html=True)

# Run the selected experiment
if selected_experiment == "Astable Multivibrator using 555 IC":
    astable_multivibrator_555()
elif selected_experiment == "Monostable Multivibrator using 555 IC":
    monostable_multivibrator_555()
elif selected_experiment == "Binary Up/Down Counter":
    binary_up_down_counter()
elif selected_experiment == "BCD Decoder with 7-Segment Display":
    bcd_decoder_7segment()
    
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
