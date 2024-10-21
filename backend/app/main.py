# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
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

@app.get("/members", tags=["members"])
async def get_members() -> dict:
    return { "data": team_members }