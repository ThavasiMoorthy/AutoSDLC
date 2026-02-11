from .base import BaseAgent
from ..models import ProjectState, ProjectPlan, WBSTask
import uuid
import asyncio

class PlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Planning Agent")

    async def process(self, project_state: ProjectState) -> ProjectState:
        if not project_state.srs:
             self.update_status("failed", "No SRS found. Cannot plan.")
             return project_state

        self.update_status("working", "Estimating Effort & Costs...")
        
        from ..llm import generate_json, GROQ_API_KEY
        tasks = []
        complexity_score = 3  # Default: simple project
        

        if GROQ_API_KEY:
            try:
                self.update_status("working", "Consulting AI for Estimation...")
                req_text = "\n".join([f"- {r.description} ({r.priority})" for r in project_state.srs.requirements])
                system_prompt = """You are a lean startup CTO giving REALISTIC cost estimates.
                
RULES:
- Keep total project days UNDER 25 for most projects
- Simple features = 0.5-1 day, Medium = 1-2 days, Complex = 2-4 days
- Setup/config = 0.5-1 day MAX
- Testing = 1-2 days total, NOT per feature
- Do NOT pad estimates. Be aggressive and lean.
- Max 8 tasks total

Return JSON:
{
    "complexity_score": 1-10,
    "tasks": [
        {"name": string, "description": string, "role_category": "backend"|"frontend"|"setup"|"test"|"devops", "days": number, "dependency": string|null}
    ]
}"""
                response = await generate_json(system_prompt, f"Requirements:\n{req_text}")
                
                complexity_score = response.get("complexity_score", 3)
                
                for i, t in enumerate(response.get("tasks", [])):
                    days = min(t.get('days', 1), 5)  # Cap single task at 5 days
                    tasks.append(WBSTask(
                        id=f"TASK-{i+1:03d}",
                        name=t['name'],
                        description=t.get('description', ''),
                        estimated_days=round(days, 1),
                        dependencies=[t['dependency']] if t.get('dependency') else [],
                        assigned_role=t.get('role_category', 'backend')
                    ))
                    
            except Exception as e:
                print(f"LLM Planning Failed: {e}")
        
        if not tasks:
            # Fallback Heuristic
            req_count = len(project_state.srs.requirements)
            is_simple = req_count <= 3
            
            tasks.append(WBSTask(
                id="TASK-000", name="Project Setup", 
                description="Repo & Env Init", 
                estimated_days=0.5 if is_simple else 1.0, dependencies=[]
            ))
            
            for req in project_state.srs.requirements:
                days = 1.0 if req.priority == "High" else 0.5
                tasks.append(WBSTask(
                    id=f"TASK-{req.id}", name=f"Implement {req.id}",
                    description=req.description,
                    estimated_days=days, dependencies=["TASK-000"]
                ))
                
            tasks.append(WBSTask(
                id="TASK-999", name="Testing & QA",
                description="Testing phase",
                estimated_days=1.0, dependencies=["TASK-000"]
            ))

        # Fair per-day rates — SCALED by complexity
        # complexity_score was set by LLM (1-10) or defaults to 3
        # Simple (1-3): freelancer rates, Medium (4-6): mid-range, Complex (7-10): agency rates
        
        if complexity_score <= 3:
            # Simple project: todo app, blog, portfolio
            BASE_RATE = 100  # $/day
        elif complexity_score <= 6:
            # Medium: e-commerce, chat app, CRM
            BASE_RATE = 160  # $/day
        else:
            # Complex: AI, fintech, real-time systems
            BASE_RATE = 220  # $/day
        
        ROLE_MULTIPLIER = {
            "setup": 0.6,
            "backend": 1.0,
            "frontend": 0.9,
            "design": 0.7,
            "test": 0.5,
            "devops": 0.8
        }
        
        total_days = 0
        total_cost = 0.0
        
        for task in tasks:
            role = (task.assigned_role or "backend").lower()
            name_lower = task.name.lower()
            
            # Detect role from task name if not set
            if "setup" in name_lower or "config" in name_lower: role = "setup"
            elif "frontend" in name_lower or "ui" in name_lower: role = "frontend"
            elif "test" in name_lower or "qa" in name_lower: role = "test"
            elif "deploy" in name_lower or "devops" in name_lower: role = "devops"
            elif "design" in name_lower: role = "design"
            
            multiplier = ROLE_MULTIPLIER.get(role, 1.0)
            cost = task.estimated_days * BASE_RATE * multiplier
            total_cost += cost
            total_days += task.estimated_days
        
        # Sanity cap: scale down if LLM over-estimated days
        if total_days > 25:
            scale = 20.0 / total_days
            total_days = round(total_days * scale, 1)
            total_cost = round(total_cost * scale, 2)
            for task in tasks:
                task.estimated_days = round(task.estimated_days * scale, 1)
            
        project_state.plan = ProjectPlan(
            project_id=project_state.id,
            tasks=tasks,
            total_estimated_days=round(total_days, 1),
            estimated_cost=round(total_cost, 2)
        )
        
        self.update_status("completed", f"Plan Created. Cost: ${total_cost:,.2f}")
        return project_state
