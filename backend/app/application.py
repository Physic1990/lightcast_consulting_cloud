# Import modules and packages
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
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

# Google Drive authentication endpoints

@app.get("/auth/login")
async def login(request: Request):
    """
    Initiates Google OAuth2 authentication flow.
    
    Parameters: request is a FastAPI Request object.
    Returns: a dictionary containing the authorization URL to redirect the user.
    """
    if "credentials" in request.session:
        del request.session["credentials"]
    
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
        include_granted_scopes = 'true',
        prompt='consent'
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
    
@app.get("/is_authenticated")
async def is_authenticated(request: Request):
    """
    Checks if the user is authenticated.

    Parameters: request is a FastAPI Request object.
    Returns: a dictionary indicating whether the user is authenticated.
    """
    try:
        credential_handler.get_creds(request.session)
        return {"status": "authenticated"}  # User is authenticated
    except HTTPException:
        return {"status": "not authenticated"}  # User is not authenticated
    
@app.get("/test/delete_creds")
async def test_delete_creds(request: Request):
    """
    Test endpoint to delete credentials stored in session.
    
    Parameters: request is a FastAPI Request object.
    Returns: A status on if expiring the token was successful.
    """
    if "credentials" in request.session:
        del request.session["credentials"]
        return {"status": "Credentials found and deleted"}
    else:
        return {"status": "No credentials found"}

@app.get("/test/expire_token")
async def test_expire_token(request: Request):
    """
    Test endpoint to simulate an expired token.
    
    Parameters: request is a FastAPI Request object.
    Returns: A status on if expiring the token was successful.
    """
    try:
        creds_data = request.session.get("credentials")
        if not creds_data:
            return {"status": "No credentials found"}
        
        # Convert creds json to dictionary
        creds_dict = json.loads(creds_data) if isinstance(creds_data, str) else eval(creds_data)
        
        # Set an expired timestamp - make sure it expires the token
        if "token" in creds_dict and "expiry" in creds_dict:
            from datetime import datetime, timedelta
            expire_time = (datetime.now() - timedelta(hours = 2)).isoformat() + "Z"
            creds_dict["expiry"] = expire_time
                
            # Update session with modified credentials
            request.session["credentials"] = json.dumps(creds_dict)
            return {"status": "Token expired artificially", "new_expiry": expire_time}
        
        return {"status": "Could not expire token - missing fields"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}
        
@app.get("/test/remove_refresh_token")
async def test_remove_refresh_token(request: Request):
    """
    Remove the refresh token to test re-authentication
    
    Parameters: request is a FastAPI Request object.
    Returns: A status on if removing the refresh token was successful.
    """
    try:
        creds_data = request.session.get("credentials")
        if not creds_data:
            return {"status": "No credentials found"}
        
        # Convert creds json to dictionary
        creds_dict = json.loads(creds_data) if isinstance(creds_data, str) else eval(creds_data)
        
        # Remove refresh token and set token as expired
        if "refresh_token" in creds_dict:
            del creds_dict["refresh_token"]
            
        # Update session
        request.session["credentials"] = json.dumps(creds_dict)
        return {"status": "Refresh token removed"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}
        
@app.get("/dump_request")
async def dump_request(request: Request):
    """
    Dumps various attributes of the Request object for debugging.
    
    Parameters: request is a FastAPI Request object.
    Returns: A HTMLResponse of the request dumped.
    """
    output = f"Request URL: {request.url}\n"
    output += f"Request Method: {request.method}\n"
    output += f"Request Headers:\n"
    for header, value in request.headers.items():
        output += f"  {header}: {value}\n"
    output += f"Request Query Parameters: {request.query_params}\n"
    output += f"Request Client: {request.client}\n"
    output += f"Request Cookies: {request.cookies}\n" # Important for checking session
    output += f"Request State: {request.state}\n"

    return HTMLResponse(f"<pre>{output}</pre>")

def exception_auth_redirect(e):
    """
    Used for if an exception occurs during the running of a drive related endpoint.
    
    Parameters: e is an exception.
    Returns: an authorization URL as a result of redirecting to /auth/login.
    """
    if "missing fields refresh_token" in str(e):
        print(f"An exception occured, missing fields refresh_token: {str(e)}")
        return RedirectResponse("/auth/login", status_code=302)
    else:
        print(f"An exception occurred: {str(e)}")
        return RedirectResponse("/auth/login", status_code=302)

@app.get("/drive_data")
async def drive_data(request: Request, include_trashed: bool = False):
    """
    Lists all files in the user's Google Drive, requires user to be 
    authenticated to Google Drive through the app.
    
    Parameters: request is a FastAPI Request object;
                include_trashed is a boolean which signals whether to include trashed files, defaults to False.
    Returns: a list of file metadata from Google Drive.
    """
    try:
        creds = credential_handler.get_creds(request.session)
        return drive.return_all_drive_data(include_trashed, creds)
    except HTTPException as e:
        return exception_auth_redirect(e)

@app.get("/search")
async def search(request: Request, file_name: str):
    """
    Searches for files in the user's Google Drive by file name, requires user to be 
    authenticated to Google Drive through the app.
    
    Paramters: request is a FastAPI Request object;
               file_name is a string of the name of file to search for.
    Returns: a list of matching file metadata based on the file_name. 
    """
    try:
        creds = credential_handler.get_creds(request.session)
        return drive.search_file(file_name, creds)
    except HTTPException as e:
        return exception_auth_redirect(e)

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
    try:
        creds = credential_handler.get_creds(request.session)
        return drive.download_file(file_id, file_name, creds)
    except HTTPException as e:
        return exception_auth_redirect(e)

@app.post("/file_upload")
async def file_upload(request: Request, data: dict):
    """
    Uploads a file to the user's Google Drive, requires user to be 
    authenticated through the app to Google Drive.
    
    Paramters: data is a dictionary containing file_name, mimetype, and upload_filename.
    Returns: the boolean True if the file upload to the Google Drive was successful, returns False otherwise.
    """
    try:
        creds = credential_handler.get_creds(request.session)
        return drive.save_file(file_name=data.get("file_name"),mimetype=data.get("mimetype"),upload_filename=data.get("upload_filename"), creds=creds)
    except HTTPException as e:
        return exception_auth_redirect(e)

@app.get("/drive_structure")
async def drive_structure(request: Request, folder_id: str = "root", indent: int = 0, include_trashed: bool = False):
    """
    Retrieves the hierarchical structure of the files in the user's Google Drive, 
    requires user to be authenticated through the app to Google Drive. 
    Has extra cases because this function is currently used to test if the user is 
    currently authorized to bring up the login button on the frontend.
    
    Parameters: request is a FastAPI Request object;
                folder_id is a string of the starting folder ID, defaults to "root";
                indent is an integer of the indentation level for the file hierarchy, defaults to 0;
                include_trashed is a boolean which signals whether to include trashed items, defaults to False.
    Returns: a list of each of the files in the drive and each element of the list contains the relevant file metadata related to the drive file structure.
    """
    if "credentials" not in request.session: # case that frontend calls to bring up login button to authenticate
        creds = credential_handler.get_creds(request.session)
        return drive.return_drive_structure(folder_id, indent, include_trashed, creds)
    else: # case when there are credentials, which is almost all other cases
        try: # case which actually retrieves the data
            creds = credential_handler.get_creds(request.session)
            return drive.return_drive_structure(folder_id, indent, include_trashed, creds)
        except HTTPException as e: # case which handles when refresh token missing
            return exception_auth_redirect(e)

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
        