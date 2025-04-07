# Import modules and packages
import io
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
from . import credential_handler
import pandas as pd
from fastapi import HTTPException

# Define storage directories
DOWNLOAD_FOLDER = "downloading"  # Files downloaded from Google Drive
PROCESSED_FOLDER = "got_from_local_helper_processed"  # Processed files received from Local Helper

# Ensure directories exist
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Application to Google Drive related functions

def return_all_drive_data(include_trashed=False, creds = None):
    """
    Fetches all files from Google Drive with optional trash inclusion.
    
    Parameters: include_trashed is a boolean flag to include/exclude trashed files, defaults to false;
                creds is the Google credentials retrieved from get_creds() in credential_handler.py, defaults to None.
    Raises: ValueError if credentials are not provided.
    Returns: list of file metadata from Google Drive.
    """
    if creds is None:
        raise ValueError("Credentials are None; need to authenticate before calling this function.")

    # Build Google Drive API service
    service = build("drive", "v3", credentials=creds) 

    # Create query to retrieve all relevant files in drive, filter trashed files if specified
    query = None if include_trashed else "trashed = false"
    results = service.files().list(q=query).execute()

    # Format and return result from query
    items = results.get("files", [])

    if not items:
        print("No files found in Google Drive.")
        return []

    for i in items:
        print(f"File found: {i['name']} ({i['id']})")

    return items

def search_file(file_name, creds = None):
    """
    Searches for a file in Google Drive by file name. 
    
    Parameters: file_name is a string of the exact name of the file to search for in Google Drive;
                creds is the Google credentials retrieved from get_creds() in credential_handler.py, defaults to None.
    Raises: ValueError if credentials are not provided.
    Returns: a list of dictionaries of file metadata related to the file_name.
    """
    if creds is None:
        raise ValueError("Credentials are None; need to authenticate before calling this function.")

    # Build Google Drive API service
    service = build("drive", "v3", credentials=creds)
    
    # Create query to retrieve all relevant files by file name in drive
    query = f"name = '{file_name}'"
    results = service.files().list(q=query).execute()
    
    # Format and return result from query
    items = results.get("files", [])

    if not items:
        print(f"No files found matching: {file_name}")
        return []

    for i in items:
        print(f"Found file: {i['name']} ({i['id']})")

    return items

def download_file(file_id, file_name=None, creds = None):
    """
    Downloads a file from Google Drive using its file ID.
    
    Parameters: file_id is a string of the Google Drive file ID, required;
                file_name is a string of the name to save the downloaded file as, defaults to None;
                creds is the Google credentials retrieved from get_creds() in credential_handler.py, defaults to None.
    Raises: ValueError if credentials are not provided.
    Returns: a string of the local file path of the downloaded file.
    """
    if creds is None:
        raise ValueError("Credentials are None; need to authenticate before calling this function.")

    # Build Google Drive API service
    service = build("drive", "v3", credentials=creds)

    # Request file media content
    request = service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)

    # Download file in chunks with progress tracking
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download progress: {int(status.progress() * 100)}%")

    # If no file_name provided, get it from the file metadata
    if file_name is None:
        file_info = service.files().get(fileId=file_id).execute()
        file_name = file_info.get("name", "downloaded_file")

    # Save downloaded content to file
    local_path = os.path.join(DOWNLOAD_FOLDER, file_name)
    with open(local_path, "wb") as f:
        f.write(file_data.getvalue())

    # Display and return resulting path of downloaded file
    print(f"File downloaded successfully: {local_path}")
    return local_path

def save_file(file_name, mimetype, upload_filename, resumable=True, chunksize=262144, creds = None):
    """
    Uploads a file from the application to Google Drive.

    Parameters: file_name which is a string of the local path of the file to upload;
                mimetype which is a string of the MIME type of the file;
                upload_filename which is a string of the name to use for the uploaded file;
                resumable which is a boolean flag of whether to use resumable upload defaults to True;
                chunksize which is an integer of the chunk size for resumable uploads, defaults to 262144;
                creds is the Google credentials retrieved from get_creds() in credential_handler.py, defaults to None.
    Raises: ValueError if credentials are not provided;
            HTTPException if upload fails.
    Returns: True if file upload to Google Drive was successful, returns False otherwise.
    """
    try:
        if creds is None:
            raise ValueError("Credentials are None; need to authenticate before calling this function.")

        # Build Google Drive API service
        service = build("drive", "v3", credentials = creds)

        # Remove file name prefix and prepare file metadata and media
        loc_file_name = file_name[8:]
        upload_filename = os.path.basename(file_name)
        file_metadata = {
            'name': upload_filename,
            'mimeType': mimetype
        }
        
        # Configure the media upload with resumable option for large files
        media = MediaFileUpload(loc_file_name, mimetype=mimetype, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        # If file created, return True, else False
        if(file):
            return True
        else:
            return False
    except:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")

def return_drive_structure(folder_id = "root", indent = 0, include_trashed = False, creds = None):
    """
    Recursively retrieves Google Drive folder structure beginning from specified folder.
    
    Parameters: folder_id is a string which is an ID of the starting folder, defaults to "root";
                indent is an integer which indicates the indentation level for file hierarchy visualization, defaults to 0;
                include_trashed is a boolean which is a flag of whether to include trashed files in the returned structure; defaults to False;
                creds is the Google credentials retrieved from get_creds() in credential_handler.py, defaults to None.
    Raises: ValueError if credentials are not provided.
    Returns: a list of each of the files in the drive and each element of the list contains the relevant file metadata related to the drive file structure.
    """
    if creds is None:
        raise ValueError("Credentials are None; need to authenticate before calling this function.")
    
    # Build Google Drive API service
    service = build("drive", "v3", credentials = creds)
    
    # Build query for relevant files
    query = f"'{folder_id}' in parents"
    if not include_trashed: # by default trash is included in the query at this point
        query += " and trashed=false" # so we add this to the query to not include the trash files
    results = service.files().list(
        q = query,
        spaces = 'drive',
        fields = "files(id, name, mimeType, trashed)",
    ).execute()
    
    # Format and return result from query 
    items = results.get('files', [])
    structure = []
    for item in items:
        item_info = {
            "name": item['name'],
            "id": item['id'],
            "type": "folder" if item['mimeType'] == 'application/vnd.google-apps.folder' else "file",
            "indent": indent,
            "trashed": item["trashed"]
        }
        structure.append(item_info)
        
        # Recursively process subfolders
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            structure.extend(return_drive_structure(folder_id = item['id'], indent = indent + 1, include_trashed = include_trashed, creds = creds))
    
    return structure
    
# Application to local file related functions    
    
def process_file(file_path):
    """
    Processes the given file based on its format.
    If it's an Excel file (.xlsx, .xls), it adds a new column and saves it.
    :param file_path: Path to the downloaded file.
    :return: Processed file path.
    """
    try:
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        processed_file_path = os.path.join(PROCESSED_FOLDER, f"processed_{os.path.basename(file_path)}")

        if file_extension in [".xlsx", ".xls"]:
            print(f"⚙️ Processing Excel file: {file_path}")

            df = pd.read_excel(file_path)

            # Add a new column (Example: Adding a column "Sum" that sums first two columns)
            if len(df.columns) >= 2:
                df["Sum"] = df.iloc[:, 0] + df.iloc[:, 1]
            else:
                df["Sum"] = 0  # If there aren't enough columns, default value

            df.to_excel(processed_file_path, index=False)
            print(f"Processed Excel file saved: {processed_file_path}")

        else:
            print(f"Unsupported file type: {file_extension}")
            return None

        return processed_file_path

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None