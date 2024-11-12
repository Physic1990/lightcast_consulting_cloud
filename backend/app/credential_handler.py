#import os
import os.path
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/docs",
          "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.metadata.readonly"]

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

def get_creds():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, "token.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    return request_creds()