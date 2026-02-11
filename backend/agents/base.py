from abc import ABC, abstractmethod
from typing import Any, Dict
from ..models import ProjectState, AgentStatus

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.status = AgentStatus(agent_name=name, status="idle")

    def update_status(self, status: str, task: str = None):
        self.status.status = status
        if task:
            self.status.current_task = task
        self.status.last_updated = self.status.last_updated.now()

    @abstractmethod
    async def process(self, project_state: ProjectState) -> ProjectState:
        """
        Process the project state and return the updated state.
        """
        pass
