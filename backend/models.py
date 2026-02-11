from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime
import uuid

class ProjectBrief(BaseModel):
    name: str
    description: str
    brief_content: str  # The unstructured text

class Requirement(BaseModel):
    id: str
    description: str
    priority: Literal["High", "Medium", "Low"]
    acceptance_criteria: List[str]

class SRS(BaseModel):
    project_id: str
    requirements: List[Requirement]
    generated_at: datetime = Field(default_factory=datetime.now)

class WBSTask(BaseModel):
    id: str
    name: str
    description: str
    estimated_days: float
    dependencies: List[str] = []
    assigned_role: Optional[str] = None

class ProjectPlan(BaseModel):
    project_id: str
    tasks: List[WBSTask]
    total_estimated_days: float
    estimated_cost: float

class AgentStatus(BaseModel):
    agent_name: str
    status: Literal["idle", "working", "completed", "failed"]
    current_task: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)

class Artifacts(BaseModel):
    file_structure: List[str] = []
    code_snippets: Dict[str, str] = {} # filename -> content

class ProjectState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    brief: ProjectBrief
    srs: Optional[SRS] = None
    plan: Optional[ProjectPlan] = None
    artifacts: Optional[Artifacts] = None
    status: str = "brief_submitted"
    agent_statuses: Dict[str, AgentStatus] = {}
