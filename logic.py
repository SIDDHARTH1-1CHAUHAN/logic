import streamlit as st
import serial
import time
import os
import pandas as pd

# 🔌 Available COM ports (Modify for your system)
available_ports = ['COM3', 'COM4', 'COM5', 'COM6']
selected_port = st.sidebar.selectbox("Select COM Port:", available_ports)

# 📡 Serial Communication
try:
    ser = serial.Serial(selected_port, 9600, timeout=1)
    time.sleep(2)
    st.success(f"Connected to {selected_port}")
except Exception as e:
    ser = None
    st.error(f"Error connecting to Arduino: {e}")

# 🎛️ Logic Gate Functions
def AND_gate(a, b): return a and b
def OR_gate(a, b): return a or b
def XOR_gate(a, b): return a ^ b
def NAND_gate(a, b): return not (a and b)
def NOR_gate(a, b): return not (a or b)
def XNOR_gate(a, b): return not (a ^ b)

gate_functions = {
    "AND": AND_gate, "OR": OR_gate, "XOR": XOR_gate,
    "NAND": NAND_gate, "NOR": NOR_gate, "XNOR": XNOR_gate
}

gate_descriptions = {
    "AND": "The AND gate outputs **1** only if **both inputs** are 1.",
    "OR": "The OR gate outputs **1** if **at least one input** is 1.",
    "XOR": "The XOR gate outputs **1** if the inputs are **different**.",
    "NAND": "The NAND gate outputs **0** only if **both inputs** are 1.",
    "NOR": "The NOR gate outputs **1** only if **both inputs** are 0.",
    "XNOR": "The XNOR gate outputs **1** if the inputs are **the same**."
}

st.title("🔮 **Futuristic Logic Gate Simulator**")
st.sidebar.header("⚙️ Gate Selection")

selected_gate = st.sidebar.selectbox("Choose a logic gate:", list(gate_functions.keys()))
mode = st.sidebar.radio("Mode Selection", ["🔴 Hardware Mode", "🟢 Manual Mode", "🔥 Circuit Simulator"])

st.write(f"### Selected Gate: **{selected_gate}**")
st.info(gate_descriptions[selected_gate])

# 🔍 Display Logic & IC Diagram
logic_image_path = f"images/{selected_gate.lower()}_logic.png"
ic_image_path = f"images/{selected_gate.lower()}_ic.png"

if os.path.exists(logic_image_path):
    st.image(logic_image_path, caption="Logic Gate Diagram")
else:
    st.warning(f"⚠️ Logic gate diagram not found for {selected_gate}.")

if os.path.exists(ic_image_path):
    st.image(ic_image_path, caption="IC Diagram")
else:
    st.warning(f"⚠️ IC diagram not found for {selected_gate}.")

# 📈 Persistent Data Logging
log_file = "logic_gate_logs.csv"

# Load existing log data if available
if os.path.exists(log_file):
    history_data = pd.read_csv(log_file).to_dict(orient="records")
else:
    history_data = []

def log_data(in1, in2, result):
    """Logs the experiment data into a CSV file."""
    entry = {"Input 1": in1, "Input 2": in2, "Output": result, "Gate": selected_gate}
    history_data.append(entry)
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(history_data)
    df.to_csv(log_file, index=False)

# 🔴 Hardware Mode (Live from Arduino)
if mode == "🔴 Hardware Mode":
    if ser:
        st.write("### Live Experiment from Arduino")
        placeholder = st.empty()
        
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                if data:
                    try:
                        in1, in2 = map(int, data.split(","))
                        result = gate_functions[selected_gate](in1, in2)
                        ser.write(f"{int(result)}\n".encode('utf-8'))
                        log_data(in1, in2, result)

                        with placeholder.container():
                            st.metric("Input 1", in1)
                            st.metric("Input 2", in2)
                            st.metric("Output", result)
                            st.write(f"📡 **Arduino Live Input:** {in1}, {in2} → **Output:** {result}")

                    except ValueError:
                        st.warning("⚠️ Invalid data received from Arduino.")
    else:
        st.error("⚠️ No connection to Arduino detected!")

# 🟢 Manual Mode
elif mode == "🟢 Manual Mode":
    in1 = st.toggle("Input 1", value=False)
    in2 = st.toggle("Input 2", value=False)
    result = gate_functions[selected_gate](int(in1), int(in2))
    log_data(int(in1), int(in2), result)
    st.metric("Output", result)

# 🔥 Circuit Simulator
elif mode == "🔥 Circuit Simulator":
    st.write("### ⚡ Drag & Drop Circuit Simulator")
    st.markdown("Click the button below to open the Circuit Simulator:")
    
    # Open CircuitVerse in a new tab
    st.markdown(
        '[🛠️ Open Circuit Simulator](https://circuitverse.org/simulator) 🎛️',
        unsafe_allow_html=True
    )

# 📜 Experiment History with Filter
st.sidebar.header("📜 Experiment History")

if history_data:
    df_logs = pd.DataFrame(history_data)
    
    # Dropdown to filter logs by gate type
    gate_filter = st.sidebar.selectbox("Filter by Gate:", ["All"] + list(gate_functions.keys()))
    
    if gate_filter != "All":
        df_logs = df_logs[df_logs["Gate"] == gate_filter]

    st.sidebar.write("### Experiment Logs")
    st.sidebar.dataframe(df_logs)

    # 📥 Download Experiment Data
    csv_data = df_logs.to_csv(index=False)
    st.sidebar.download_button("📥 Download Log (CSV)", data=csv_data, file_name="logic_gate_logs.csv", mime="text/csv")
else:
    st.sidebar.info("No logs yet. Start experimenting!")

st.success("✅ Simulation running smoothly!") 
