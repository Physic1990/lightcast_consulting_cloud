import os
import pickle
import platform
import re
import subprocess
import time
import pandas as pd
import tkinter as tk
from tkinter import scrolledtext, filedialog
import threading
from flask import Flask, jsonify, request

app = Flask(__name__)

#Where is the selected model pickled?
MODEL_STORAGE = os.path.join('pickles','model_pickle')
#Where is the selected data pickled?
DATA_STORAGE = os.path.join('pickles', 'data_pickle')

#Open file explorer to select model
def open_file_explorer_request():
    selected_folder = filedialog.askdirectory(initialdir=(os.getcwd()), title="Select a Folder", )

    if(selected_folder):
        update_terminal_log(f"Selected Python script folder {selected_folder}")
        with open(MODEL_STORAGE, 'wb+') as file:
            pickle.dump(selected_folder, file)
    else:
        update_terminal_log(f"No valid folder selected.")
        return

#Cleanup for when local helper is closed
def on_closing():
    if os.path.exists(DATA_STORAGE):
        os.remove(DATA_STORAGE)

    root.destroy()

# Function to update GUI terminal log
def update_terminal_log(message):
    global terminal
    terminal.insert(tk.END, message + "\n")
    terminal.see(tk.END)  # Auto-scroll to latest message

# Function to process Excel files
def process_excel_file(run_script: str):
    global active_data

    #Check that both data and a model have been selected
    data_selected = (os.path.getsize(DATA_STORAGE) > 0)
    model_selected = (os.path.getsize(MODEL_STORAGE) > 0)
    if not(data_selected and model_selected):
        update_terminal_log("Must select data and then model.")
        return

    #Check that the active data exists
    if(not os.path.exists(active_data)):
        update_terminal_log(f"{active_data} does not exist on the local system.")
        return

    try:
        start_time = time.time()
        update_terminal_log(f"Processing started for: {active_data}")

        with open(MODEL_STORAGE, 'rb+') as file:
            python_model = os.path.join(pickle.load(file), run_script)

        #Run the model.py subprocess on active_data
        subprocess.run(["python", python_model, active_data], capture_output=True, text=True)

        #Uncomment the following to debug in the local helper terminal
        # update_terminal_log(results.stdout)
        # update_terminal_log(results.stderr)

        end_time = time.time()
        update_terminal_log(f"Total processing time: {end_time - start_time:.2f} seconds")

        return {"processed_file": active_data}

    except Exception as e:
        update_terminal_log(f"Error processing Excel file: {str(e)}")
        return {"error": f"Failed to process file: {str(e)}"}

# Function to process files of different types
def run_model(file_path, model_name):
    global active_data

    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    reg_exp = re.compile(".*\\.xl..?")
    if re.match(reg_exp, file_extension):
        active_data = file_path
        with open(DATA_STORAGE, 'wb+') as file:
            pickle.dump(active_data, file)
        process_excel_file(model_name)
        return {"processed_file": file_path}
    else:
        active_data = None
        update_terminal_log(f"Unsupported file type: {file_extension}")
        return {"error": f"Unsupported file type: {file_extension}"}

# API route to receive file uploads
@app.route("/upload-file", methods=["POST"])
def upload_file():
    file_path = request.json['file']
    py_script = request.json['script']

    update_terminal_log(f"Received file for processing: {file_path}")

    response = run_model(os.path.join("local_data", file_path), py_script)

    if "error" in response:
        update_terminal_log(f"Error: {response['error']}")
        return jsonify({"error": "Something went wrong in file delivery."})

    return jsonify({"success": "File delivered."})

@app.route("/scripts-folder", methods=["GET"])
def get_scripts_folder():
    #Make sure the folder is selected
    if(os.path.getsize(MODEL_STORAGE) <= 0):
        return {"error": "No script folder selected."}
    
    with open(MODEL_STORAGE, "rb+") as file:
        scripts_folder = pickle.load(file)
    
    return os.listdir(scripts_folder) 

# Start Flask API in a separate thread
def start_flask():
    app.run(port=9000, debug=True, use_reloader=False)

# GUI Application
def start_gui():
    global terminal

    terminal = scrolledtext.ScrolledText(root, width=80, height=20, wrap=tk.WORD)
    terminal.pack()

    models_button = tk.Button(root, text="Select Model Folder", command=open_file_explorer_request)
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