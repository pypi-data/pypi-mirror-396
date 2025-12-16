"""Typed models for MARSGuard SDK (enforced schema).

This module defines the Pydantic models used for request and response schemas
when interacting with the MARSGuard backend API.

Each model and field is documented for IDE hover support and user clarity.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class AppModel(BaseModel):
    """
    Represents an application for which guardrails are to be generated.

    Attributes:
        name (str): The name of the application.
        description (Optional[str]): A brief description of the application.
    """
    name: str = Field(..., description="The name of the application.")
    description: Optional[str] = Field(
        None, description="A brief description of the application (optional)."
    )

class ModelSpec(BaseModel):
    """
    Model specification for the LLM provider and model name.

    Attributes:
        provider (Optional[str]): The name of the LLM provider (default: 'openai').
        name (str): The name or identifier of the model to use.
    """
    provider: Optional[str] = Field(
        "openai", description="The name of the LLM provider (default: 'openai')."
    )
    name: str = Field(..., description="The name or identifier of the model to use.")

class GenerateGuardrailsRequest(BaseModel):
    """
    Request schema for the /guardrails/generate endpoint.

    Used to request the generation of guardrails for a specific application and domain.

    Attributes:
        app (AppModel): The application details.
        domain (str): The domain or industry (e.g., 'insurance', 'finance').
        custom (Optional[str]): Optional custom instructions or context.
        model (Optional[ModelSpec]): Optional model specification.
        project_spec (Optional[Dict[str, Any]]): Optional project-specific configuration.
    """
    app: AppModel = Field(..., description="The application details for guardrails generation.")
    domain: str = Field(..., description="The domain or industry (e.g., 'insurance', 'finance').")
    custom: Optional[str] = Field(
        None, description="Optional custom instructions or context for guardrails generation."
    )
    model: ModelSpec = Field(
        None, description="Model specification for the LLM."
    )
    project_spec: Optional[Dict[str, Any]] = Field(
        None, description="Optional project-specific configuration as a dictionary."
    )

class MinimalGuardrailsResponse(BaseModel):
    """
    Response schema for the /guardrails/generate endpoint.

    Attributes:
        guardrails (Dict[str, Any]): The generated guardrails as a dictionary.
    """
    guardrails: Dict[str, Any] = Field(
        ..., description="The generated guardrails as a dictionary."
    )

__all__ = [
    "AppModel",
    "ModelSpec",
    "GenerateGuardrailsRequest",
    "MinimalGuardrailsResponse",
]
