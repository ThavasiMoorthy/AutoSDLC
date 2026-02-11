from .base import BaseAgent
from ..models import ProjectState
import asyncio
import random

class RoleAssignmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Role Assignment Agent")

    async def process(self, project_state: ProjectState) -> ProjectState:
        if not project_state.plan:
             self.update_status("failed", "No Project Plan found.")
             return project_state

        self.update_status("working", "Assigning roles to tasks...")
        await asyncio.sleep(1)
        
        for task in project_state.plan.tasks:
            name_lower = task.name.lower()
            desc_lower = task.description.lower()
            
            # Smart Role Assignment
            if any(w in name_lower for w in ["setup", "deploy", "ci/cd", "pipeline", "server", "database", "docker"]):
                task.assigned_role = "DevOps Engineer"
            elif any(w in name_lower for w in ["ui", "frontend", "design", "css", "react", "component"]):
                task.assigned_role = "Frontend Developer"
            elif any(w in name_lower for w in ["api", "backend", "logic", "model", "data", "auth"]):
                task.assigned_role = "Backend Developer"
            elif any(w in name_lower for w in ["test", "verify", "quality", "check"]):
                 task.assigned_role = "QA Engineer"
            else:
                # Default fallback based on description or random
                if "interface" in desc_lower:
                    task.assigned_role = "Frontend Developer"
                else:
                    task.assigned_role = "Full Stack Developer"
                
        self.update_status("completed", "Roles assigned to all tasks.")
        return project_state
