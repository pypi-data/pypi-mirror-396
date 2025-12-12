"""Хелперы для параметров FastAPI (query, path, body).

Модуль предоставляет функции-хелперы для упрощения документирования параметров
FastAPI с автоматической генерацией примеров через ExampleGenerators.

Пример использования:
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
        ),
    ):
        pass
    ```
"""

from typing import Any, Optional

from fastapi import Body, Path, Query

from fastapi_openapi_plus.generators import ExampleGenerators


def query_param(
    description: str,
    default: Any = ...,
    alias: Optional[str] = None,
    type_hint: Optional[type] = None,
    example: Optional[Any] = None,
    **kwargs
) -> Any:
    """Хелпер для query параметров с автогенерацией example.
    
    Валидирует description и автоматически генерирует example через
    ExampleGenerators, если example не указан явно.
    
    Args:
        description: Описание параметра (обязательно, не может быть пустым)
        default: Значение по умолчанию. Если не Ellipsis (...), используется как example
        alias: Альтернативное имя параметра в запросе
        type_hint: Тип для автогенерации example (если example не указан)
        example: Явно указанный пример (имеет приоритет над автогенерацией)
        **kwargs: Дополнительные параметры для Query() (ge, le, min_length, etc.)
    
    Returns:
        Query объект FastAPI с description и example (если доступен)
    
    Raises:
        ValueError: Если description пустой или содержит только пробелы
    
    Пример:
        ```python
        # С автогенерацией example
        page: int = query_param(
            description="Номер страницы",
            type_hint=int,
        )  # example будет 1
        
        # С явным example
        page: int = query_param(
            description="Номер страницы",
            example=42,
        )
        
        # С default как example
        page: int = query_param(
            description="Номер страницы",
            default=1,
        )  # example будет 1
        ```
    """
    # Валидация description
    if not description or not description.strip():
        raise ValueError("description is required and cannot be empty")
    
    # Определяем example
    final_example = example
    
    # Если example не указан явно
    if final_example is None:
        # Если default не Ellipsis, используем его как example
        if default is not ...:
            final_example = default
        # Иначе пытаемся автогенерировать через type_hint
        elif type_hint is not None:
            final_example = ExampleGenerators.generate_for_type(type_hint)
            # Если генератор не найден, final_example останется None
    
    # Формируем параметры для Query
    query_params = {
        "description": description,
        **kwargs,
    }
    
    # Добавляем example только если он определен и не передан в kwargs
    if final_example is not None and "example" not in query_params and "examples" not in query_params:
        query_params["example"] = final_example
    
    # Добавляем alias если указан
    if alias is not None:
        query_params["alias"] = alias
    
    # ВАЖНО: всегда передаём default (в т.ч. Ellipsis для обязательных)
    # Query() принимает default первым позиционным аргументом
    return Query(default, **query_params)


def path_param(
    description: str,
    type_hint: Optional[type] = None,
    example: Optional[Any] = None,
    **kwargs
) -> Any:
    """Хелпер для path параметров с автогенерацией example.
    
    Валидирует description и автоматически генерирует example через
    ExampleGenerators, если example не указан явно.
    
    **КРИТИЧНО:** Не принимает параметр alias, так как имя параметра
    берется из шаблона маршрута.
    
    Args:
        description: Описание параметра (обязательно, не может быть пустым)
        type_hint: Тип для автогенерации example (если example не указан)
        example: Явно указанный пример (имеет приоритет над автогенерацией)
        **kwargs: Дополнительные параметры для Path() (ge, le, min_length, etc.)
                 **НЕ принимает alias** - имя берется из маршрута
    
    Returns:
        Path объект FastAPI с description и example (если доступен)
    
    Raises:
        ValueError: Если description пустой или содержит только пробелы
        ValueError: Если передан параметр alias (не поддерживается для path параметров)
    
    Пример:
        ```python
        @router.get("/items/{item_id}")
        async def get_item(
            item_id: int = path_param(
                description="Уникальный идентификатор элемента",
                type_hint=int,
            ),
        ):
            pass
        ```
    """
    # Валидация description
    if not description or not description.strip():
        raise ValueError("description is required and cannot be empty")
    
    # Проверка, что alias не передан (path параметры не поддерживают alias)
    if "alias" in kwargs:
        raise ValueError(
            "path_param() does not accept 'alias' parameter. "
            "Path parameter name is taken from the route template."
        )
    
    # Определяем example
    final_example = example
    
    # Если example не указан явно, пытаемся автогенерировать
    if final_example is None and type_hint is not None:
        final_example = ExampleGenerators.generate_for_type(type_hint)
        # Если генератор не найден, final_example останется None
    
    # Формируем параметры для Path
    path_params = {
        "description": description,
        **kwargs,
    }
    
    # Добавляем example только если он определен и не передан в kwargs
    if final_example is not None and "example" not in path_params and "examples" not in path_params:
        path_params["example"] = final_example
    
    # ВАЖНО: Path-параметры всегда обязательные: default=...
    # Path() принимает default первым позиционным аргументом
    return Path(..., **path_params)


def body_param(
    description: str,
    embed: bool = False,
    example: Optional[Any] = None,
    default: Any = ...,
    type_hint: Optional[type] = None,
    **kwargs
) -> Any:
    """Хелпер для body параметров с автогенерацией example.
    
    Валидирует description и автоматически генерирует example через
    ExampleGenerators, если example не указан явно.
    
    Логика приоритетов для example:
    1. Явно указанный example (имеет наивысший приоритет)
    2. default (если не Ellipsis) используется как example
    3. Автогенерация через type_hint (если указан)
    
    Args:
        description: Описание параметра (обязательно, не может быть пустым)
        embed: Встраивать ли body в схему (по умолчанию False)
        example: Явно указанный пример (имеет приоритет над автогенерацией)
        default: Значение по умолчанию. Если не Ellipsis (...), используется как example
        type_hint: Тип для автогенерации example (если example не указан и default не задан)
        **kwargs: Дополнительные параметры для Body() (media_type, etc.)
    
    Returns:
        Body объект FastAPI с description и example (если доступен)
    
    Raises:
        ValueError: Если description пустой или содержит только пробелы
    
    Пример:
        ```python
        @router.post("/items")
        async def create_item(
            # body_param используется напрямую
            item: ItemModel = body_param(
                description="Данные элемента для создания",
                type_hint=ItemModel,
            ),
        ):
            pass
        
        # С явным example
        item: ItemModel = body_param(
            description="Данные элемента для создания",
            example={"name": "Test", "price": 100},
        )
        
        # С default как example
        item: ItemModel = body_param(
            description="Данные элемента для создания",
            default={"name": "Default", "price": 0},
        )  # example будет {"name": "Default", "price": 0}
        ```
    """
    # Валидация description
    if not description or not description.strip():
        raise ValueError("description is required and cannot be empty")
    
    # Определяем example (унифицированная логика с query_param)
    final_example = example
    
    # Если example не указан явно
    if final_example is None:
        # Если default не Ellipsis, используем его как example
        if default is not ...:
            final_example = default
        # Иначе пытаемся автогенерировать через type_hint
        elif type_hint is not None:
            final_example = ExampleGenerators.generate_for_type(type_hint)
            # Если генератор не найден, final_example останется None
    
    # Формируем параметры для Body
    body_params = {
        "description": description,
        "embed": embed,
        **kwargs,
    }
    
    # Добавляем example только если он определен и не передан в kwargs
    if final_example is not None and "example" not in body_params and "examples" not in body_params:
        body_params["example"] = final_example
    
    # Body() принимает default первым аргументом
    if default is not ...:
        return Body(default, **body_params)
    else:
        return Body(..., **body_params)
