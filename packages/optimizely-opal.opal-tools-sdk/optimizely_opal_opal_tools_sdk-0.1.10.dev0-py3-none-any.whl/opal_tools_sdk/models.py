from enum import Enum
from typing import List, Dict, Any, Optional, Literal, TypedDict
from dataclasses import dataclass

from pydantic import BaseModel, Field


class ParameterType(str, Enum):
    """Types of parameters supported by Opal tools."""

    string = "string"
    integer = "integer"
    number = "number"
    boolean = "boolean"
    list = "array"  # Changed to match main service expectation
    dictionary = "object"  # Standard JSON schema type


@dataclass
class Parameter:
    """Parameter definition for an Opal tool."""

    name: str
    param_type: ParameterType
    description: str
    required: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for the discovery endpoint."""
        return {"name": self.name, "type": self.param_type.value, "description": self.description, "required": self.required}


@dataclass
class AuthRequirement:
    """Authentication requirements for an Opal tool."""

    provider: str  # e.g., "google", "microsoft"
    scope_bundle: str  # e.g., "calendar", "drive"
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for the discovery endpoint."""
        return {"provider": self.provider, "scope_bundle": self.scope_bundle, "required": self.required}


class Credentials(TypedDict):
    """AuthData credentials."""

    access_token: str
    org_sso_id: Optional[str]
    customer_id: str
    instance_id: str
    product_sku: str


class AuthData(TypedDict):
    """Authentication data for an Opal tool."""

    provider: str
    credentials: Credentials


class Environment(TypedDict):
    """Execution environment for an Opal tool. Interactive will provide interaction islands, while headless will not."""

    execution_mode: Literal["headless", "interactive"]


@dataclass
class Function:
    """Function definition for an Opal tool."""

    name: str
    description: str
    parameters: List[Parameter]
    endpoint: str
    auth_requirements: Optional[List[AuthRequirement]] = None
    http_method: str = "POST"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for the discovery endpoint."""
        result = {
            "name": self.name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "endpoint": self.endpoint,
            "http_method": self.http_method,
        }

        if self.auth_requirements:
            result["auth_requirements"] = [auth.to_dict() for auth in self.auth_requirements]

        return result


# Interaction island related classes
class IslandConfig(BaseModel):
    class Field(BaseModel):
        name: str
        label: str
        type: Literal["string", "boolean", "json"]
        value: str = Field(default="")
        hidden: bool = Field(default=False)
        options: list[str] = Field(default=[])

    class Action(BaseModel):
        name: str
        label: str
        type: str
        endpoint: str
        operation: str = Field(default="create")

    fields: list[Field]
    actions: list[Action]
    type: Optional[str] = None
    icon: Optional[str] = None


class IslandResponse(BaseModel):
    class ResponseConfig(BaseModel):
        islands: list[IslandConfig]

    type: Literal["island"]
    config: ResponseConfig
    message: Optional[str] = None

    @classmethod
    def create(cls, islands: list[IslandConfig], message: Optional[str] = None):
        return cls(type="island", config=cls.ResponseConfig(islands=islands), message=message)