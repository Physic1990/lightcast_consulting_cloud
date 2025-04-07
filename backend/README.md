# Backend Files

## Features

This backend uses FastAPI. It authenticates and does various file interactions with 
Google Cloud. It contains functions the frontend calls. It also establishes a 
connection and interacts with the local helper.

## File Structure

app/application.py: FastAPI app with web handlers, the OAuth authentication system, and part of the credential handling. <br>
app/drive.py: Google Drive API interaction functions as well as local helper file processing functions. <br>
app/credential_handler.py: Authentication credential management. <br>
app/creds.json: OAuth 2.0 client credentials. <br>

## Main Endpoints

/auth/login: Start Google authentication <br>
/auth/callback: Authentication redirection URI after /auth/login <br>
/drive_data: List Google Drive files <br>
/drive_structure: Show Google Drive folder hierarchy <br>
/search: Find Google Drive files by name <br>
/download: Download files from Google Drive <br>
/file_download: Downloads files from application to local device <br>
/file_upload: Upload processed files to Google Drive <br>
/scripts_folder: Retrieves local helper scripts folder <br>
/run-local-model: Process files with local helper <br>

## Run After Setup

After environment is setup and dependencies installed, run in backend directory by:

```bash
uvicorn app.application:app --reload
```

The backend will be available at http://localhost:8000.

