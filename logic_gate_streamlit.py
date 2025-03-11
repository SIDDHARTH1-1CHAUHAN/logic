import streamlit as st
import serial
import time
import os

# Available COM ports (Modify as per your system)
available_ports = ['COM3', 'COM4', 'COM5', 'COM6']
selected_port = st.sidebar.selectbox("Select COM Port:", available_ports)

# Setup serial communication with Arduino
ser = None
try:
    ser = serial.Serial(selected_port, 9600, timeout=1)
    time.sleep(2)  # Allow some time for the serial connection to establish
    st.success(f"Connected to {selected_port}")
except serial.SerialException as e:
    st.error(f"Error connecting to Arduino: {e}")

# Define logic gates functions
def AND_gate(a, b): return a and b
def OR_gate(a, b): return a or b
def XOR_gate(a, b): return a ^ b
def NAND_gate(a, b): return not (a and b)
def NOR_gate(a, b): return not (a or b)
def XNOR_gate(a, b): return not (a ^ b)

gate_functions = {
    "AND": AND_gate,
    "OR": OR_gate,
    "XOR": XOR_gate,
    "NAND": NAND_gate,
    "NOR": NOR_gate,
    "XNOR": XNOR_gate
}

gate_descriptions = {
    "AND": "The AND gate outputs **1** only if **both inputs** are 1.",
    "OR": "The OR gate outputs **1** if **at least one input** is 1.",
    "XOR": "The XOR (Exclusive OR) gate outputs **1** if the inputs are **different**.",
    "NAND": "The NAND (NOT AND) gate outputs **0** only if **both inputs** are 1.",
    "NOR": "The NOR (NOT OR) gate outputs **1** only if **both inputs** are 0.",
    "XNOR": "The XNOR (Exclusive NOR) gate outputs **1** if the inputs are **the same**."
}

# UI Layout
st.title("🔌 Logic Gate Simulator")
st.sidebar.header("⚙️ Gate Selection")
selected_gate = st.sidebar.selectbox("Choose a logic gate:", list(gate_functions.keys()))

mode = st.sidebar.radio("Mode Selection", ["🔴 Hardware Mode", "🟢 Manual Mode"])

st.write(f"### Selected Gate: **{selected_gate}**")
st.info(gate_descriptions[selected_gate])

# Logic Diagram & IC Diagram (Handles missing images)
logic_image_path = f"{selected_gate.lower()}.png"
ic_image_path = f"images/{selected_gate.lower()}_ic.png"

if os.path.exists(logic_image_path):
    st.image(logic_image_path, caption="Logic Gate Diagram")
else:
    st.warning(f"⚠️ Logic gate diagram not found for {selected_gate}.")

if os.path.exists(ic_image_path):
    st.image(ic_image_path, caption="IC Diagram")
else:
    st.warning(f"⚠️ IC diagram not found for {selected_gate}.")

# Live Hardware Mode (Dynamic Updates)
if mode == "🔴 Hardware Mode":
    if ser:
        st.write("### Live Experiment from Arduino")
        placeholder = st.empty()  # Placeholder for dynamic updates
        
        # Check for data availability and update periodically
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            if data:
                try:
                    in1, in2 = map(int, data.split(","))
                    result = gate_functions[selected_gate](in1, in2)
                    ser.write(f"{int(result)}\n".encode('utf-8'))

                    # Update the UI dynamically
                    with placeholder.container():
                        st.metric("Input 1", in1)
                        st.metric("Input 2", in2)
                        st.metric("Output", result)
                        st.write(f"📡 **Arduino Live Input:** {in1}, {in2} → **Output:** {result}")

                except ValueError:
                    st.warning("⚠️ Invalid data received from Arduino.")

        # Refresh the Streamlit app periodically
        time.sleep(1)  # Optional delay to reduce CPU load
        st.rerun()  # Updated method to trigger a re-run of the app

    else:
        st.error("⚠️ No connection to Arduino detected!")

# Manual Mode (User Inputs)
elif mode == "🟢 Manual Mode":
    in1 = st.toggle("Input 1", value=False)
    in2 = st.toggle("Input 2", value=False)
    # Convert boolean to int (0 or 1)
    in1 = int(in1)
    in2 = int(in2)
    result = gate_functions[selected_gate](in1, in2)

    st.metric("Output", result)

st.success("✅ Simulation running!")
