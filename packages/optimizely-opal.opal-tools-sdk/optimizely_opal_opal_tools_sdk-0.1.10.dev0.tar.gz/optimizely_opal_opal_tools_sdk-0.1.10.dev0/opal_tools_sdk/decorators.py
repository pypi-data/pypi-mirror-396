import inspect
import re
import logging
from typing import Callable, Any, List, Dict, Type, get_origin, get_type_hints, Optional, Union
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from .models import Parameter, ParameterType, AuthRequirement
from .logging import get_logger

logger = get_logger(__name__)

def tool(name: str, description: str, auth_requirements: Optional[List[Dict[str, Any]]] = None):
    """Decorator to register a function as an Opal tool.

    Args:
        name: Name of the tool
        description: Description of the tool
        auth_requirements: Authentication requirements (optional)
            Format: [{"provider": "oauth_provider", "scope_bundle": "permissions_scope", "required": True}, ...]
            Example: [{"provider": "google", "scope_bundle": "calendar", "required": True}]

    Returns:
        Decorator function

    Note:
        If your tool requires authentication, define your handler function with two parameters:
        async def my_tool(parameters: ParametersModel, auth_data: Optional[Dict] = None):
            ...
    """
    def decorator(func: Callable):
        # Get the ToolsService instance from the global registry
        from . import _registry

        # Extract parameters from function signature
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        parameters: List[Parameter] = []
        param_model = None

        # Look for a parameter that is a pydantic model (for parameters)
        for param_name, param in sig.parameters.items():
            if param_name in type_hints:
                param_type = type_hints[param_name]
                if hasattr(param_type, '__fields__') or hasattr(param_type, 'model_fields'):  # Pydantic v1 or v2
                    param_model = param_type
                    break

        # If we found a pydantic model, extract parameters
        if param_model:
            model_fields = getattr(param_model, 'model_fields', getattr(param_model, '__fields__', {}))
            for field_name, field in model_fields.items():
                # Get field metadata
                field_info = field.field_info if hasattr(field, 'field_info') else field

                # Determine type
                if hasattr(field, 'outer_type_'):
                    field_type = field.outer_type_
                elif hasattr(field, 'annotation'):
                    field_type = field.annotation
                else:
                    field_type = str

                # Check if the field is Optional (Union with None)
                # Optional[X] is equivalent to Union[X, None]
                type_args = getattr(field_type, '__args__', ())
                is_optional = get_origin(field_type) is Union and type(None) in type_args

                # Extract the actual type from Optional[T]
                if is_optional and type_args:
                    # Get the non-None type from Union[T, None]
                    field_type = next(
                        (arg for arg in type_args if arg is not type(None)),
                        field_type,
                    )

                # Map Python type to Parameter type
                param_type = ParameterType.string
                if field_type is int:
                    param_type = ParameterType.integer
                elif field_type is float:
                    param_type = ParameterType.number
                elif field_type is bool:
                    param_type = ParameterType.boolean
                elif field_type is list or get_origin(field_type) is list:
                    param_type = ParameterType.list
                elif field_type is dict or get_origin(field_type) is dict:
                    param_type = ParameterType.dictionary

                # Determine if required
                field_info_extra = getattr(field_info, "json_schema_extra") or {}
                if "required" in field_info_extra:
                    required = field_info_extra["required"]
                # If the field is typed as Optional, it's not required (check this FIRST)
                elif is_optional:
                    required = False
                # Check for Pydantic v2 is_required() method
                elif hasattr(field_info, 'is_required'):
                    required = field_info.is_required()
                # Fall back to checking if default is ... (Pydantic v1/v2 compatibility)
                elif hasattr(field_info, 'default'):
                    required = field_info.default is ...
                else:
                    # If no default attribute at all, assume required
                    required = True

                # Get description
                description_text = ""
                if hasattr(field_info, 'description'):
                    description_text = field_info.description
                elif hasattr(field, 'description'):
                    description_text = field.description

                parameters.append(Parameter(
                    name=field_name,
                    param_type=param_type,
                    description=description_text,
                    required=required
                ))

                logger.info(f"Registered parameter: {field_name} of type {param_type.value}, required: {required}")
        else:
            logger.warning(f"Warning: No parameter model found for {name}")

        endpoint = f"/tools/{name}"

        # Register the tool with the service
        auth_req_list = None
        if auth_requirements:
            auth_req_list = []
            for auth_req in auth_requirements:
                auth_req_list.append(AuthRequirement(
                    provider=auth_req.get("provider", ""),
                    scope_bundle=auth_req.get("scope_bundle", ""),
                    required=auth_req.get("required", True)
                ))

        logger.info(f"Registering tool {name} with endpoint {endpoint}")

        if not _registry.services:
            logger.warning("No services registered in registry! Make sure to create ToolsService before decorating functions.")

        for service in _registry.services:
            service.register_tool(
                name=name,
                description=description,
                handler=func,
                parameters=parameters,
                endpoint=endpoint,
                auth_requirements=auth_req_list
            )

        return func

    return decorator
