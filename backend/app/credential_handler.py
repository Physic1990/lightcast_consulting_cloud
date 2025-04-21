# Import modules and packages
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from fastapi import HTTPException
import json

# OAuth Scopes for Google Drive
SCOPES = ["https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/docs",
          "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.metadata.readonly"]

# New session based implementation
def get_creds(session = None):
    """
    Retrieves Google OAuth2 credentials from session storage or token file if no session.
    
    Parameters: session from the request, defaults to None.
    Raises: HTTPException if user is not authenticated and no valid credentials are found.
    Returns: Google credentials object.
    """     
    if session is None:
        # If no session is provided, fall back to the previous token.json method
        script_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(script_dir, "token.json")

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            return creds
    else:
        # Use the session-based method
        creds_data = session.get("credentials")
        if not creds_data:
            raise HTTPException(status_code = 401, detail = "Not authenticated")
        
        creds_dict = json.loads(creds_data) if isinstance(creds_data, str) else eval(creds_data)
        try:
            if 'refresh_token' not in creds_dict:
                raise HTTPException(status_code = 401, detail = "refresh_token missing from creds_dict, re-authentication required")
            
            creds = Credentials.from_authorized_user_info(eval(creds_data), SCOPES) # send json as a dictionary and scopes to get creds
            
            if creds and creds.expired and creds.refresh_token: # if credentials expired, refresh
                creds.refresh(Request())
                session["credentials"] = creds.to_json() # update passed in session with new credentials
                
            return creds
        
        except Exception as e:
            raise HTTPException(status_code = 401, detail = f"Try reauthenticating. Error: {str(e)}")