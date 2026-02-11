# How to Run AutoSDLC

Since the automatic startup is having issues, you can run the backend and frontend manually in two separate terminal windows.

## Prerequisites

- Python 3.10+
- Node.js 18+

## Step 1: Start the Backend

1. Open a new terminal.
2. Navigate to the project directory:
   ```powershell
   cd d:\SDLC_AUTOMATION
   ```
3. Install Python dependencies (if not already installed):
   ```powershell
   pip install -r backend/requirements.txt
   ```
4. Run the FastAPI server:
   ```powershell
   python -m uvicorn backend.main:app --reload --port 8000
   ```
   *You should see output indicating the server is running at http://localhost:8000*

## Step 2: Start the Frontend

1. Open a **second** terminal.
2. Navigate to the client directory:
   ```powershell
   cd d:\SDLC_AUTOMATION\client
   ```
3. Install Node dependencies (if not already installed):
   ```powershell
   npm install
   ```
4. Run the development server:
   ```powershell
   npm run dev
   ```
   *You should see output indicating the server is running, usually at http://localhost:5173*

## Step 3: Open in Browser

- Open your web browser and go to the URL shown in the frontend terminal (e.g., `http://localhost:5173`).
