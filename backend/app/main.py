from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from google_auth_oauthlib.flow import Flow
import uuid
import json
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

# OAuth2 configuration
REDIRECT_URI = "http://localhost:8000/auth/callback"

SCOPES = ["https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/docs",
          "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.metadata.readonly"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key = "XA99wx1rfjygvR4qAvt3Kb9uqYkKrWabpZXQ16oGdoaQYqmQWRdcWZhDftdshXSh", # Change as desired and add as environment variable
    session_cookie = "lightcast_consulting_cloud_app_session",
    max_age = 3600 # Time in seconds the current session lasts
)

@app.get("/")
def read_root():
    return {"message": "Hello, Team! Welcome to the Lightcast Consulting Cloud API"}

team_members = [
    {"id": "1", "item": "Ian King"},
    {"id": "2", "item": "Shashwot Niraula"},
    {"id": "3", "item": "Andrew Plum"},
    {"id": "4", "item": "Bibek Sharma"},
    {"id": "5", "item": "Caleb Mouat"}
]

# ---------- BEGIN EXAMPLE FUNCTIONS ----------
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

# ---------- END EXAMPLE FUNCTIONS ----------

# Drive authentication
@app.get("/auth/login")
async def login(request: Request):
    state = str(uuid.uuid4())
    request.session["state"] = state
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(script_dir, "creds.json")
    
    flow = Flow.from_client_secrets_file(
        creds_path,
        scopes = SCOPES,
        redirect_uri = REDIRECT_URI
    )
    authorization_url, _ = flow.authorization_url(
        access_type = 'offline',
        state=state,
        include_granted_scopes = 'true'
    )
    return {"authorization_url": authorization_url}

@app.get("/auth/callback")
async def callback(request: Request, code: str, state: str):
    if state != request.session.get("state"):
        raise HTTPException(status_code = 400, detail = "Invalid state parameter")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(script_dir, "creds.json")
    
    flow = Flow.from_client_secrets_file(
        creds_path,
        scopes = SCOPES,
        redirect_uri = REDIRECT_URI
    )
    flow.fetch_token(code = code)
    
    request.session["credentials"] = flow.credentials.to_json()
    return {"status": "authenticated"}  

@app.get("/drive_data")
async def drive_data(request: Request, include_trashed: bool = False):
    creds = credential_handler.get_creds(request.session)
    return drive.return_all_drive_data(include_trashed, creds)

@app.get("/search")
async def search(request: Request, file_name: str):
    creds = credential_handler.get_creds(request.session)
    return drive.search_file(file_name, creds)

@app.get("/download")
async def download(request: Request, file_id: Union[str, None] = None, file_name: Union[str, None] = None):
    creds = credential_handler.get_creds(request.session)
    return drive.download_file(file_id, file_name, creds)

import logging
logging.basicConfig(level=logging.DEBUG)

LOCAL_HELPER_URL = "http://127.0.0.1:9000"

@app.post("/run-local-model")
async def run_local_model(data: dict):
    file_id = data.get("file_id")
    script = data.get('script')
    if not file_id or not script:
        raise HTTPException(status_code=400, detail="File ID and script selection are required.")

    try:
        file_path = drive.download_file(file_id)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Failed to download file.")

        print(f"File downloaded successfully: {file_path}")
        
        #SHOULD BE MODIFIED TO GET FULL FILE PATH FROM FRONTEND
        file_data = {"file": os.path.basename(file_path), 'script': script}
        response = requests.post(f"{LOCAL_HELPER_URL}/upload-file", json=file_data)

        response.raise_for_status()
        processed_data = response.json()

        return {"success": processed_data}

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur
        raise HTTPException(status_code=500, detail=f"Error connecting to local helper: {str(e)}")

@app.get("/script_folder")
async def get_scripts_folder():
    response = requests.get(f"{LOCAL_HELPER_URL}/scripts-folder")
    return response.json()

@app.get("/drive_structure")
async def drive_structure(request: Request, folder_id: str = 'root', indent: int = 0, include_trashed: bool = False):
    creds = credential_handler.get_creds(request.session)
    return drive.return_drive_structure(folder_id, indent, include_trashed, creds)

#Upload processed file from application to Drive
@app.post("/file_upload")
async def file_upload(data: dict):
    creds = credential_handler.get_creds(request.session)
    return drive.save_file(file_name=data.get("file_name"),mimetype=data.get("mimetype"),upload_filename=data.get("upload_filename"), creds=creds)

#Save file from application to local device
@app.get("/file_download")
async def file_download(file_path: str):
    try:
        return FileResponse(loc_file_path)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        