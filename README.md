
# Lightcast Consulting Cloud

## Project Overview
The **Lightcast Consulting Cloud** project is a web-based platform developed using **FastAPI** (for the backend) and **React (TypeScript)** (for the frontend). It is designed to:
- Manage **Excel-based data modeling projects**.
- Automate **customer deliverables**.
- Support **file handling and processing** via a **local helper desktop application**.


---

## Project Setup

### Clone the Repository
First, clone the repository to your local machine:
```bash
git clone <repo-url>
cd lightcast_consulting_cloud
```

### How to run the program

Start the Local Helper inside local_helper folder: python3 local_helper.py

Run the backend inside backend folder with virtual env: uvicorn app.main:app --reload

Start the frontend inside frontend folder: yarn dev (or npm run dev)

### Front end setup

```bash
cd frontend
yarn install  # OR npm install
yarn run dev --host
```

The frontend will be available at http://localhost:3000.


### Back end setup
```bash
cd backend
python3 -m venv lightcast_env  # Create a virtual environment
source lightcast_env/bin/activate  # (Mac/Linux)
lightcast_env\Scripts\activate  # (Windows)
```

Install dependencies

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
The backend will be available at http://localhost:8000.

### Local helper setup
```bash
cd local_helper
python3 local_helper.py
```
This will launch a GUI application and also start a Flask server at http://localhost:9000.

## Contributors
- Andrew Plum
- Bibek Sharma
- Caleb Mouat
- Ian King
- Shashwot Niraula
