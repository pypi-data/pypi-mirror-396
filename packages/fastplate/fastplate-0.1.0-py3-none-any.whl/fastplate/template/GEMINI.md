# Project Overview

This is a web application built with a FastAPI backend and a Tailwind CSS frontend. It uses Jinja2 for templating, and DaisyUI as a component library for Tailwind CSS. The project is containerized using Docker.

# Building and Running

## Local Development

### Backend

1.  **Install Python dependencies:**
    ```bash
    uv sync
    ```
2.  **Start the FastAPI development server:**
    ```bash
    uv run fastapi dev --host 0.0.0.0 --port 8000
    ```
    Alternatively, you can use the Makefile command:
    ```bash
    make run-uv
    ```

### Frontend

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
3.  **Start the Tailwind CSS watch mode:**
    ```bash
    npm run dev
    ```

## Docker Development

```bash
# Build and start the application
docker compose up --build
```
Or use the Makefile:
```bash
make run-docker
```

# Development Conventions

*   **Backend:** The backend is a FastAPI application. The main application is in `app/main.py`. Views are defined in the `app/views` directory, and API routes should be placed in the `app/api` directory.
*   **Frontend:** The frontend uses Jinja2 for templating. The base template is `frontend/templates/base.html`. Pages are located in `frontend/templates/pages` and reusable components are in `frontend/templates/components`.
*   **Styling:** Styling is done with Tailwind CSS and DaisyUI. The main CSS file is `frontend/static/css/input.css`, which is compiled to `frontend/static/css/output.css`.
*   **Dependencies:** Python dependencies are managed with `uv` and defined in `pyproject.toml`. Frontend dependencies are managed with `npm` and defined in `frontend/package.json`.
*   **Makefile:** The `Makefile` provides convenient commands for running and managing the application.
*   **API Documentation:** FastAPI automatically generates API documentation, which can be found at `/docs` and `/redoc` when the application is running.
