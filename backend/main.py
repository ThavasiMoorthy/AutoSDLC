from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import asyncio
import uuid
import os
from typing import Dict, List, Optional

from .models import ProjectBrief, ProjectState
from .agents.requirement_agent import RequirementAgent
from .agents.planning_agent import PlanningAgent
from .agents.role_agent import RoleAssignmentAgent
from .agents.coding_agent import CodingAgent
from .agents.prototype_agent import PrototypeAgent

load_dotenv()

app = FastAPI(title="AutoSDLC API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (Replace with DB later)
projects_db: Dict[str, ProjectState] = {}

# Initialize Agents
req_agent = RequirementAgent()
plan_agent = PlanningAgent()
role_agent = RoleAssignmentAgent()
code_agent = CodingAgent()
prototype_agent = PrototypeAgent()

@app.get("/")
def read_root():
    # In production, serve the built React frontend
    index_file = Path(__file__).parent.parent / "client" / "dist" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "AutoSDLC API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

async def run_orchestration(project_id: str):
    """
    Orchestrate the agents sequentially.
    """
    state = projects_db[project_id]
    
    # Step 1: Requirements
    state = await req_agent.process(state)
    projects_db[project_id] = state 
    
    # Step 2: Planning
    state = await plan_agent.process(state)
    projects_db[project_id] = state
    
    # Step 3: Role Assignment
    state = await role_agent.process(state)
    projects_db[project_id] = state

    # Step 4: Coding Agent
    state = await code_agent.process(state)
    projects_db[project_id] = state

@app.post("/projects", response_model=ProjectState)
async def create_project(brief: ProjectBrief, background_tasks: BackgroundTasks):
    """
    Submit a new project brief and start the automation.
    """
    new_project = ProjectState(brief=brief)
    projects_db[new_project.id] = new_project
    
    # Trigger agents in background
    background_tasks.add_task(run_orchestration, new_project.id)
    
    return new_project

@app.get("/projects", response_model=List[ProjectState])
def list_projects():
    return list(projects_db.values())

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[project_id]

@app.post("/prototype/{project_id}")
async def generate_prototype(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    result = await prototype_agent.process(project)
    return result


class ChatMessage(BaseModel):
    message: str
    project_id: Optional[str] = None

@app.post("/chat")
async def chat(msg: ChatMessage):
    from .llm import generate_completion, GROQ_API_KEY
    
    if not GROQ_API_KEY:
        return {"reply": "AI is not configured. Please set your Groq API key."}
    
    # Build context from current project if available
    context = ""
    if msg.project_id and msg.project_id in projects_db:
        proj = projects_db[msg.project_id]
        context += f"\nProject Brief: {proj.brief.brief_content}"
        if proj.srs:
            context += f"\nRequirements: {[r.description for r in proj.srs.requirements]}"
        if proj.plan:
            context += f"\nPlan Tasks: {[t.name for t in proj.plan.tasks]}"
            context += f"\nEstimated Cost: ${proj.plan.estimated_cost}"
        if proj.artifacts:
            context += f"\nGenerated Files: {proj.artifacts.file_structure}"
    
    system_prompt = f"""You are AutoSDLC Assistant, an AI expert in software development.
You help users understand their project plans, suggest improvements, answer technical questions,
and provide guidance on implementation.

Current Project Context:{context if context else ' No project loaded yet.'}

Be concise, helpful, and technical. Use markdown formatting."""

    try:
        reply = await generate_completion(system_prompt, msg.message)
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"Sorry, I encountered an error: {str(e)}"}

# === STATIC FILE SERVING (Production) ===
# Mount built React frontend if it exists (after npm run build)
_client_dist = Path(__file__).parent.parent / "client" / "dist"
if _client_dist.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(_client_dist / "assets")), name="static-assets")
    
    # SPA catch-all: serve index.html for any non-API route
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # If the path is an API route, FastAPI handles it above
        # Otherwise serve the SPA
        file_path = _client_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_client_dist / "index.html"))
