"""fastapi-openapi-plus: Library for simplifying OpenAPI documentation in FastAPI.

Библиотека для упрощения документирования OpenAPI в FastAPI проектах.
Автоматизирует рутинные задачи по документированию параметров, схем и примеров.

Основные возможности:
- Хелперы для параметров (query_param, path_param, body_param)
- Typed-хелперы для популярных типов (query_uuid, path_uuid, query_bool, query_int)
- Автоматическая генерация примеров через ExampleGenerators
- Поддержка Pydantic v1 и v2

Пример использования:
    ```python
    from fastapi import APIRouter
    from fastapi_openapi_plus import query_uuid, path_uuid, query_bool
    
    router = APIRouter()
    
    @router.get("/players/{playerId}/statistic")
    async def get_statistic(
        player_id: str = path_uuid(description="Уникальный идентификатор игрока"),
        season_id: str = query_uuid(alias="seasonId", description="ID сезона"),
        include_stats: bool = query_bool(alias="includeStats", description="Включить статистику"),
    ):
        pass
    ```
"""

__version__ = "0.1.0"

# Параметры FastAPI
from fastapi_openapi_plus.params import body_param, path_param, query_param

# Typed-хелперы
from fastapi_openapi_plus.typed_helpers import (
    path_uuid,
    query_bool,
    query_int,
    query_uuid,
)

# Генераторы примеров
from fastapi_openapi_plus.generators import ExampleGenerators

# Pydantic интеграция
from fastapi_openapi_plus.fields import field
from fastapi_openapi_plus.examples import add_example_to_model

__all__ = [
    # Параметры FastAPI
    "query_param",
    "path_param",
    "body_param",
    # Typed-хелперы
    "query_uuid",
    "path_uuid",
    "query_bool",
    "query_int",
    # Генераторы примеров
    "ExampleGenerators",
    # Pydantic интеграция
    "field",
    "add_example_to_model",
    # Версия
    "__version__",
]
