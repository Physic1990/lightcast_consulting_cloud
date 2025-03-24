from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from google_auth_oauthlib.flow import Flow
from typing import Union
import uuid
import os
import requests
import platform
import subprocess
from . import credential_handler
from . import drive
from . import backend

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "localhost:3000"
]

# Cross-Origin Resource Sharing middleware
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
    secret_key = "your-secret-key-keep-it-safe",
    session_cookie = "session_cookie",
    max_age = 60 # time in seconds the current session lasts
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

# OAuth2 configuration
#GOOGLE_CLIENT_ID = "client-id-from-creds.json"
#GOOGLE_CLIENT_SECRET = "client-secret-from-creds.json"
REDIRECT_URI = "http://localhost:8000/auth/callback"
SCOPES = ["https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/docs",
          "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.metadata.readonly"]

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl = "https://accounts.google.com/o/oauth2/auth",
    tokenUrl = "https://oauth2.googleapis.com/token",
    scopes = {"drive": " ".join(SCOPES)}
)

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

# Google Drive Server Access Implementation

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

LOCAL_HELPER_URL = "http://127.0.0.1:9000/upload-file"

PROCESSED_FOLDER = "got_from_local_helper_processed"
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

        return {"processed_file": processed_file_path}

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        # Forward the request to the local helper app
        # response = requests.post("http://host.docker.internal:9000/run-model", timeout=5)
        response = requests.post("http://localhost:9000/run-model")
        print("Signal sent!")
        response.raise_for_status()  # Raise an error if the request fails
        returned_response = response.json()
        print(returned_response)
        return returned_response  # Return the response from the local helper
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur
        raise HTTPException(status_code=500, detail=f"Error connecting to local helper: {str(e)}")

@app.get("/drive_structure")
async def drive_structure(request: Request, folder_id: str = 'root', indent: int = 0, include_trashed: bool = False):
    creds = credential_handler.get_creds(request.session)
    return drive.return_drive_structure(folder_id, indent, include_trashed, creds)

#----------------------------------------------------------
# Temporary global variable for open_file_explorer function
MODELS_FOLDER = os.getcwd() # get relative path of current working directory
#----------------------------------------------------------

@app.get("/open_file_explorer", tags = ["utility"])
async def open_file_explorer():
    return backend.open_file_explorer_request(MODELS_FOLDER)
