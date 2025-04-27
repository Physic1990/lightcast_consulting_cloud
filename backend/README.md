# Backend Files

## Features

This backend uses FastAPI. It authenticates and does various file interactions with 
Google Cloud. It contains functions the frontend calls. It also establishes a 
connection and interacts with the local helper.

## File Structure

app/application.py: FastAPI app with web handlers, the OAuth authentication system, and part of the credential handling. <br>
app/drive.py: Google Drive API interaction functions as well as local helper file processing functions. <br>
app/credential_handler.py: Handles the authentication credentials stored in the session. <br>
app/creds.json: File which stores the OAuth 2.0 client credentials. <br>

## Main Endpoints

/auth/login: Start Google authentication <br>
/auth/callback: Authentication redirection URI after /auth/login <br>
/is_authenticated: Checks of user is authenticated <br>
/drive_data: List Google Drive files <br>
/search: Find Google Drive files by name <br>
/download: Download files from Google Drive <br>
/file_upload: Upload processed files to Google Drive <br>
/drive_structure: Show Google Drive folder hierarchy <br>
/run-local-model: Process files with local helper <br>
/scripts_folder: Retrieves local helper scripts folder <br>
/file_download: Downloads files from application to local device <br>

## Test Endpoints

/test/delete_creds: Deletes current set of credentials stored in session <br>
/test/expire_token: Expires access token stored in the credentials in the session <br>
/test/remove_refresh_token: Removes refresh token from the credentials in the session <br>
/dump_request: Outputs attributes of the request object for debugging purposes <br>

## Backend System Mechanism

Main Sequence: <br>
1) The frontend makes a request to the /drive_structure endpoint. An error is returned to the frontend if the credentials in the session are invalid, otherwise the data from return_drive_structure() is returned. <br>
2) If the user current credentials stored in the session are invalid, the user must authenticate. Clicking the login button on the frontend, makes a request to the /auth/login endpoint. Here, Google OAuth's authentication flow is started and an authorization_url is returned. <br>
3) The user goes through Google's authentication process. <br>
4) After authenticating, the user is redirected to the endpoint /auth/callback where an authentication status is returned. The credentials are also stored in the session here. <br>
5) After being redirected, if the authentication was successful, the user is now authorized to call any of the drive functions. Refreshing the frontend webpage after successful authentication, will make another request to the /drive_structure endpoint where the relevant data will then be returned and displayed to the user. <br> 

Note: <br>
- The credentials are retrieved from the session using credential_handler.get_creds() each time a request to drive related endpoint is made. After the credentials are retrieved, they are then passed to the related drive function in the drive.py file. <br>
- If an error arises where the refresh token is missing after previous successful authentication, the user will need to re-authenticate by refreshing the frontend webpage twice to bring up the login button, and then beginning the authentication process as before by clicking the button. <br>

## Run After Setup

After environment is setup and dependencies installed, run in backend directory by:

```bash
uvicorn app.application:app --reload
```

The backend will be available at http://localhost:8000.

