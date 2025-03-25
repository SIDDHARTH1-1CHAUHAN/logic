import streamlit as st
import serial
import time
import json
import pandas as pd
import plotly.graph_objects as go

# Initialize Arduino serial connection
def initialize_serial_connection(port):
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        return ser
    except Exception as e:
        st.sidebar.error(f"Error connecting to Arduino: {e}")
        return None

# Send command to Arduino and receive response
def send_arduino_command(ser, gate_type, inputs):
    try:
        # Prepare command as JSON
        command = {
            "operation": "GATE",
            "gate_type": gate_type,
            "inputs": inputs
        }
        
        # Send command to Arduino
        ser.write((json.dumps(command) + "\n").encode())
        time.sleep(0.1)  # Small delay for Arduino processing
        
        # Read response from Arduino
        response_raw = ser.readline().decode('utf-8').strip()
        if not response_raw:
            return {"error": "No response from Arduino"}
        
        response = json.loads(response_raw)
        return response
            
    except Exception as e:
        return {"error": f"Communication error: {str(e)}"}

# Streamlit UI setup
st.set_page_config(page_title="Digital Logic Lab Simulator", page_icon="🔌", layout="wide")

# Sidebar for serial port and connection
available_ports = ['COM3', 'COM4', 'COM5', 'COM6']
selected_port = st.sidebar.selectbox("Select COM Port:", available_ports)

# Connect to hardware
ser = None
if st.sidebar.button("Connect to Hardware"):
    ser = initialize_serial_connection(selected_port)
    if ser:
        st.sidebar.success(f"Connected to {selected_port}")
    else:
        st.sidebar.error(f"Failed to connect to {selected_port}")

# Logic Gate Simulator
def basic_logic_gate_simulator(gate_name):
    st.write(f"### {gate_name}")
    
    # Truth Table for gates
    truth_table_data = []
    if gate_name != "NOT Gate":
        for a in [0, 1]:
            for b in [0, 1]:
                if gate_name == "AND Gate":
                    result = a & b
                elif gate_name == "OR Gate":
                    result = a | b
                elif gate_name == "XOR Gate":
                    result = a ^ b
                elif gate_name == "NAND Gate":
                    result = not (a & b)
                elif gate_name == "NOR Gate":
                    result = not (a | b)
                elif gate_name == "XNOR Gate":
                    result = not (a ^ b)
                truth_table_data.append([a, b, result])
    else:
        for a in [0, 1]:
            result = not a
            truth_table_data.append([a, result])
    
    # Display the truth table
    df = pd.DataFrame(truth_table_data, columns=["Input A", "Input B", "Output"] if gate_name != "NOT Gate" else ["Input A", "Output"])
    st.table(df)

    # Interactive simulation in hardware mode
    if st.sidebar.radio("Mode Selection", ["🔴 Hardware Mode", "🟢 Simulation Mode"]) == "🔴 Hardware Mode" and ser:
        st.write("Hardware Mode")
        
        if gate_name != "NOT Gate":
            in1 = st.radio("Input A", [0, 1], index=0)
            in2 = st.radio("Input B", [0, 1], index=0)
            inputs = [int(in1), int(in2)]
        else:
            in1 = st.radio("Input A", [0, 1], index=0)
            inputs = [int(in1)]
        
        # Send command to Arduino to perform the gate operation
        response = send_arduino_command(ser, gate_name.split()[0], inputs)
        
        if "error" in response:
            st.error(response["error"])
        else:
            st.metric("Output", response.get("output"))
            
# Main Experiment Selection
st.title("🔌 Digital Logic Lab Simulator")

selected_gate = st.sidebar.selectbox("Select Gate", ["AND Gate", "OR Gate", "NOT Gate", "NAND Gate", "NOR Gate", "XOR Gate", "XNOR Gate"])
basic_logic_gate_simulator(selected_gate)
