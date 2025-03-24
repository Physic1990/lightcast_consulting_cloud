#import os
import os.path
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from fastapi import HTTPException

SCOPES = ["https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/docs",
          "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.metadata.readonly"]

# Previous token.json implementation
"""
def request_creds():
    creds = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(script_dir, "creds.json")
    token_path = os.path.join(script_dir, "token.json")

    if os.path.exists(creds_path):
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port = 0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
        return Credentials.from_authorized_user_file(token_path, SCOPES)   
    else:
        #print("Current working directory:", os.getcwd())
        print("Credentials are not present")
        sys.exit(1)
"""

"""
def get_creds():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, "token.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    return request_creds()
"""
#

# New session based implementation
def get_creds(session = None):
    """Get credentials from session storage"""
    
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
        return request_creds()
    else:
        # Use the session-based method
        creds_data = session.get("credentials")
        if not creds_data:
            raise HTTPException(status_code = 401, detail = "Not authenticated")
        
        creds = Credentials.from_authorized_user_info(eval(creds_data), SCOPES)
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Update session with new credentials
            session["credentials"] = creds.to_json()
        
        return creds
    """
    
    # Use the session-based method
    if session is None:
        raise ValueError("No session passed to get_creds ie session is None; pass a session.")
    
    creds_data = session.get("credentials")
    if not creds_data:
        raise HTTPException(status_code = 401, detail = "Not authenticated")
        
    creds = Credentials.from_authorized_user_info(eval(creds_data), SCOPES)
        
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Update session with new credentials
        session["credentials"] = creds.to_json()
        
    return creds
#