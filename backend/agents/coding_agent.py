from .base import BaseAgent
from ..models import ProjectState, Artifacts
from ..llm import generate_json, generate_completion, GROQ_API_KEY
import asyncio

class CodingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Coding Agent")

    async def process(self, project_state: ProjectState) -> ProjectState:
        if not project_state.srs:
            self.update_status("failed", "No SRS found.")
            return project_state
            
        self.update_status("working", "Generating Project Code...")
        
        brief_lower = project_state.brief.brief_content.lower()
        
        # Detect tech stack
        if "node" in brief_lower or "express" in brief_lower:
            tech = "Node.js/Express"
        elif "django" in brief_lower:
            tech = "Python/Django"
        elif "flask" in brief_lower:
            tech = "Python/Flask"
        else:
            tech = "Python/FastAPI"
        
        req_descriptions = "\n".join([f"- {r.description} (Priority: {r.priority})" for r in project_state.srs.requirements])
        
        if GROQ_API_KEY:
            try:
                # Step 1: Generate file structure
                self.update_status("working", f"Designing {tech} Architecture...")
                struct_prompt = f"""You are a Senior Software Architect. Design the file structure for a {tech} project.

Project: {project_state.brief.brief_content}
Requirements:
{req_descriptions}

Return JSON with key "files" containing a list of file paths (max 12 important files).
Example: {{"files": ["backend/main.py", "backend/models.py", "frontend/src/App.tsx", "docker-compose.yml"]}}"""

                struct_res = await generate_json(struct_prompt, "Generate the file structure.")
                files = struct_res.get("files", [])
                
                # Step 2: Generate actual code for top 3 files
                self.update_status("working", "Writing Code Files...")
                code_snippets = {}
                
                # Generate code for multiple key files
                important_files = files[:4] if len(files) >= 4 else files
                
                for filename in important_files:
                    try:
                        self.update_status("working", f"Writing {filename}...")
                        code_prompt = f"""Write production-quality code for the file: {filename}

Project: {project_state.brief.brief_content}
Tech Stack: {tech}
Requirements:
{req_descriptions}

Write complete, working code with proper imports, error handling, and comments.
Return JSON: {{"code": "...the full file content..."}}"""

                        code_res = await generate_json(code_prompt, f"Write code for {filename}")
                        code_snippets[filename] = code_res.get("code", f"# TODO: Implement {filename}")
                    except Exception as e:
                        code_snippets[filename] = f"# Error generating code: {e}"
                
                project_state.artifacts = Artifacts(
                    file_structure=files,
                    code_snippets=code_snippets
                )
                
                self.update_status("completed", f"Generated {len(code_snippets)} code files.")
                return project_state
                
            except Exception as e:
                print(f"Coding Agent LLM Error: {e}")
        
        # Fallback: Generate basic templates
        await asyncio.sleep(1)
        project_state.artifacts = Artifacts(
            file_structure=[
                "backend/main.py", "backend/models.py", "backend/routes.py",
                "frontend/src/App.tsx", "frontend/src/index.css",
                "docker-compose.yml", "README.md", ".env.example"
            ],
            code_snippets={
                "backend/main.py": f'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{project_state.brief.name}")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {{"message": "{project_state.brief.name} API is running"}}

# TODO: Add routes based on requirements
''',
                "README.md": f'''# {project_state.brief.name}

{project_state.brief.description}

## Quick Start
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
'''
            }
        )
        self.update_status("completed", "Generated template code (Heuristic).")
        return project_state
