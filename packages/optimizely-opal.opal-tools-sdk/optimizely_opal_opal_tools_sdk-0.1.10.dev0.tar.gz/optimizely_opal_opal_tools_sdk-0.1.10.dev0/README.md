# Opal Tools SDK for Python

This SDK simplifies the creation of tools services compatible with the Opal Tools Management Service.

## Features

- Easy definition of tool functions with decorators
- Automatic generation of discovery endpoints
- Parameter validation and type checking
- Authentication helpers
- FastAPI integration
- Island components for interactive UI responses

## Installation

```bash
pip install optimizely-opal.opal-tools-sdk
```

Note: While the package is installed as `optimizely-opal.opal-tools-sdk`, you'll still import it in your code as `opal_tools_sdk`:

```python
# Import using the package name
from opal_tools_sdk import ToolsService, tool, IslandResponse, IslandConfig
```

## Usage

```python
from opal_tools_sdk import ToolsService, tool
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()
tools_service = ToolsService(app)

class WeatherParameters(BaseModel):
    location: str
    units: str = "metric"

@tool("get_weather", "Gets current weather for a location")
async def get_weather(parameters: WeatherParameters):
    # Implementation...
    return {"temperature": 22, "condition": "sunny"}

# Discovery endpoint is automatically created at /discovery
```

## Authentication

The SDK provides two ways to require authentication for your tools:

### 1. Using the `@requires_auth` decorator

```python
from opal_tools_sdk import ToolsService, tool, AuthData
from opal_tools_sdk.auth import requires_auth
from pydantic import BaseModel
from fastapi import FastAPI
from typing import Optional

app = FastAPI()
tools_service = ToolsService(app)

class CalendarParameters(BaseModel):
    date: str
    timezone: str = "UTC"

# Single authentication requirement
@requires_auth(provider="google", scope_bundle="calendar", required=True)
@tool("get_calendar_events", "Gets calendar events for a date")
async def get_calendar_events(parameters: CalendarParameters, auth_data: Optional[AuthData] = None):
    # The auth_data parameter contains authentication information
    if auth_data:
        token = auth_data["credentials"]["access_token"]

    # Use the token to make authenticated requests
    # ...

    return {"events": ["Meeting at 10:00", "Lunch at 12:00"]}

# Multiple authentication requirements (tool can work with either provider)
@requires_auth(provider="google", scope_bundle="calendar", required=True)
@requires_auth(provider="microsoft", scope_bundle="outlook", required=True)
@tool("get_calendar_availability", "Check calendar availability")
async def get_calendar_availability(parameters: CalendarParameters, auth_data: Optional[AuthData] = None):
    provider = ""
    token = ""
    
    if auth_data:
        provider = auth_data["provider"]
        token = auth_data["credentials"]["access_token"]

        if provider == "google":
            # Use Google Calendar API
            pass
        elif provider == "microsoft":
            # Use Microsoft Outlook API
            pass

    return {"available": True, "provider_used": provider}
```

### 2. Specifying auth requirements in the `@tool` decorator

```python
@tool(
    "get_email",
    "Gets emails from the user's inbox",
    auth_requirements=[
        {"provider": "google", "scope_bundle": "gmail", "required": True}
    ]
)
async def get_email(parameters: EmailParameters, auth_data: Optional[AuthData] = None):
    # Implementation...
    return {"emails": ["Email 1", "Email 2"]}
```

## Island Components

The SDK includes Island components for creating interactive UI responses that allow users to input data and trigger actions.

### Weather Tool with Interactive Island

```python
from opal_tools_sdk import ToolsService, tool, IslandResponse, IslandConfig
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()
tools_service = ToolsService(app)

class WeatherParameters(BaseModel):
    location: str
    units: str = "metric"

@tool("get_weather", "Gets current weather for a location")
async def get_weather(parameters: WeatherParameters):
    # Get weather data (implementation details omitted)
    weather_data = {"temperature": 22, "condition": "sunny", "humidity": 65}
    
    # Create an interactive island for weather settings
    island = IslandConfig(
        fields=[
            IslandConfig.Field(
                name="location",
                label="Location",
                type="string",
                value=parameters.location
            ),
            IslandConfig.Field(
                name="units",
                label="Temperature Units",
                type="string",
                value=parameters.units,
                options=["metric", "imperial", "kelvin"]
            ),
            IslandConfig.Field(
                name="current_temp",
                label="Current Temperature",
                type="string",
                value=f"{weather_data['temperature']}°{'C' if parameters.units == 'metric' else 'F'}"
            )
        ],
        actions=[
            IslandConfig.Action(
                name="refresh_weather",
                label="Refresh Weather",
                type="button",
                endpoint="/tools/get_weather",
                operation="update"
            )
        ]
    )
    
    return IslandResponse.create([island])
```

### Island Components

#### IslandConfig.Field
Fields represent data inputs in the UI:
- `name`: Programmatic field identifier
- `label`: Human-readable label
- `type`: Field type (`"string"`, `"boolean"`, `"json"`)
- `value`: Current field value (optional)
- `hidden`: Whether to hide from user (optional, default: False)
- `options`: Available options for selection (optional)

#### IslandConfig.Action
Actions represent buttons or operations:
- `name`: Programmatic action identifier
- `label`: Human-readable button label
- `type`: UI element type (typically `"button"`)
- `endpoint`: API endpoint to call
- `operation`: Operation type (default: `"create"`)

#### IslandConfig
Contains the complete island configuration:
- `fields`: List of IslandConfig.Field objects
- `actions`: List of IslandConfig.Action objects
- `type`: Island type for UI rendering (optional, default: `None`)
- `icon`: Icon to display in the island (optional, default: `None`)

#### IslandResponse
The response wrapper for islands:
- Use `IslandResponse.create([islands])` to create responses
- Supports multiple islands per response

## Type Definitions

The SDK provides several TypedDict and dataclass definitions for better type safety:

### Authentication Types
- `AuthData`: TypedDict containing provider and credentials information
- `Credentials`: TypedDict with access_token, org_sso_id, customer_id, instance_id, and product_sku
- `AuthRequirement`: Dataclass for specifying authentication requirements

### Execution Environment
- `Environment`: TypedDict specifying execution mode (`"headless"` or `"interactive"`)

### Parameter Types
- `ParameterType`: Enum for supported parameter types (string, integer, number, boolean, list, dictionary)
- `Parameter`: Dataclass for tool parameter definitions
- `Function`: Dataclass for complete tool function definitions

These types are automatically imported when you import from `opal_tools_sdk` and provide better IDE support and type checking.

## Documentation

See full documentation for more examples and configuration options.
