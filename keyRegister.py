try:
    from boLogger import CustomLog
    import tkinter as tk
    from pynput import keyboard
    import threading
    import time
except ImportError as e:
    input(e)
except ImportWarning as e:
    input(e)

length = 30
mylogger = CustomLog(length)
#mylogger.set_default(bold=True, color='BRed', title="Extra", underlined=False) # Example usage for my package


class KeyCounterApp:
    def __init__(self, root):
        mylogger.info("Initializing")
        
        self.root = root
        self.root.title("Key Press Counter")
        self.root.geometry("200x100")
        self.root.resizable(False, False)

        self.z_counter = 0
        self.x_counter = 0
        self.bar_length = 300
        self.block_width = 30
        self.blocks = []
        self.keys_held = {"z": False, "x": False}
        self.current_block = {"z": None, "x": None}  # Track the most recent block for each key

        # Bar for key press visualization
        self.bar_canvas = tk.Canvas(root, height=20, bg="white", highlightthickness=0)
        self.bar_canvas.pack(pady=10, fill="x", padx=10)

        # Counters frame
        self.counters_frame = tk.Frame(root)
        self.counters_frame.pack(pady=10)

        # Z counter
        self.z_label = tk.Label(
            self.counters_frame, text="Z: 0", font=("Helvetica", 10), fg="blue"
        )
        self.z_label.grid(row=0, column=0, padx=10)

        # X counter
        self.x_label = tk.Label(
            self.counters_frame, text="X: 0", font=("Helvetica", 10), fg="red"
        )
        self.x_label.grid(row=0, column=1, padx=10)

        # Start block movement thread
        self.running = True
        self.block_movement_thread = threading.Thread(target=self.move_blocks, daemon=True)
        self.block_movement_thread.start()

        # Start the listener thread
        self.listener_thread = threading.Thread(target=self.start_key_listener, daemon=True)
        self.listener_thread.start()
        
        mylogger.success("App successfully started")

    def create_block(self, color):
        # Create a new block at the start of the bar
        block = {
            "id": self.bar_canvas.create_rectangle(
                0, 0, self.block_width, 20, fill=color, outline='white'
            ),
            "position": 0,
            "width": self.block_width,
            "color": color,
            "moving": True,
        }
        self.blocks.append(block)
        return block

    def move_blocks(self):
        while self.running:
            for block in list(self.blocks):  # Use a copy of the list to avoid iteration issues
                if block["moving"]:
                    block["position"] += 5
                if block["position"] >= self.bar_length:
                    self.bar_canvas.delete(block["id"])
                    self.blocks.remove(block)
                else:
                    self.bar_canvas.coords(
                        block["id"],
                        block["position"], 0,
                        block["position"] + block["width"], 20
                    )
            time.sleep(0.05)

    def expand_block(self, key):
        block = self.current_block[key]
        if block:
            block["width"] += 5
            block["moving"] = False

    def increment_z(self):
        self.z_counter += 1
        self.z_label.config(text=f"Z: {self.z_counter}")
        self.current_block["z"] = self.create_block("blue")

    def increment_x(self):
        self.x_counter += 1
        self.x_label.config(text=f"X: {self.x_counter}")
        self.current_block["x"] = self.create_block("red")

    def on_press(self, key):
        try:
            if key.char == 'z' and not self.keys_held['z']:
                self.keys_held['z'] = True
                self.increment_z()

            elif key.char == 'x' and not self.keys_held['x']:
                self.keys_held['x'] = True
                self.increment_x()

        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if key.char in ['x', 'z']:
                if key.char == 'z':
                    self.keys_held['z'] = False
                    if self.current_block['z']:
                        self.current_block['z']["moving"] = True
                        self.current_block['z'] = None
                elif key.char == 'x':
                    self.keys_held['x'] = False
                    if self.current_block['x']:
                        self.current_block['x']["moving"] = True
                        self.current_block['x'] = None
                
                mylogger.custom_log(
                    f"User pressed {key.char}", 
                    title="Key-Press", 
                    color='Red' if key.char == 'x' else 'Blue', 
                    bold=False, 
                    underlined=False
                )
        except AttributeError:
            pass

    def start_key_listener(self):
        # Start listening to global key presses
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            while self.running:
                if self.keys_held['z']:
                    self.expand_block('z')
                if self.keys_held['x']:
                    self.expand_block('x')
                time.sleep(0.05)

    def stop(self):
        mylogger.warning("Bye bye")
        self.running = False

# Create the main window
root = tk.Tk()
app = KeyCounterApp(root)

# Handle graceful exit
root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
root.mainloop()
