import os
import pickle
import platform
import subprocess
import time
import pandas as pd
import tkinter as tk
from tkinter import scrolledtext, filedialog
import threading
from flask import Flask, jsonify, request

app = Flask(__name__)

UPLOAD_FOLDER = "received_from_backend"
PROCESSED_FOLDER = "processed_files"
# PROCESSED_FOLDER = os.path.join("..", "backend", "got_from_local_helper_processed")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

#Where are local models stored?
MODELS_FOLDER = "example_models"

#Where is the selected model pickled?
MODEL_STORAGE = os.path.join('pickles','model_pickle')
#Where is the selected data pickled?
DATA_STORAGE = os.path.join('pickles', 'data_pickle')

#Open file explorer to select model
def open_file_explorer_request():
    selected_file = filedialog.askopenfilename(initialdir=(os.getcwd() + MODELS_FOLDER), title="Select a File", defaultextension=".py")

    if(selected_file.lower().endswith('.py')):
        update_terminal_log(f"Selected Python file {selected_file}")
        with open(MODEL_STORAGE, 'wb+') as file:
            pickle.dump(selected_file, file)
    else:
        update_terminal_log(f"No valid file selected; please select a .py file.")
        return

#Save processed file on disk
def save_processed():
    if not active_data:
        return
    processed_filename = f"processed_{os.path.basename(active_data)}"
    processed_file_path = os.path.join(PROCESSED_FOLDER, processed_filename)
    if not os.path.exists(processed_file_path):
        return

    file = filedialog.asksaveasfilename(defaultextension='.xlsx')
    update_terminal_log(file)
    if file is None:
        return

    df = pd.read_excel(processed_file_path, sheet_name=None)

    with pd.ExcelWriter(file, engine="openpyxl") as writer:
        for sheet, data in df.items():
            data.to_excel(writer, sheet_name=sheet, index=False)
    
#Cleanup for when local helper is closed
def on_closing():
    if os.path.exists(MODEL_STORAGE):
        os.remove(MODEL_STORAGE)
    if os.path.exists(DATA_STORAGE):
        os.remove(DATA_STORAGE)

    root.destroy()

# Function to update GUI terminal log
def update_terminal_log(message):
    global terminal
    terminal.insert(tk.END, message + "\n")
    terminal.see(tk.END)  # Auto-scroll to latest message

# Function to process Excel files
def process_excel_file():
    global active_data

    #Check that both data and a model have been selected
    data_selected = (os.path.getsize(DATA_STORAGE) > 0)
    model_selected = (os.path.getsize(MODEL_STORAGE) > 0)
    if not(data_selected and model_selected):
        update_terminal_log("Must select data and model.")
        return

    try:
        start_time = time.time()
        update_terminal_log(f"Processing started for: {active_data}")

        python_model = None
        with open(MODEL_STORAGE, 'rb') as file:
            python_model = pickle.load(file)
        if python_model is None:
            return

        processed_filename = f"processed_{os.path.basename(active_data)}"
        processed_file_path = os.path.join(PROCESSED_FOLDER, processed_filename)

        #Run the model.py subprocess on active_data
        results = subprocess.run(["python", python_model, active_data, processed_file_path], capture_output=True, text=True)

        #Uncomment the following to debug in the local helper terminal
        # update_terminal_log(results.stdout)
        # update_terminal_log(results.stderr)

        end_time = time.time()
        update_terminal_log(f"Processed file saved: {processed_file_path}")
        update_terminal_log(f"Total processing time: {end_time - start_time:.2f} seconds")

        return {"processed_file": processed_file_path}

    except Exception as e:
        update_terminal_log(f"Error processing Excel file: {str(e)}")
        return {"error": f"Failed to process file: {str(e)}"}

# Function to process files of different types
def run_model(file_path):
    global active_data

    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == ".xlsx":
        active_data = file_path
        with open(DATA_STORAGE, 'wb+') as file:
            pickle.dump(active_data, file)
        # return process_excel_file(file_path)
        return {"processed_file": file_path}
    else:
        active_data = None
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
        return jsonify({"error": "Something went wrong in file delivery."})

    return jsonify({"success": "File delivered."})

# Start Flask API in a separate thread
def start_flask():
    app.run(port=9000, debug=True, use_reloader=False)

# GUI Application
def start_gui():
    global terminal

    terminal = scrolledtext.ScrolledText(root, width=80, height=20, wrap=tk.WORD)
    terminal.pack()

    save_button = tk.Button(root, text="Save data as...", command=save_processed)
    save_button.pack(side=tk.LEFT)

    run_button = tk.Button(root, text="Run Model", command=process_excel_file)
    run_button.pack(side=tk.RIGHT)

    models_button = tk.Button(root, text="Select Model", command=open_file_explorer_request)
    models_button.pack(side=tk.RIGHT)

    root.mainloop()

root = tk.Tk()
root.title("Local Helper GUI")
root.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == "__main__":
    #Store currently selected data
    global active_data
    active_data: str | None = None

    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Start GUI on the main thread
    start_gui()