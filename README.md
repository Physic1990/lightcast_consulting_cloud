
# Lightcast Consulting Cloud

## Project Overview
This is the **Lightcast Consulting Cloud** project. The project is being developed using **FastAPI** for building a REST API and will manage Excel-based data modeling projects, automate processes, and create customer deliverables.

---

## Project Setup

### Clone the Repository
First, clone the repository to your local machine:
```bash
git clone <repo-url>
cd lightcast_consulting_cloud
```

### Set Up a Virtual Environment
Create a virtual environment to isolate your project dependencies:

```bash
python3 -m venv lightcast_env
```

Activate the virtual environment:
- **For macOS/Linux**:
    ```bash
    source lightcast_env/bin/activate
    ```
- **For Windows**:
    ```bash
    .\lightcast_env\Scripts\activate
    ```

### Install Project Dependencies
Once the virtual environment is activated, install the necessary packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Run the Application
With everything set up, you can now run the FastAPI app using **Uvicorn**:

```bash
uvicorn app.main:app --reload
```

The `--reload` flag ensures that the app reloads when code changes are detected.

### Access the API
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)  


## Contributors
- 
