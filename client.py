import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar
import websocket
import threading
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class RingBuffer:
    def __init__(self):
        self.size = 1000
        self.values = [None] * self.size
        self.timestamps = [None] * self.size
        self.index = 0

    def push_front(self, value, timestamp):
        self.values[self.index] = value
        self.timestamps[self.index] = timestamp
        self.index = (self.index + 1) % self.size

    def get_data(self):
        values = self.values[self.index:] + self.values[:self.index]
        timestamps = self.timestamps[self.index:] + self.timestamps[:self.index]
        return values, timestamps

    def get_front(self, count=1):
        if count > self.size:
            count = self.size
        start_index = (self.index - count) % self.size
        if start_index < self.index:
            return list(zip(self.timestamps[start_index:self.index], self.values[start_index:self.index]))
        else:
            return list(zip(self.timestamps[start_index:], self.values[start_index:])) + \
                   list(zip(self.timestamps[:self.index], self.values[:self.index]))

class WebSocketApp:
    def __init__(self, master):
        self.master = master
        self.master.title("WebSocket Client")
        self.master.geometry("800x600")
        
        self.uri_label = tk.Label(master, text="WebSocket URI:")
        self.uri_label.pack(pady=10)
        
        # Frame for URI entry and connection status
        uri_frame = tk.Frame(master)
        uri_frame.pack(pady=10)

        self.uri_entry = tk.Entry(uri_frame, width=70)
        self.uri_entry.pack(side=tk.LEFT)

        self.uri_entry.insert(0, "ws://localhost:8765/ws")

        # Green checkmark for connection confirmation
        self.connection_status_label = tk.Label(uri_frame, text="", font=("Arial", 12), fg="green")
        self.connection_status_label.pack(side=tk.LEFT, padx=(10, 0))  # Add some space to the left

        # Frame for Buttons
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)
        
        # Start/Stop Button
        self.start_stop_button = tk.Button(button_frame, text="Start", command=self.toggle_connection, width=20, height=2)
        self.start_stop_button.grid(row=0, column=0, padx=10)
        
        # Show Last 100 Data Points Button
        self.show_data_button = tk.Button(button_frame, text="Show Last 100 Data Points", command=self.show_last_data, width=20, height=2)
        self.show_data_button.grid(row=0, column=1, padx=10)

        # Show Latest Data Point Button
        self.show_latest_data_button = tk.Button(button_frame, text="Show Latest Data Point", command=self.show_latest_data, width=20, height=2)
        self.show_latest_data_button.grid(row=0, column=2, padx=10)
        
        # Label to display the latest data point below the buttons
        self.latest_data_label = tk.Label(master, text="", font=("Arial", 12))
        self.latest_data_label.pack(pady=10)
        
        # Plot Area
        self.figure, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvasTkAgg(self.figure, master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.ring_buffer = RingBuffer()
        self.update_counter = 0

        self.connected = False
        self.thread = None
        self.running = False  # Flag to control the thread

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            timestamp, value = data['timestamp'], data['value']
            dt = datetime.fromisoformat(timestamp)
            timestamp_unix = dt.timestamp()

            self.ring_buffer.push_front(value, timestamp_unix)
            self.update_counter += 1

            if self.update_counter == 100:
                self.update_counter = 0
                self.update_plot()
        except (json.JSONDecodeError, KeyError):
            print("Fehler beim Verarbeiten der Nachricht:", message)

    def on_error(self, ws, error):
        print("WebSocket Fehler:", error)

    def on_close(self, ws):
        print("WebSocket Verbindung geschlossen")
        self.connected = False
        self.running = False  # Set running to False when connection closes
        self.connection_status_label.config(text="")  # Clear connection status

    def on_open(self, ws):
        print("WebSocket Verbindung hergestellt")
        self.connected = True
        self.running = True  # Set running to True when connection opens
        self.connection_status_label.config(text="✔️ Verbunden")  # Update connection status

    def run(self):
        uri = self.uri_entry.get()
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(uri,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        self.ws = ws  # Store the WebSocket instance for sending messages
        ws.run_forever()

    def toggle_connection(self):
        if self.connected:
            self.connected = False
            self.start_stop_button.config(text="Start")
            if self.thread:
                self.running = False  # Signal the thread to stop
                self.ws.close()  # Close the WebSocket connection
                self.thread.join()  # Wait for the thread to finish
            self.connection_status_label.config(text="")  # Clear connection status
        else:
            uri = self.uri_entry.get()
            if not uri:
                messagebox.showerror("Fehler", "Bitte geben Sie eine gültige WebSocket-URI ein.")
                return

            self.thread = threading.Thread(target=self.run)
            self.thread.start()
            self.start_stop_button.config(text="Stop")

    def update_plot(self):
        self.ax.clear()

        values, timestamps = self.ring_buffer.get_data()

        valid_indices = [i for i, val in enumerate(values) if val is not None]
        valid_values = [values[i] for i in valid_indices]
        valid_timestamps = [timestamps[i] for i in valid_indices]

        self.ax.plot(valid_timestamps, valid_values, marker='o')
        self.ax.set_title("Empfangene Werte")
        self.ax.set_xlabel("Zeitstempel")
        self.ax.set_ylabel("Wert")

        self.ax.xaxis.set_major_formatter(plt.FuncFormatter(self.format_unix_timestamps))
        self.canvas.draw()

    def format_unix_timestamps(self, x, pos):
        return datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S")

    def show_last_data(self):
        data = self.ring_buffer.get_front(100)

        # Create a new Toplevel window
        top = tk.Toplevel(self.master)
        top.title("Letzte 100 Datenpunkte")
        top.geometry("500x400")
        top.resizable(True, True)

        scrollbar = Scrollbar(top)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = Listbox(top, width=80, height=20, yscrollcommand=scrollbar.set)
        listbox.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=listbox.yview)

        for timestamp, value in data:
            if timestamp and value:
                formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                listbox.insert(tk.END, f"{formatted_time} - {value}")

    def show_latest_data(self):
        latest_data = self.ring_buffer.get_front(1)
        if latest_data:
            timestamp, value = latest_data[-1]
            formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

            self.latest_data_label.config(text=f"Letzter Datensatz:\nZeit: {formatted_time}\nWert: {value}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WebSocketApp(root)
    root.mainloop()
