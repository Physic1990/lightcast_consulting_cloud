# app/main.py
from fastapi import FastAPI
from typing import Union
from . import credential_handler
from . import drive

import os
import platform
import subprocess
from fastapi import HTTPException

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Team! Welcome to Lightcast Consulting Cloud API"}

# Google Drive Server Access Implementation Beginning

credential_handler.get_creds()

@app.get("/drive_data")
async def drive_data(include_trashed: bool = True):
    return drive.return_all_drive_data(include_trashed)

@app.get("/search")
async def search(file_name: str):
    return drive.search_file(file_name)

# NEED TO STILL HANDLE CASE WHERE MULTIPLE FILES ARE NAMED THE SAME
@app.get("/download")
async def download(file_id: Union[str, None] = None, file_name: Union[str, None] = None):
    return drive.download_file(file_id, file_name)

@app.get("/drive_structure")
async def drive_structure(folder_id: str = 'root'):
    return drive.return_drive_structure(folder_id)



# Google Drive Server Access Implementation End

# Open file explorer function 



#----------------------------------------------------------
# Temporary global variable for open_file_explorer function
MODELS_FOLDER = os.getcwd() # get relative path of current working directory
#----------------------------------------------------------

@app.get("/open_file_explorer", tags = ["utility"])
async def open_file_explorer():
    try:
        # Check if the path exists
        if not os.path.exists(MODELS_FOLDER):
            raise HTTPException(status_code = 400, detail = f"Path does not exist: {FILE_EXPLORER_PATH}")

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

