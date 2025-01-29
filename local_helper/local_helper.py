import tkinter as tk
from tkinter import scrolledtext
import time
from flask import Flask, jsonify, request
import threading

app = Flask(__name__)

# Function to simulate running the model
def run_model(hardcoded_text):
    # Simulate processing with logging
    result = hardcoded_text.upper()
    return {
        "input_text": hardcoded_text,
        "processed_text": result,
        "status": "Model execution completed!"
    }

# Flask route to trigger the model
@app.route("/run-model", methods=["POST"])
def run_model_api():
    hardcoded_text = "hello world"  # Hardcoded text
    response = run_model(hardcoded_text)
    return jsonify(response)

# Start Flask in a separate thread
def start_flask():
    app.run(port=9000, debug=True)

# GUI Application
def start_gui():
    def on_run_model_click():
        terminal.delete(1.0, tk.END)  # Clear the terminal
        terminal.insert(tk.END, "Running model locally...\n")
        response = run_model("hello world")
        terminal.insert(tk.END, f"Input Text: {response['input_text']}\n")
        terminal.insert(tk.END, f"Processed Text: {response['processed_text']}\n")
        terminal.insert(tk.END, f"{response['status']}\n")

    root = tk.Tk()
    root.title("Local Helper")

    # Terminal area to display outputs
    terminal = scrolledtext.ScrolledText(root, width=60, height=20, wrap=tk.WORD)
    terminal.pack()

    # Run Model button
    run_button = tk.Button(root, text="Run Model", command=on_run_model_click)
    run_button.pack()

    root.mainloop()

# Run Flask server and GUI concurrently
if __name__ == "__main__":
    # threading.Thread(target=start_flask, daemon=True).start()
    threading.Thread(target=start_gui).start()
    start_flask()
    # start_gui()
