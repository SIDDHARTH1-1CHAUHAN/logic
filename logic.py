import streamlit as st
import serial
import time
import os
import pandas as pd
import plotly.graph_objects as go

# 🔌 Available COM ports (Modify as needed)
available_ports = ['COM3', 'COM4', 'COM5', 'COM6']
selected_port = st.sidebar.selectbox("Select COM Port:", available_ports)

# 📡 Serial Communication Setup
ser = None
try:
    ser = serial.Serial(selected_port, 9600, timeout=1)
    time.sleep(2)
    st.success(f"Connected to {selected_port}")
except Exception as e:
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

# 📝 Gate Descriptions
gate_descriptions = {
    "AND": "Outputs **1** if **both inputs** are 1.",
    "OR": "Outputs **1** if **at least one input** is 1.",
    "XOR": "Outputs **1** if the inputs are **different**.",
    "NAND": "Outputs **0** only if **both inputs** are 1.",
    "NOR": "Outputs **1** only if **both inputs** are 0.",
    "XNOR": "Outputs **1** if the inputs are **the same**."
}

st.title("🔮 **Logic Gate Simulator with Real-Time Waveform**")
st.sidebar.header("⚙️ Gate Selection")

selected_gate = st.sidebar.selectbox("Choose a logic gate:", list(gate_functions.keys()))
mode = st.sidebar.radio("Mode Selection", ["🔴 Hardware Mode", "🟢 Manual Mode", "🔥 Circuit Simulator"])

st.write(f"### Selected Gate: **{selected_gate}**")
st.info(gate_descriptions[selected_gate])

# 🖼️ Display Logic Gate and IC Diagram
logic_image_path = f"images/{selected_gate.lower()}.png"
ic_image_path = f"images/{selected_gate.lower()}_ic.png"

if os.path.exists(logic_image_path):
    st.image(logic_image_path, caption="Logic Gate Diagram")
else:
    st.warning("⚠️ Logic gate diagram not found.")

if os.path.exists(ic_image_path):
    st.image(ic_image_path, caption="IC Diagram")
else:
    st.warning("⚠️ IC diagram not found.")

# 📈 Persistent Data Logging using Streamlit session_state
if "history_data" not in st.session_state:
    st.session_state.history_data = []

if "waveform_data" not in st.session_state:
    st.session_state.waveform_data = {"Time": [], "Input 1": [], "Input 2": [], "Output": []}

def log_data(in1, in2, result):
    """Logs experiment data dynamically."""
    entry = {"Input 1": in1, "Input 2": in2, "Output": result, "Gate": selected_gate}
    st.session_state.history_data.append(entry)
    
    # Update waveform data
    st.session_state.waveform_data["Time"].append(len(st.session_state.waveform_data["Time"]))
    st.session_state.waveform_data["Input 1"].append(in1)
    st.session_state.waveform_data["Input 2"].append(in2)
    st.session_state.waveform_data["Output"].append(result)

# 🎛 Interactive Timing Diagram
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
            title=f"⏳ Timing Diagram - {selected_gate} Gate",
            xaxis_title="Time Steps",
            yaxis_title="Logic State (0/1)",
            yaxis=dict(tickmode="array", tickvals=[0, 1]),
            height=400,
            template="plotly_dark"
        )

    return fig

# 🔴 Hardware Mode (Live from Arduino)
if mode == "🔴 Hardware Mode":
    st.write("### Live Experiment from Arduino")
    start_experiment = st.button("Start Experiment")

    if start_experiment and ser:
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                if data:
                    try:
                        in1, in2 = map(int, data.split(","))
                        result = gate_functions[selected_gate](in1, in2)
                        
                        # Send response back
                        ser.write(f"{int(result)}\n".encode('utf-8'))
                        
                        log_data(in1, in2, result)

                        # Display Metrics & Waveform
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.metric("Input 1", in1)
                            st.metric("Input 2", in2)
                            st.metric("Output", result)

                        with col2:
                            st.plotly_chart(plot_logic_wave(), use_container_width=True)

                    except ValueError:
                        st.warning("⚠️ Invalid data received from Arduino.")

# 🟢 Manual Mode
elif mode == "🟢 Manual Mode":
    col1, col2 = st.columns([1, 2])

    with col1:
        in1 = st.toggle("Input 1", value=False)
        in2 = st.toggle("Input 2", value=False)
        result = gate_functions[selected_gate](int(in1), int(in2))
        log_data(int(in1), int(in2), result)
        st.metric("Output", result)

    with col2:
        st.plotly_chart(plot_logic_wave(), use_container_width=True)

# 🔥 Circuit Simulator
elif mode == "🔥 Circuit Simulator":
    st.write("### ⚡ Drag & Drop Circuit Simulator")
    st.components.v1.html("""
        <iframe width="100%" height="500px" src="https://circuitverse.org/simulator"></iframe>
    """, height=550)

# 📜 Experiment History with Filter
st.sidebar.header("📜 Experiment History")

if st.session_state.history_data:
    df_logs = pd.DataFrame(st.session_state.history_data)
    
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
