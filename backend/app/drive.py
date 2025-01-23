import io
import json
import asyncio
import websockets
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
   
"""   
def socket(arg1: int, arg2: int, script_file_name: File):
    if arg1 and arg2: 
        # save both arguments to a file which can be parsed
        
        # send the data to the terminal and run the script and 
        # still in the terminal save the output of running the script as a file
        
        # send the script output file back to the backend of the app
        
        # save/store the new output file to the google drive root directory
        
        # display contents of the output file - use download function
    else:
        return
    
""" 

async def socket(arg1: int, arg2: int, script_file_name: str):
    if arg1 and arg2:
        # Save both arguments to a file
        args_file_name = "args.json"
        with open(args_file_name, "w") as args_file:
            json.dump({"arg1": arg1, "arg2": arg2}, args_file)

        async def send_to_terminal_and_process():
            async with websockets.connect("ws://localhost:8765") as websocket:
                # Send the arguments file and script name to the terminal
                await websocket.send(json.dumps({"args_file": args_file_name, "script_file": script_file_name}))

                # Wait for the terminal to send back the output file name
                output_file_name = await websocket.recv()
                print(f"Received output file: {output_file_name}")

                # Upload the output file to Google Drive
                creds = credential_handler.get_creds()
                service = build("drive", "v3", credentials=creds)
                with open(output_file_name, "rb") as file:
                    media = MediaIoBaseUpload(file, mimetype="text/plain")
                    file_metadata = {"name": output_file_name}
                    service.files().create(body=file_metadata, media_body=media, fields="id").execute()

                # Display the contents of the output file
                with open(output_file_name, "r") as file:
                    print(file.read())

        # Await the asynchronous function
        await send_to_terminal_and_process()
        return {"message": "Socket operation completed"}
    else:
        return {"error": "arg1 and arg2 must be provided"}

