import io
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
from os import stat
from . import credential_handler
import pandas as pd
from fastapi import HTTPException


# Define storage directories
DOWNLOAD_FOLDER = "downloading"  # Files downloaded from Google Drive
PROCESSED_FOLDER = "got_from_local_helper_processed"  # Processed files received from Local Helper

# Ensure directories exist
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def return_all_drive_data(include_trashed=False):
    """
    Fetches all files from Google Drive.
    :param include_trashed: Boolean flag to include/exclude trashed files.
    :return: List of file metadata from Google Drive.
    """
    creds = credential_handler.get_creds()
    service = build("drive", "v3", credentials=creds)

    query = None if include_trashed else "trashed = false"
    results = service.files().list(q=query).execute()

    items = results.get("files", [])

    if not items:
        print("No files found in Google Drive.")
        return []

    for i in items:
        print(f"File found: {i['name']} ({i['id']})")

    return items

def search_file(file_name):
    creds = credential_handler.get_creds()
    service = build("drive", "v3", credentials=creds)
    query = f"name = '{file_name}'"
    results = service.files().list(q=query).execute()
    items = results.get("files", [])

    if not items:
        print(f"No files found matching: {file_name}")
        return []

    for i in items:
        print(f"Found file: {i['name']} ({i['id']})")

    return items

def download_file(file_id, file_name=None):
    """
    Downloads a file from Google Drive using its file ID.
    :param file_id: The Google Drive file ID.
    :param file_name: (Optional) Custom filename to save the file.
    :return: Local file path of the downloaded file.
    """
    creds = credential_handler.get_creds()
    service = build("drive", "v3", credentials=creds)

    request = service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download progress: {int(status.progress() * 100)}%")

    if file_name is None:
        file_info = service.files().get(fileId=file_id).execute()
        file_name = file_info.get("name", "downloaded_file")

    local_path = os.path.join(DOWNLOAD_FOLDER, file_name)
    with open(local_path, "wb") as f:
        f.write(file_data.getvalue())

    print(f"File downloaded successfully: {local_path}")
    return local_path

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

def return_drive_structure(folder_id = 'root', indent = 0):
    creds = credential_handler.get_creds()
    service = build("drive", "v3", credentials = creds)

    query = f"'{folder_id}' in parents"
    results = service.files().list(
        q = query,
        spaces = 'drive',
        fields = "files(id, name, mimeType)",
    ).execute()

    items = results.get('files', [])
    structure = []
    for item in items:
        item_info = {
            "name": item['name'],
            "id": item['id'],
            "type": "folder" if item['mimeType'] == 'application/vnd.google-apps.folder' else "file",
            "indent": indent
        }
        structure.append(item_info)
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            structure.extend(return_drive_structure(folder_id = item['id'], indent = indent + 1))
    return structure

#Save a file from the application to Drive
def save_file(file_name, mimetype, upload_filename, resumable=True, chunksize=262144):
    try:
        creds = credential_handler.get_creds()
        service = build("drive", "v3", credentials = creds)

        loc_file_name = file_name[8:]

        upload_filename = os.path.basename(file_name)

        file_metadata = {
        'name': upload_filename,
        'mimeType': mimetype
        }
        media = MediaFileUpload(loc_file_name, mimetype=mimetype, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        if(file):
            return True
    except:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")
