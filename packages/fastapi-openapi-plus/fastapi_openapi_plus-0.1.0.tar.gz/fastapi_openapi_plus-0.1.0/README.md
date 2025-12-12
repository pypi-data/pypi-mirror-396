# fastapi-openapi-plus

Library for simplifying OpenAPI documentation in FastAPI (parameters, schemas, examples).

**Repository:** [github.com/seligoroff/fastapi-openapi-plus](https://github.com/seligoroff/fastapi-openapi-plus)

## Overview

`fastapi-openapi-plus` helps reduce boilerplate when documenting FastAPI endpoints by providing:

- **Helper functions** for parameters (`query_param`, `path_param`, `body_param`)
- **Typed helpers** for common types (`query_uuid`, `path_uuid`, `query_bool`, `query_int`)
- **Automatic example generation** via registry pattern (`ExampleGenerators`)
- **Pydantic v1/v2 compatibility** for field documentation (`field`, `add_example_to_model`)
- **Validation tools** for checking documentation completeness (`validate_on_startup`, `audit` CLI)

Works seamlessly with [`fastapi-errors-plus`](https://github.com/seligoroff/fastapi-errors-plus) for complete OpenAPI documentation coverage.

## Installation

```bash
pip install fastapi-openapi-plus
```

For CLI audit functionality:

```bash
pip install fastapi-openapi-plus[audit]
```

## Quick Start

### Using typed helpers (recommended)

```python
from fastapi import APIRouter
from fastapi_openapi_plus import query_uuid, path_uuid, query_bool, query_int

router = APIRouter()

@router.get("/players/{playerId}/statistic")
async def get_statistic(
    player_id: str = path_uuid(description="Уникальный идентификатор игрока"),
    season_id: str = query_uuid(alias="seasonId", description="ID сезона для фильтрации"),
    include_stats: bool = query_bool(alias="includeStats", description="Включить статистику", default=False),
    page: int = query_int(alias="page", description="Номер страницы", default=1, ge=1),
):
    return {"player_id": player_id, "season_id": season_id}
```

**Result in Swagger UI:**
- ✅ All parameters have descriptions
- ✅ All parameters have realistic examples (auto-generated UUIDs, etc.)
- ✅ Validation constraints (ge=1) are applied

### Using basic parameter helpers

```python
from fastapi import APIRouter
from fastapi_openapi_plus import query_param, path_param, body_param

router = APIRouter()

@router.get("/items/{item_id}")
async def get_item(
    item_id: int = path_param(
        description="Уникальный идентификатор элемента",
        type_hint=int,
    ),
    page: int = query_param(
        description="Номер страницы",
        alias="page",
        default=1,
        type_hint=int,
    ),
):
    return {"item_id": item_id, "page": page}

@router.post("/items")
async def create_item(
    item: dict = body_param(
        description="Данные элемента для создания",
        type_hint=dict,
    ),
):
    return {"item": item}
```

### Using Pydantic field helpers

```python
from pydantic import BaseModel
from fastapi_openapi_plus import field

class UserModel(BaseModel):
    name: str = field(description="Имя пользователя", type_hint=str)
    age: int = field(description="Возраст", type_hint=int, ge=0, le=120)
    email: str = field(description="Email", example="user@example.com")
```

### Using automatic model examples

```python
from pydantic import BaseModel
from fastapi_openapi_plus import add_example_to_model

class UserModel(BaseModel):
    name: str
    age: int

# Автоматически генерирует примеры для всех полей
add_example_to_model(UserModel)

# Теперь в OpenAPI будет пример:
# {"name": "example_string", "age": 1}
```

### Using custom generators

```python
from fastapi_openapi_plus import ExampleGenerators
from uuid import uuid4

# Register custom type generator
class CustomType:
    pass

ExampleGenerators.register(CustomType, lambda: "custom_example")

# Now it works automatically
from fastapi_openapi_plus import query_param

custom_param = query_param(
    description="Custom parameter",
    type_hint=CustomType,
)  # example will be "custom_example"
```

### Validating documentation on startup

```python
from fastapi import FastAPI
from fastapi_openapi_plus.validators import validate_on_startup

app = FastAPI()

# ... define your routes ...

# Validate documentation at startup (outputs warnings, doesn't break app)
validate_on_startup(app)
```

### Using CLI audit

```bash
# Check documentation via app import
python -m fastapi_openapi_plus audit "myapp.main:app"

# Check documentation via OpenAPI URL
python -m fastapi_openapi_plus audit --openapi-url http://localhost:8000/openapi.json

# Save report to file
python -m fastapi_openapi_plus audit "myapp.main:app" -o report.json
```

## API Reference

### Parameter Helpers

#### `query_param(description, default=..., alias=None, type_hint=None, examples=None, **kwargs)`

Helper for query parameters with automatic example generation.

**Parameters:**
- `description` (str, required): Parameter description (cannot be empty)
- `default` (Any, optional): Default value. If not `...`, used as example
- `alias` (str, optional): Alternative parameter name in request
- `type_hint` (type, optional): Type for auto-generating example
- `examples` (List[Dict], optional): Explicit examples (has priority over auto-generation)
- `**kwargs`: Additional parameters for `Query()` (ge, le, min_length, etc.)

**Returns:** `Query` object with description and examples

**Example:**
```python
page: int = query_param(
    description="Номер страницы",
    type_hint=int,
)  # examples will be [{"value": 1}]
```

#### `path_param(description, type_hint=None, examples=None, **kwargs)`

Helper for path parameters with automatic example generation.

**Parameters:**
- `description` (str, required): Parameter description (cannot be empty)
- `type_hint` (type, optional): Type for auto-generating example
- `examples` (List[Dict], optional): Explicit examples (has priority over auto-generation)
- `**kwargs`: Additional parameters for `Path()` (ge, le, min_length, etc.)

**Returns:** `Path` object with description and examples

**Note:** Path parameters do not accept `alias` (name is taken from route template).

**Example:**
```python
item_id: int = path_param(
    description="Уникальный идентификатор элемента",
    type_hint=int,
)
```

#### `body_param(description, embed=False, examples=None, default=..., type_hint=None, **kwargs)`

Helper for body parameters with automatic example generation.

**Parameters:**
- `description` (str, required): Parameter description (cannot be empty)
- `embed` (bool, optional): Embed body in schema (default: False)
- `examples` (List[Dict], optional): Explicit examples (has priority over auto-generation)
- `default` (Any, optional): Default value. If not `...`, used as example
- `type_hint` (type, optional): Type for auto-generating example
- `**kwargs`: Additional parameters for `Body()` (media_type, etc.)

**Returns:** `Body` object with description and examples

**Example:**
```python
item: dict = body_param(
    description="Данные элемента для создания",
    type_hint=dict,
)
```

### Typed Helpers

#### `query_uuid(description, alias=None, default=..., **kwargs)`

Query parameter for UUID with automatic UUID generation.

**Example:**
```python
season_id: str = query_uuid(
    alias="seasonId",
    description="ID сезона для фильтрации",
)
```

#### `path_uuid(description, **kwargs)`

Path parameter for UUID with automatic UUID generation.

**Note:** Does not accept `alias` parameter.

**Example:**
```python
player_id: str = path_uuid(description="Уникальный идентификатор игрока")
```

#### `query_bool(description, alias=None, default=False, **kwargs)`

Query parameter for boolean with `default` used as example.

**Example:**
```python
include_stats: bool = query_bool(
    alias="includeStats",
    description="Включить статистику",
    default=False,
)
```

#### `query_int(description, alias=None, default=..., ge=None, le=None, **kwargs)`

Query parameter for integer with example generation considering constraints.

**Example:**
```python
page: int = query_int(
    alias="page",
    description="Номер страницы",
    default=1,
    ge=1,
)
```

### Example Generators

#### `ExampleGenerators`

Registry for type-to-generator mappings.

**Methods:**

- `register(type_hint, generator)`: Register a generator for a type
- `generate_for_type(type_hint)`: Generate example for a type (returns `None` if not found)
- `reset()`: Reset registry to default generators
- `unregister(type_hint)`: Remove generator for a type

**Pre-registered types:** `str`, `int`, `bool`, `float`, `UUID`, `datetime`

**Example:**
```python
from fastapi_openapi_plus import ExampleGenerators

# Register custom generator
ExampleGenerators.register(MyType, lambda: MyType.example())

# Generate example
example = ExampleGenerators.generate_for_type(MyType)  # Returns MyType.example()
```

### Pydantic Integration

#### `field(description, *, default=..., alias=None, type_hint=None, example=None, **kwargs)`

Helper for Pydantic `Field` with automatic example generation and v1/v2 support.

**Parameters:**
- `description` (str, required): Field description (cannot be empty)
- `default` (Any, optional): Default value. If not `...`, used as example
- `alias` (str, optional): Alternative field name in JSON
- `type_hint` (type, optional): Type for auto-generating example
- `example` (Any, optional): Explicit example (has priority over auto-generation)
- `**kwargs`: Additional parameters for `Field()` (ge, le, min_length, etc.)

**Returns:** Pydantic `Field` object with description and example

**Example:**
```python
from pydantic import BaseModel
from fastapi_openapi_plus import field

class UserModel(BaseModel):
    name: str = field(description="Имя пользователя", type_hint=str)
    age: int = field(description="Возраст", type_hint=int, ge=0, le=120)
```

#### `add_example_to_model(model)`

Adds automatically generated examples to a Pydantic model.

**Parameters:**
- `model` (Type[BaseModel]): Pydantic model class

**Returns:** The same model class with added examples

**Note:** For Pydantic v2, automatically calls `model.model_rebuild()` after configuration changes.

**Example:**
```python
from pydantic import BaseModel
from fastapi_openapi_plus import add_example_to_model

class UserModel(BaseModel):
    name: str
    age: int

add_example_to_model(UserModel)
# Now OpenAPI will include example: {"name": "example_string", "age": 1}
```

### Validation Tools

#### `validate_on_startup(app)`

Validates OpenAPI documentation completeness at application startup.

**Parameters:**
- `app` (FastAPI): FastAPI application

**Behavior:**
- Checks for missing `description` and `example` in parameters and request body
- Outputs `warnings.warn()` for issues (does not raise exceptions)
- Does not break application startup

**Example:**
```python
from fastapi import FastAPI
from fastapi_openapi_plus.validators import validate_on_startup

app = FastAPI()

# ... define routes ...

validate_on_startup(app)
```

#### CLI: `audit`

Command-line tool for auditing OpenAPI documentation.

**Usage:**
```bash
# Via app import
python -m fastapi_openapi_plus audit "myapp.main:app"

# Via OpenAPI URL
python -m fastapi_openapi_plus audit --openapi-url http://localhost:8000/openapi.json

# Save report
python -m fastapi_openapi_plus audit "myapp.main:app" -o report.json
```

**Exit codes:**
- `0`: No issues found
- `1`: Issues found

## How Auto-Generation Works

Auto-generation of examples works **only** if:

1. ✅ Explicit `examples` parameter is provided — always works
2. ✅ Typed helper is used (`query_uuid`, `path_uuid`, `query_bool`, `query_int`) — always works
3. ✅ `type_hint` is provided and a generator is registered for the type — works after registration
4. ❌ Otherwise — `example` is not generated (remains `None`)

**Important:** The library does not substitute placeholder data if a generator is not found.

## Features

- ✅ **Transparent API**: Simple wrappers over FastAPI/Pydantic functions
- ✅ **Explicit parameters**: All parameters must be explicitly specified (description is required)
- ✅ **Pydantic v1/v2 compatibility**: Automatic version detection
- ✅ **Type normalization**: Handles `Optional[T]`, `Union[T, None]`, `Annotated[T, ...]`
- ✅ **Test isolation**: `ExampleGenerators.reset()` and `unregister()` for clean tests
- ✅ **Validation tools**: Startup validation and CLI audit

## Requirements

- Python >= 3.8
- FastAPI >= 0.104.0
- Pydantic >= 1.10.0

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=fastapi_openapi_plus --cov-report=term-missing

# Run linter
ruff check .

# Run type checker
mypy fastapi_openapi_plus/
```

## License

MIT
