"""Workflow execution payload models."""

from typing import Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class WorkflowExecutionCreateRequest(BaseModel):
    """Request model for workflow execution creation."""

    model_config = ConfigDict(populate_by_name=True)

    user_input: Optional[Union[str, dict, list, int, float, bool]] = Field(
        None, description="User input for the workflow execution"
    )
    file_name: Optional[str] = Field(
        None, description="File name associated with the workflow execution"
    )
    propagate_headers: bool = Field(
        default=False,
        description="Enable propagation of X-* HTTP headers to MCP servers during tool execution",
    )
