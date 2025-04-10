# Import modules and packages
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from google_auth_oauthlib.flow import Flow
import uuid
import json
from typing import Union
import requests
import os
from . import credential_handler # DELETE during AWS deployment
from . import drive # DELETE during AWS deployment
# from credential_handler import get_creds
# from drive import return_all_drive_data, search_file, download_file, save_file, return_drive_structure
# from credential_handler import *
# from drive import *

# Initialize FastAPI application
app = FastAPI()

# Configure CORS to allow requests from frontend
origins = [
    "http://localhost:3000",
    "https://localhost:3000"
]

# OAuth2 configuration
REDIRECT_URI = "http://localhost:8000/auth/callback"

# OAuth scopes for Google Drive
SCOPES = ["https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/docs",
          "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.metadata.readonly"]

# CORS middleware handles cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Session middleware stores authentication state and credentials 
app.add_middleware(
    SessionMiddleware,
    secret_key = "XA99wx1rfjygvR4qAvt3Kb9uqYkKrWabpZXQ16oGdoaQYqmQWRdcWZhDftdshXSh", # change as desired and add as environment variable
    session_cookie = "lightcast_consulting_cloud_app_session",
    max_age = 3600 # time in seconds the current session lasts
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

# Google Drive authentication endpoints

@app.get("/auth/login")
async def login(request: Request):
    """
    Initiates Google OAuth2 authentication flow.
    
    Parameters: request is a FastAPI Request object.
    Returns: a dictionary containing the authorization URL to redirect the user.
    """
    # Generate a random state token for cross-site request forgery (CSRF) attack prevention
    state = str(uuid.uuid4())
    request.session["state"] = state
    
    # Load OAuth credentials of client Having hard time to find cred_jason creds_path = "/var/app/current/creds.json" work with local host (Causing Issue)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(script_dir, "creds.json")
    
    # Create OAuth authentication flow with credentials and scopes
    flow = Flow.from_client_secrets_file(
        creds_path,
        scopes = SCOPES,
        redirect_uri = REDIRECT_URI
    )
    
    # Create and return authorization url which is used by frontend
    authorization_url, _ = flow.authorization_url(
        access_type = 'offline',
        state=state,
        include_granted_scopes = 'true'
    )
    return {"authorization_url": authorization_url}

@app.get("/auth/callback")
async def callback(request: Request, code: str, state: str):
    """
    Handles OAuth callback after successful Google authentication.
    
    Parameters: request FastAPI Request object;
                code is a string which is an authorization code from Google;
                state is a string which is used to verify request.
    Raises: HTTPException if state verification fails (done for security).
    Returns: A status if the authentication was successful.
    """
    # Check state to prevent CSRF attacks
    if state != request.session.get("state"):
        raise HTTPException(status_code = 400, detail = "Invalid state parameter")
    
    # Retrieve OAuth credentials of client
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(script_dir, "creds.json")
    
    # Finish OAuth flow and trade authorization code for access token 
    flow = Flow.from_client_secrets_file(
        creds_path,
        scopes = SCOPES,
        redirect_uri = REDIRECT_URI
    )
    flow.fetch_token(code = code)
    
    # Store credentials and return authentication status
    request.session["credentials"] = flow.credentials.to_json()
    return {"status": "authenticated"}

@app.get("/drive_data")
async def drive_data(request: Request, include_trashed: bool = False):
    """
    Lists all files in the user's Google Drive, requires user to be 
    authenticated to Google Drive through the app.
    
    Parameters: request is a FastAPI Request object;
                include_trashed is a boolean which signals whether to include trashed files, defaults to False.
    Returns: a list of file metadata from Google Drive.
    """
    creds = credential_handler.get_creds(request.session)
    return drive.return_all_drive_data(include_trashed, creds)

@app.get("/search")
async def search(request: Request, file_name: str):
    """
    Searches for files in the user's Google Drive by file name, requires user to be 
    authenticated to Google Drive through the app.
    
    Paramters: request is a FastAPI Request object;
               file_name is a string of the name of file to search for.
    Returns: a list of matching file metadata based on the file_name. 
    """
    creds = credential_handler.get_creds(request.session)
    return drive.search_file(file_name, creds)

@app.get("/download")
async def download(request: Request, file_id: Union[str, None] = None, file_name: Union[str, None] = None):
    """
    Downloads a file from the user's Google Drive, requires user to be 
    authenticated through the app to Google Drive.
    
    Parameters: request is a FastAPI Request object;
                file_id is a string of the ID of file to download, defaults to None;
                file_name is a string of the name to save the downloaded file as, defaults to None.
    Returns: a string of the local path of the downloaded file.
    """
    creds = credential_handler.get_creds(request.session)
    return drive.download_file(file_id, file_name, creds)

@app.post("/file_upload")
async def file_upload(request: Request, data: dict):
    """
    Uploads a file to the user's Google Drive, requires user to be 
    authenticated through the app to Google Drive.
    
    Paramters: data is a dictionary containing file_name, mimetype, and upload_filename.
    Returns: the boolean True if the file upload to the Google Drive was successful, returns False otherwise.
    """
    creds = credential_handler.get_creds(request.session)
    return drive.save_file(file_name=data.get("file_name"),mimetype=data.get("mimetype"),upload_filename=data.get("upload_filename"), creds=creds)

@app.get("/drive_structure")
async def drive_structure(request: Request, folder_id: str = "root", indent: int = 0, include_trashed: bool = False):
    """
    Retrieves the hierarchical structure of the files in the user's Google Drive, 
    requires user to be authenticated through the app to Google Drive.
    
    Parameters: request is a FastAPI Request object;
                folder_id is a string of the starting folder ID, defaults to "root";
                indent is an integer of the indentation level for the file hierarchy, defaults to 0;
                include_trashed is a boolean which signals whether to include trashed items, defaults to False.
    Returns: a list of each of the files in the drive and each element of the list contains the relevant file metadata related to the drive file structure.
    """
    creds = credential_handler.get_creds(request.session)
    return drive.return_drive_structure(folder_id, indent, include_trashed, creds)

# Local helper connection and its endpoints

import logging
logging.basicConfig(level=logging.DEBUG)

LOCAL_HELPER_URL = "http://127.0.0.1:9000"

@app.post("/run-local-model")
async def run_local_model(request: Request, data: dict):
    file_id = data.get("file_id")
    script = data.get('script')
    creds = credential_handler.get_creds(request.session)
    if not file_id or not script:
        raise HTTPException(status_code=400, detail="File ID and script selection are required.")

    try:
        file_path = drive.download_file(file_id, creds=creds)
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

@app.get("/file_download")
async def file_download(file_path: str):
    try:
        return FileResponse(file_path)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        