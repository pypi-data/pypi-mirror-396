"""Хелпер для Pydantic полей с поддержкой v1/v2.

Модуль предоставляет функцию field() для упрощения создания Pydantic полей
с автоматической генерацией примеров через ExampleGenerators.

Поддерживает Pydantic v1 и v2 с автоматическим определением версии.

Пример использования:
    ```python
    from pydantic import BaseModel
    from fastapi_openapi_plus import field
    
    class UserModel(BaseModel):
        name: str = field(description="Имя пользователя", type_hint=str)
        age: int = field(description="Возраст", type_hint=int, ge=0, le=120)
    ```
"""

from typing import Any, Optional

try:
    import pydantic
    from pydantic import Field
except ImportError:  # pragma: no cover
    raise ImportError("pydantic is required. Install it with: pip install pydantic>=1.10.0")

from fastapi_openapi_plus.generators import ExampleGenerators


def _is_pydantic_v2() -> bool:
    """Определяет, используется ли Pydantic v2.
    
    Returns:
        True если Pydantic v2, False если v1
    """
    if hasattr(pydantic, "VERSION"):
        version = pydantic.VERSION
        # Pydantic v2 начинается с "2."
        return version.startswith("2.")
    # Если VERSION нет, проверяем наличие v2-специфичных атрибутов
    return hasattr(pydantic, "BaseModel") and hasattr(pydantic.BaseModel, "model_config")  # pragma: no cover


def field(
    description: str,
    *,
    default: Any = ...,
    alias: Optional[str] = None,
    type_hint: Optional[type] = None,
    example: Optional[Any] = None,
    **kwargs
) -> Any:
    """Хелпер для Pydantic Field с автогенерацией example и поддержкой v1/v2.
    
    Валидирует description и автоматически генерирует example через
    ExampleGenerators, если example не указан явно.
    
    Логика приоритетов для example:
    1. Явно указанный example (имеет наивысший приоритет)
    2. default (если не Ellipsis) используется как example
    3. Автогенерация через type_hint (если указан)
    4. None (если ничего не доступно)
    
    Для Pydantic v1 использует Field(example=...).
    Для Pydantic v2 использует Field(json_schema_extra={"example": ...}).
    
    Args:
        description: Описание поля (обязательно, не может быть пустым)
        default: Значение по умолчанию. Если не Ellipsis (...), используется как example
        alias: Альтернативное имя поля в JSON
        type_hint: Тип для автогенерации example (если example не указан и default не задан)
        example: Явно указанный пример (имеет приоритет над автогенерацией)
        **kwargs: Дополнительные параметры для Field() (ge, le, min_length, etc.)
    
    Returns:
        Field объект Pydantic с description и example (если доступен)
    
    Raises:
        ValueError: Если description пустой или содержит только пробелы
    
    Пример:
        ```python
        from pydantic import BaseModel
        from fastapi_openapi_plus import field
        
        class UserModel(BaseModel):
            # С автогенерацией example
            name: str = field(
                description="Имя пользователя",
                type_hint=str,
            )  # example будет "example_string"
            
            # С явным example
            email: str = field(
                description="Email пользователя",
                example="user@example.com",
            )
            
            # С default как example
            age: int = field(
                description="Возраст",
                default=25,
                ge=0,
                le=120,
            )  # example будет 25
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
    
    # Формируем параметры для Field
    field_params = {
        "description": description,
        **kwargs,
    }
    
    # Добавляем alias если указан
    if alias is not None:
        field_params["alias"] = alias
    
    # Добавляем default если не Ellipsis
    if default is not ...:
        field_params["default"] = default
    
    # Добавляем example в зависимости от версии Pydantic
    if final_example is not None:
        is_v2 = _is_pydantic_v2()
        if is_v2:
            # Pydantic v2: используем json_schema_extra
            # Проверяем, не передан ли уже json_schema_extra
            if "json_schema_extra" in field_params:
                # Если уже есть, обновляем его
                if isinstance(field_params["json_schema_extra"], dict):
                    field_params["json_schema_extra"]["example"] = final_example
                else:
                    # Если это callable, создаем новый dict
                    field_params["json_schema_extra"] = {"example": final_example}
            else:
                field_params["json_schema_extra"] = {"example": final_example}
        else:  # pragma: no cover
            # Pydantic v1: используем example напрямую
            field_params["example"] = final_example
    
    return Field(**field_params)
