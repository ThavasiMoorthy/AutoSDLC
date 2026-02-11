# --- Build Stage: Frontend ---
FROM node:18-slim AS frontend-build
WORKDIR /app/client
COPY client/package*.json ./
RUN npm install
COPY client/ ./
RUN npm run build

# --- Final Stage: Backend + Frontend Assets ---
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies if any
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend assets from the frontend-build stage
COPY --from=frontend-build /app/client/dist ./client/dist

# Expose the port (Railway uses PORT environment variable)
EXPOSE 8000

# Start command (shell form for variable expansion)
CMD python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
