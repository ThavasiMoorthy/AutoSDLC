from .base import BaseAgent
from ..models import ProjectState, SRS, Requirement
import uuid
import asyncio

class RequirementAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Requirement Agent")

    async def process(self, project_state: ProjectState) -> ProjectState:
        self.update_status("working", "Analyzing project brief...")
        
        from ..llm import generate_json, GROQ_API_KEY
        
        brief_text = project_state.brief.brief_content

        if GROQ_API_KEY:
            try:
                self.update_status("working", "Consulting AI Model (Groq Llama 3)...")
                system_prompt = """
                You are a Senior Business Analyst. Analyze the project brief and extract a list of functional requirements.
                Return a JSON object with a single key 'requirements', which is a list of objects.
                Each requirement object must have:
                - description: string
                - priority: "High" | "Medium" | "Low"
                - acceptance_criteria: list of strings
                """
                
                response = await generate_json(system_prompt, brief_text)
                req_data = response.get("requirements", [])
                
                requirements = []
                for i, r in enumerate(req_data):
                    requirements.append(Requirement(
                        id=f"REQ-{i+1:03d}",
                        description=r['description'],
                        priority=r['priority'],
                        acceptance_criteria=r['acceptance_criteria']
                    ))
                
                self.update_status("completed", f"AI identified {len(requirements)} requirements.")
                
                project_state.srs = SRS(project_id=project_state.id, requirements=requirements)
                return project_state
                
            except Exception as e:
                print(f"LLM Failed, falling back to heuristics: {e}")
                # Fallthrough to heuristic logic below

        # Simulate processing time if not using LLM
        await asyncio.sleep(1.5)
        
        # Heuristic 1: Split by common delimiters (., ;, and) to find actionable items
        import re
        sentences = re.split(r'[.;\n]+', brief_text)
        
        requirements = []
        for i, raw_line in enumerate(sentences):
            line = raw_line.strip()
            if len(line) < 10: continue # Skip short noise

            # Heuristic 2: Determine Priority
            priority = "Medium"
            lower_line = line.lower()
            if any(w in lower_line for w in ["must", "critical", "urgent", "immediate", "core"]):
                priority = "High"
            elif any(w in lower_line for w in ["maybe", "later", "optional", "nice to have"]):
                priority = "Low"
            
            # Heuristic 3: Generate Acceptance Criteria based on keywords
            criteria = []
            if "login" in lower_line or "auth" in lower_line:
                criteria.append("Verify secure login with hashed passwords.")
                criteria.append("Ensure session management is secure.")
            elif "api" in lower_line:
                criteria.append("Endpoint returns correct JSON structure.")
                criteria.append("Response time under 200ms.")
            elif "ui" in lower_line or "design" in lower_line:
                criteria.append("Matches Figma/Design mockups.")
                criteria.append("Responsive on mobile devices.")
            else:
                criteria.append(f"Verify that '{line[:20]}...' functionality works as expected.")

            req = Requirement(
                id=f"REQ-{i+1:03d}",
                description=line.capitalize(),
                priority=priority,
                acceptance_criteria=criteria
            )
            requirements.append(req)

        if not requirements:
            requirements.append(Requirement(
                id="REQ-001", 
                description="Implement core project functionality defined in brief", 
                priority="High", 
                acceptance_criteria=["Functionality meets user needs"]
            ))

        project_state.srs = SRS(
            project_id=project_state.id,
            requirements=requirements
        )
        
        self.update_status("completed", f"Identified {len(requirements)} requirements (Heuristic Mode).")
        return project_state
