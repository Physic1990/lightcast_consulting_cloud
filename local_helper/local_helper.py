import os
import time
import pandas as pd
import tkinter as tk
from tkinter import scrolledtext
import threading
from flask import Flask, jsonify, request

app = Flask(__name__)

UPLOAD_FOLDER = "local_helper/received_from_backend"
# PROCESSED_FOLDER = "local_helper/processed_files"
PROCESSED_FOLDER = "../backend/got_from_local_helper_processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Function to update GUI terminal log
def update_terminal_log(message):
    global terminal
    terminal.insert(tk.END, message + "\n")
    terminal.see(tk.END)  # Auto-scroll to latest message

# Function to process Excel files
def process_excel_file(file_path):
    try:
        start_time = time.time()
        update_terminal_log(f"Processing started for: {file_path}")

        df = pd.read_excel(file_path, sheet_name=None)
        processed_data = {}

        for sheet_name, data in df.items():
            update_terminal_log(f"Processing sheet: {sheet_name} ({data.shape[0]} rows, {data.shape[1]} columns)")

            if data.shape[1] >= 2:
                data["Sum"] = data.iloc[:, 0] + data.iloc[:, 1]
                data["Product"] = data.iloc[:, 0] * data.iloc[:, 1]
                data["Mean"] = data.iloc[:, :2].mean(axis=1)

                processed_data[sheet_name] = data
                update_terminal_log(f"Completed processing sheet: {sheet_name}")
            else:
                update_terminal_log(f"Skipping sheet {sheet_name}, not enough columns.")

        processed_filename = f"processed_{os.path.basename(file_path)}"
        processed_file_path = os.path.join(PROCESSED_FOLDER, processed_filename)

        with pd.ExcelWriter(processed_file_path, engine="openpyxl") as writer:
            for sheet, data in processed_data.items():
                data.to_excel(writer, sheet_name=sheet, index=False)

        end_time = time.time()
        update_terminal_log(f"Processed file saved: {processed_file_path}")
        update_terminal_log(f"Total processing time: {end_time - start_time:.2f} seconds")

        return {"processed_file": processed_file_path}

    except Exception as e:
        update_terminal_log(f"Error processing Excel file: {str(e)}")
        return {"error": f"Failed to process file: {str(e)}"}

# Function to process files of different types
def run_model(file_path):
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == ".xlsx":
        return process_excel_file(file_path)
    else:
        update_terminal_log(f"Unsupported file type: {file_extension}")
        return {"error": f"Unsupported file type: {file_extension}"}

# API route to receive file uploads
@app.route("/upload-file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    update_terminal_log(f"Received file for processing: {file_path}")

    response = run_model(file_path)

    if "error" in response:
        update_terminal_log(f"Error: {response['error']}")
    else:
        update_terminal_log(f"Processed file available at: {response['processed_file']}")

    return jsonify(response)

# Start Flask API in a separate thread
def start_flask():
    app.run(port=9000, debug=True, use_reloader=False)

# GUI Application
def start_gui():
    global terminal
    root = tk.Tk()
    root.title("Local Helper GUI")

    terminal = scrolledtext.ScrolledText(root, width=80, height=20, wrap=tk.WORD)
    terminal.pack()

    run_button = tk.Button(root, text="Waiting for Files...", state=tk.DISABLED)
    run_button.pack()

    root.mainloop()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Start GUI on the main thread
    start_gui()
