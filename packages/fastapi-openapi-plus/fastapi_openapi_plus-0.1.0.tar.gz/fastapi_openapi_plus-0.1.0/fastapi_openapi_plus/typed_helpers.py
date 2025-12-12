"""Typed-хелперы для популярных типов.

Модуль предоставляет специализированные функции-хелперы для часто используемых
типов (UUID, bool, int) с автоматической генерацией примеров.

Пример использования:
    ```python
    from fastapi import APIRouter
    from fastapi_openapi_plus import query_uuid, path_uuid, query_bool, query_int
    
    router = APIRouter()
    
    @router.get("/players/{playerId}/statistic")
    async def get_statistic(
        player_id: str = path_uuid(description="Уникальный идентификатор игрока"),
        season_id: str = query_uuid(alias="seasonId", description="ID сезона"),
        include_stats: bool = query_bool(alias="includeStats", description="Включить статистику"),
        page: int = query_int(alias="page", description="Номер страницы", ge=1),
    ):
        pass
    ```
"""

from typing import Any, Optional
from uuid import UUID, uuid4

from fastapi_openapi_plus.params import path_param, query_param


def query_uuid(
    description: str,
    alias: Optional[str] = None,
    default: Any = ...,
    **kwargs
) -> Any:
    """Query параметр для UUID с автоматической генерацией example.
    
    Автоматически генерирует example в формате строки UUID.
    
    Args:
        description: Описание параметра (обязательно, не может быть пустым)
        alias: Альтернативное имя параметра в запросе
        default: Значение по умолчанию
        **kwargs: Дополнительные параметры для Query() (ge, le, etc.)
    
    Returns:
        Query объект FastAPI с description и example (UUID в формате строки)
    
    Raises:
        ValueError: Если description пустой или содержит только пробелы
    
    Пример:
        ```python
        season_id: str = query_uuid(
            alias="seasonId",
            description="ID сезона для фильтрации",
        )  # example будет сгенерирован автоматически как str(uuid4())
        ```
    """
    # Генерируем UUID example
    uuid_example = str(uuid4())
    
    # Используем query_param с явным example
    return query_param(
        description=description,
        alias=alias,
        default=default,
        example=uuid_example,
        **kwargs
    )


def path_uuid(
    description: str,
    **kwargs
) -> Any:
    """Path параметр для UUID с автоматической генерацией example.
    
    Автоматически генерирует example в формате строки UUID.
    
    **КРИТИЧНО:** Не принимает параметр alias, так как имя параметра
    берется из шаблона маршрута.
    
    Args:
        description: Описание параметра (обязательно, не может быть пустым)
        **kwargs: Дополнительные параметры для Path() (ge, le, etc.)
                 **НЕ принимает alias** - имя берется из маршрута
    
    Returns:
        Path объект FastAPI с description и example (UUID в формате строки)
    
    Raises:
        ValueError: Если description пустой или содержит только пробелы
        ValueError: Если передан параметр alias (не поддерживается для path параметров)
    
    Пример:
        ```python
        @router.get("/players/{playerId}")
        async def get_player(
            player_id: str = path_uuid(
                description="Уникальный идентификатор игрока",
            ),
        ):
            pass
        ```
    """
    # Проверка, что alias не передан
    if "alias" in kwargs:
        raise ValueError(
            "path_uuid() does not accept 'alias' parameter. "
            "Path parameter name is taken from the route template."
        )
    
    # Генерируем UUID example
    uuid_example = str(uuid4())
    
    # Используем path_param с явным example
    return path_param(
        description=description,
        example=uuid_example,
        **kwargs
    )


def query_bool(
    description: str,
    alias: Optional[str] = None,
    default: bool = False,
    **kwargs
) -> Any:
    """Query параметр для boolean с использованием default как example.
    
    Использует значение default как example для параметра.
    
    Args:
        description: Описание параметра (обязательно, не может быть пустым)
        alias: Альтернативное имя параметра в запросе
        default: Значение по умолчанию (используется как example, по умолчанию False)
        **kwargs: Дополнительные параметры для Query()
    
    Returns:
        Query объект FastAPI с description и example (равным default)
    
    Raises:
        ValueError: Если description пустой или содержит только пробелы
    
    Пример:
        ```python
        include_stats: bool = query_bool(
            alias="includeStats",
            description="Включить статистику",
            default=False,
        )  # example будет False
        ```
    """
    # Используем default как example
    return query_param(
        description=description,
        alias=alias,
        default=default,
        example=default,  # Используем default как example
        **kwargs
    )


def query_int(
    description: str,
    alias: Optional[str] = None,
    default: int = 1,
    ge: Optional[int] = None,
    le: Optional[int] = None,
    **kwargs
) -> Any:
    """Query параметр для int с генерацией example с учетом ограничений.
    
    Генерирует example с учетом ограничений ge (greater or equal) и le (less or equal).
    - Если ge указан → example >= ge
    - Если le указан → example <= le
    - Если оба указаны → ge <= example <= le
    
    Args:
        description: Описание параметра (обязательно, не может быть пустым)
        alias: Альтернативное имя параметра в запросе
        default: Значение по умолчанию (по умолчанию 1)
        ge: Минимальное значение (greater or equal)
        le: Максимальное значение (less or equal)
        **kwargs: Дополнительные параметры для Query()
    
    Returns:
        Query объект FastAPI с description и example (с учетом ограничений)
    
    Raises:
        ValueError: Если description пустой или содержит только пробелы
        ValueError: Если ge > le (некорректные ограничения)
    
    Пример:
        ```python
        # С ограничением ge
        page: int = query_int(
            alias="page",
            description="Номер страницы",
            ge=1,
        )  # example будет >= 1
        
        # С ограничениями ge и le
        page_size: int = query_int(
            alias="pageSize",
            description="Размер страницы",
            ge=1,
            le=200,
        )  # example будет в диапазоне [1, 200]
        ```
    """
    # Генерируем example с учетом ограничений
    example_value = default
    
    # Если есть ограничения, генерируем значение с их учетом
    if ge is not None and le is not None:
        # Оба ограничения указаны
        if ge > le:
            raise ValueError(f"Invalid constraints: ge ({ge}) > le ({le})")
        # Выбираем значение в середине диапазона или ближе к default
        if default >= ge and default <= le:
            example_value = default
        else:
            # Если default вне диапазона, выбираем середину
            example_value = (ge + le) // 2
            if example_value < ge:
                example_value = ge
    elif ge is not None:
        # Только ge указан
        example_value = max(default, ge)
    elif le is not None:
        # Только le указан
        example_value = min(default, le)
    
    # Используем query_param с вычисленным example
    return query_param(
        description=description,
        alias=alias,
        default=default,
        example=example_value,
        ge=ge,
        le=le,
        **kwargs
    )
