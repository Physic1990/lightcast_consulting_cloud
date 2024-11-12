# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
from . import credential_handler
from . import drive

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"message": "Hello, Team! Welcome to Lightcast Consulting Cloud API"}

team_members = [
    {
        "id": "1",
        "item": "Ian King"
    },
    {
        "id": "2",
        "item": "Shashwot Niraula"
    },
    {
        "id": "3",
        "item": "Andrew Plum"
    },
    {
        "id": "4",
        "item": "Bibek Sharma"
    },
    {
        "id": "5",
        "item": "Caleb Mouat"
    }
]

#Help with members example from https://testdriven.io/blog/fastapi-react/
#GET route for the members page
@app.get("/members", tags=["members"])
async def get_members() -> dict:
    return { "data": team_members }

#POST route for the members page
@app.post("/members", tags=["members"])
async def add_member(member: dict) -> dict:
    team_members.append(member)
    return {
        "data": { "Member added." }
    }

#DELETE route for the members page - BROKEN WITH CODE 422
@app.delete("/members/{id}", tags=["members"])
async def delete_member(memberID: int) -> dict:
    for member in team_members:
        if int(member["id"]) == memberID:
            team_members.remove(member)
            return {
                "data": f"Member with id {memberID} has been removed."
            }
    return {
        "data": f"Member with id {memberID} not found"
    }

# Google Drive Server Access Implementation Beginning

credential_handler.get_creds()

@app.get("/drive_data")
async def drive_data(include_trashed: bool = True):
    return drive.return_all_drive_data(include_trashed)

@app.get("/search")
async def search(file_name: str):
    return drive.search_file(file_name)

# NEED TO STILL HANDLE CASE WHERE MULTIPLE FILES ARE NAMED THE SAME
@app.get("/download")
async def download(file_id: Union[str, None] = None, file_name: Union[str, None] = None):
    return drive.download_file(file_id, file_name)

# Google Drive Server Access Implementation End