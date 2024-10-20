# app/main.py
from fastapi import FastAPI
from typing import Union
from . import credential_handler
from . import drive

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

# Google Drive Server Access Implementation End