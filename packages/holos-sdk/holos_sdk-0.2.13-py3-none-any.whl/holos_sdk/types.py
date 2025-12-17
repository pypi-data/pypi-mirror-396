import uuid
from typing import Optional, List, Union, Literal
from pydantic import Field, model_validator
from a2a.types import A2ABaseModel, Artifact


class Plan(A2ABaseModel):
    kind: Literal['plan'] = 'plan'
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the plan")
    context_id: str = Field(..., description="The id of the context for this plan")
    goal: str = Field(..., description="The goal or objective of this plan")
    depend_plans: List['Plan'] = Field(default_factory=list, description="Dependent plans")
    metadata: Optional[dict] = Field(None, description="Metadata for the plan")

class Assignment(A2ABaseModel):
    kind: Literal['assignment'] = 'assignment'
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the assignment")
    context_id: Optional[str] = Field(None, description="The id of the context for this assignment")
    object_id: str = Field(..., description="The id of the object to assign")
    object_kind: str = Field(..., description="The kind of the object to assign")
    assignee_id: str = Field(..., description="The id of the agent who is assigned to handle the object")
    assignee_name: Optional[str] = Field(None, description="The name of the agent who is assigned to handle the object")
    assignee_responsibility: Optional[str] = Field(None, description="The responsibility of the agent who is assigned to handle the object. Could be Accountable, Responsible, Consulted, Informed")
    metadata: Optional[dict] = Field(None, description="Metadata for the assignment")

class TaskArtifact(A2ABaseModel):
    kind: Literal['task-artifact'] = 'task-artifact'
    id: Optional[str] = Field(None, description="Unique identifier for the task artifact, taken from artifact.artifact_id")
    context_id: str
    artifact: Artifact
    task_id: str
    metadata: Optional[dict] = Field(None, description="Metadata for the task artifact")

    @model_validator(mode='after')
    def set_id_from_artifact(self):
        if self.id is None and self.artifact:
            self.id = self.artifact.artifact_id
        return self
