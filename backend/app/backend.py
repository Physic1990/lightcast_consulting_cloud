import os
import platform
import subprocess
from fastapi import FastAPI, HTTPException

def open_file_explorer_request(MODELS_FOLDER):
    try:
        # Check if the path exists
        if not os.path.exists(MODELS_FOLDER):
            raise HTTPException(status_code = 400, detail = f"Path does not exist: {MODELS_FOLDER}")

        # Open the file explorer based on the operating system
        if platform.system() == "Windows": # Windows
            os.startfile(MODELS_FOLDER)
        elif platform.system() == "Darwin": # macOS
            subprocess.run(["open", MODELS_FOLDER])
        else: # Linux and others
            subprocess.run(["xdg-open", MODELS_FOLDER])

        return f"File explorer opened at: {MODELS_FOLDER}"

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Failed to open file explorer: {str(e)}")
    return
