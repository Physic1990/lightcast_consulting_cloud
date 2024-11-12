import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from . import credential_handler

def return_all_drive_data(include_trashed = True):
    creds = credential_handler.get_creds()
    service = build("drive", "v3", credentials = creds)

    # Use query of specific files in google drive if you only want to see certain files
    if include_trashed: # no query needed, this will include trashed files by default
        query = None
    else: # exclude trashed files
        query = "trashed = false"

    if query: # results exclude trash - this is not the default
        results = service.files().list(q = query).execute()
    else: # results include trash - this is the default
        results = service.files().list().execute()
    items = results.get("files", [])

    if not items:
        print("No files found")
        return []
    print("Files:")
    for i in items:
        print(u"{0} ({1})".format(i["name"], i["id"]))

    return items

def search_file(file_name):
    creds = credential_handler.get_creds()
    service = build("drive", "v3", credentials = creds)
    query = f"name = '{file_name}'"
    results = service.files().list(q = query).execute() # with query of specific files in google drive if you only want to see certain files
    items = results.get("files", [])

    if not items:
        print("No files found")
        return []
    print("Files:")
    for i in items:
        print(u"{0} ({1})".format(i["name"], i["id"]))

    return items

def download_file(file_id, file_name = None):
    if file_id:
        creds = credential_handler.get_creds()
        service = build("drive", "v3", credentials = creds)
        request = service.files().get_media(fileId = file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}")
        return file.getvalue()
    elif file_name:
        files = search_file(file_name)
        if len(files) == 0:
            print(f"Could not find file {file_name}")
            return
        elif len(files) > 1:
            print(f"File name {file_name} is not unique")
            return 
        file_id = files[0]["id"]
        return download_file(file_id)
    else:
        print("No file_id or file_name provided")