from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
import requests
import os
from . import credential_handler
from . import drive
import hashlib

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"message": "Hello, Team! Welcome to Lightcast Consulting Cloud API"}

team_members = [
    {"id": "1", "item": "Ian King"},
    {"id": "2", "item": "Shashwot Niraula"},
    {"id": "3", "item": "Andrew Plum"},
    {"id": "4", "item": "Bibek Sharma"},
    {"id": "5", "item": "Caleb Mouat"}
]

@app.get("/members", tags=["members"])
async def get_members() -> dict:
    return { "data": team_members }

@app.post("/members", tags=["members"])
async def add_member(member: dict) -> dict:
    team_members.append(member)
    return {"data": { "Member added." }}

@app.delete("/members/{id}", tags=["members"])
async def delete_member(memberID: int) -> dict:
    for member in team_members:
        if int(member["id"]) == memberID:
            team_members.remove(member)
            return {"data": f"Member with id {memberID} has been removed."}
    return {"data": f"Member with id {memberID} not found"}

# Google Drive Server Access Implementation
credential_handler.get_creds()

@app.get("/drive_data")
async def drive_data(include_trashed: bool = True):
    return drive.return_all_drive_data(include_trashed)

@app.get("/search")
async def search(file_name: str):
    return drive.search_file(file_name)

@app.get("/download")
async def download(file_id: Union[str, None] = None, file_name: Union[str, None] = None):
    return drive.download_file(file_id, file_name)

import logging
logging.basicConfig(level=logging.DEBUG)

LOCAL_HELPER_URL = "http://127.0.0.1:9000/upload-file"

PROCESSED_FOLDER = "backend/got_from_local_helper_processed"
os.makedirs(PROCESSED_FOLDER, exist_ok=True)  # Ensure processed folder exists

@app.post("/run-local-model")
async def run_local_model(data: dict):
    file_id = data.get("file_id")
    if not file_id:
        raise HTTPException(status_code=400, detail="File ID is required.")

    try:
        file_path = drive.download_file(file_id)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Failed to download file.")

        print(f"File downloaded successfully: {file_path}")

        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(LOCAL_HELPER_URL, files=files)
        
        response.raise_for_status()
        processed_data = response.json()

        processed_filename = os.path.basename(file_path)
        processed_file_path = os.path.join(PROCESSED_FOLDER, processed_filename)

        with open(processed_file_path, "w") as processed_file:
            processed_file.write(processed_data.get("processed_text", ""))

        print(f"Processed file saved: {processed_file_path}")

        #Generate hash for unique identification of file
        h = hashlib.sha1()

        #Open file for binary mode reading
        with open(processed_file_path,'rb') as file:

            #Loop through file
            chunk = 0
            while chunk != b'':
                #Read 1024-byte chunk
                chunk = file.read(1024)
                h.update(chunk)

        return {"processed_file": processed_file_path, "hash": h.hexdigest()}

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        # Forward the request to the local helper app
        # response = requests.post("http://host.docker.internal:9000/run-model", timeout=5)
        # response = requests.post("http://localhost:9000/run-model")
        # print("Signal sent!")
        # response.raise_for_status()  # Raise an error if the request fails
        # returned_response = response.json()
        # print(returned_response)
        # return returned_response  # Return the response from the local helper
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur
        raise HTTPException(status_code=500, detail=f"Error connecting to local helper: {str(e)}")

@app.get("/drive_structure")
async def drive_structure(folder_id: str = 'root'):
    return drive.return_drive_structure(folder_id)

@app.post("/file_upload")
async def file_upload(data: dict):
    print(data)
    file_name = data.get("file_name")
    mimetype = data.get("mimetype")
    upload_filename = data.get("upload_filename")
    resumable = data.get("resumable")
    chunksize = data.get("chunksize")
    if not (file_name and mimetype and upload_filename):
        raise HTTPException(status_code=400, detail="File name, mimetype, and upload name are required.")
    if chunksize is None:
        chunksize=262144
    if resumable is None:
        return drive.save_file(file_name, mimetype, upload_filename, resumable=True, chunksize=chunksize)

    return drive.save_file(file_name, mimetype, upload_filename, resumable, chunksize)