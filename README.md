
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

## Docker Setup

This project uses Docker to containerize both the frontend and backend services. Follow the steps below to build, run, and manage the application using Docker.

### Prerequisites

- Ensure you have [Docker](https://www.docker.com/products/docker-desktop) and [Docker Compose](https://docs.docker.com/compose/) installed on your machine.

### Project Structure

The project has the following directory structure:

```plaintext
project-root/
├── frontend/
│   ├── Dockerfile            # Dockerfile for frontend
│   ├── package.json          # Frontend dependencies and scripts
│   └── other frontend files...
├── backend/
│   ├── Dockerfile            # Dockerfile for backend
│   ├── requirements.txt      # Backend dependencies
│   └── other backend files...
└── docker-compose.yml        # Docker Compose configuration
```

## Verifying Docker Installation

Before proceeding, ensure that Docker and Docker Compose are installed on your system.

###  Check Docker Installation
To verify Docker is installed, open your terminal and run:

```bash
docker --version
```
## Docker Setup Instructions

The `docker-compose.yml` file is configured to build and run both frontend and backend services. Make sure this file is present in the root of the project.

### Build the Docker Images

To build the Docker images for both services, use the following command:

```bash
docker-compose build
```

This command builds the images based on the Dockerfiles in the `frontend` and `backend` directories.

### Run the Containers

Start the containers by running:

```bash
docker-compose up
```

This command will start both the frontend and backend containers and display logs in the terminal. By default, the frontend will be available on port `3000` and the backend on port `8000`.

### Access the Application

- **Frontend**: Visit `http://localhost:3000` in your browser.
- **Backend**: Access `http://localhost:8000` (or your API endpoints).

### Stop the Containers

To stop the containers, press `CTRL+C` in the terminal where `docker-compose up` is running. Alternatively, you can stop the containers with:

```bash
docker-compose down
```

### Rebuilding Containers

If you make changes to the `Dockerfile` or dependencies, you may need to rebuild the images. Use the following command to rebuild without cache:

```bash
docker-compose build --no-cache
```

## Troubleshooting

- **Error: `vite: not found`**: Ensure that `vite` is listed in the `devDependencies` section of `package.json` in the frontend directory.
- **Command not found in Docker**: If a command is not recognized in the container, try specifying its full path (e.g., `node_modules/.bin/vite`).
- **Port conflicts**: If ports `3000` or `8000` are already in use, modify the ports in `docker-compose.yml`.


## Contributors
- Andrew Plum
- Bibek Sharma
- Caleb Mouat
- Ian King
- Shashwot Niraula
