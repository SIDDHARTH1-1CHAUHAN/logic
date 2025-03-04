import tkinter as tk
from PIL import Image, ImageTk
import serial
import threading
import time
import queue

class LogicGateGUI:
    def __init__(self, master):
        self.master = master 
        master.title("Digital Logic Gates + Hardware Status")
        
        # Set a fixed window size
        self.master.geometry("800x600")  # Fixed size window (width x height)
        
        # -------------------- 
        # 1) LOAD IMAGES
        # -------------------- 
        def load_image(path, size=None):
            try:
                img = Image.open(path)
                if size:
                    img = img.resize(size)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading image {path}: {e}")
                return None  # You might want to set a default image here

        # Load images for logic gates
        gate_filenames = {
            "AND": "AND TT.jpg",
            "OR": "OR TT.jpg",
            "NOT": "NOT TT.png",
            "NAND": "NAND TT.jpg",
            "NOR": "NOR TT.png",
            "XOR": "XOR TT.jpg",
            "XNOR": "XNOR TT.jpg",
        }
        self.gate_images = {}
        for gate, filename in gate_filenames.items():
            self.gate_images[gate] = load_image(filename)

        # Load images for LED indicators
        self.led_on_image = load_image("LED ON.jpg", (150, 150))
        self.led_off_image = load_image("LED OFF.jpg", (150, 150))

        # --------------------
        # 2) INITIAL STATES
        # --------------------
        self.input_a = False
        self.input_b = False

        # --------------------
        # 3) GATE & LED FRAME
        # --------------------
        self.gate_frame = tk.Frame(master)
        self.gate_frame.pack(pady=5, side="left")

        self.gate_label = tk.Label(self.gate_frame, image=self.gate_images.get("AND"))  # Default to AND gate
        self.gate_label.pack(side=tk.LEFT)

        # --------------------
        # 5) RADIO BUTTONS FOR GATES
        # --------------------
        self.gate_type = tk.StringVar(value="AND")
        
        font = ('Arial', 14)  # Increased font size for radio buttons

        self.and_button  = tk.Radiobutton(master, text="AND Gate",  variable=self.gate_type, value="AND",  command=self.update_output, font=font)
        self.or_button   = tk.Radiobutton(master, text="OR Gate",   variable=self.gate_type, value="OR",   command=self.update_output, font=font)
        self.not_button  = tk.Radiobutton(master, text="NOT Gate",  variable=self.gate_type, value="NOT",  command=self.update_output, font=font)
        self.nand_button = tk.Radiobutton(master, text="NAND Gate", variable=self.gate_type, value="NAND", command=self.update_output, font=font)
        self.nor_button  = tk.Radiobutton(master, text="NOR Gate",  variable=self.gate_type, value="NOR",  command=self.update_output, font=font)
        self.xor_button  = tk.Radiobutton(master, text="XOR Gate",  variable=self.gate_type, value="XOR",  command=self.update_output, font=font)
        self.xnor_button = tk.Radiobutton(master, text="XNOR Gate", variable=self.gate_type, value="XNOR", command=self.update_output, font=font)

        self.and_button.pack()
        self.or_button.pack()
        self.not_button.pack()
        self.nand_button.pack()
        self.nor_button.pack()
        self.xor_button.pack()
        self.xnor_button.pack()

        # --------------------
        # 6) HARDWARE LED INDICATOR (RIGHT SIDE)
        # --------------------
        self.hardware_frame = tk.Frame(master)
        self.hardware_frame.pack(pady=5, side="right")

        # Additional label for displaying the real hardware status from Arduino
        self.hardware_status_label = tk.Label(self.hardware_frame, text="Hardware Gate Output:", font=('Arial', 14, 'bold'))
        self.hardware_status_label.pack(pady=(10, 0))

        self.hardware_led_label = tk.Label(self.hardware_frame, image=self.led_off_image)
        self.hardware_led_label.pack(pady=5)

        # --------------------
        # 7) SET UP SERIAL READER
        # --------------------
        try:
            self.serial_port = serial.Serial("COM13", 9600, timeout=1)
            print("Serial port opened successfully.")
        except Exception as e:
            self.serial_port = None
            print(f"Could not open serial port. Check your connection or port name. Error: {e}")

        # Initialize a queue for thread-safe communication
        self.queue = queue.Queue()

        # If serial is open, start reading the hardware state in the background
        if self.serial_port and self.serial_port.is_open:
            self.read_hardware_status()
            self.master.after(100, self.process_queue)

        # Detect if the window is resized or switched to fullscreen
        self.master.bind("<Configure>", self.on_resize)

    # --------------------
    # SOFTWARE LOGIC UPDATE
    # --------------------
    def update_output(self):
        gate = self.gate_type.get()

        # Update gate image
        if self.gate_label and self.gate_images.get(gate):
            self.gate_label.config(image=self.gate_images[gate])

        # Send selected gate type to Arduino over serial
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(f"{gate}\n".encode())  # Send gate type as a string followed by newline

    # --------------------
    # HARDWARE STATUS READER
    # --------------------
    def read_hardware_status(self):
        """Continuously read the hardware state from Arduino and update the LED indicator."""
        def _read_serial():
            while True:
                if self.serial_port.in_waiting > 0:
                    try:
                        line = self.serial_port.readline().decode("utf-8").strip()
                        self.queue.put(line)
                    except Exception as e:
                        print(f"Error reading serial data: {e}")
                time.sleep(0.1)

        # Run the reading on a separate thread so it doesn't block the GUI
        t = threading.Thread(target=_read_serial, daemon=True)
        t.start()

    def process_queue(self):
        """Process items in the queue and update the hardware LED and input states."""
        try:
            while True:
                line = self.queue.get_nowait()
                if line == "1":
                    if self.hardware_led_label and self.led_on_image:
                        self.hardware_led_label.config(image=self.led_on_image)
                else:
                    if self.hardware_led_label and self.led_off_image:
                        self.hardware_led_label.config(image=self.led_off_image)
        except queue.Empty:
            pass
        self.master.after(100, self.process_queue)

    def on_resize(self, event):
        """Handle resizing of the window, adjust widget layout if needed."""
        width, height = event.width, event.height
        print(f"Window resized to {width}x{height}")

# Running the application
root = tk.Tk()
app = LogicGateGUI(root)
root.mainloop()
