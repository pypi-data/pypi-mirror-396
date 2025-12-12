"""Генерация примеров для Pydantic моделей.

Модуль предоставляет функцию add_example_to_model() для автоматической
генерации примеров для всех полей Pydantic модели через ExampleGenerators.

Поддерживает Pydantic v1 и v2 с автоматическим определением версии.

Пример использования:
    ```python
    from pydantic import BaseModel
    from fastapi_openapi_plus import add_example_to_model
    
    class UserModel(BaseModel):
        name: str
        age: int
    
    # Автоматически генерирует примеры для всех полей
    add_example_to_model(UserModel)
    ```
"""

from typing import Any, Dict, Type, TypeVar

try:
    import pydantic
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    raise ImportError("pydantic is required. Install it with: pip install pydantic>=1.10.0")

from fastapi_openapi_plus.generators import ExampleGenerators

T = TypeVar("T", bound=BaseModel)


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


def _get_model_fields(model: Type[BaseModel]) -> Dict[str, Any]:
    """Получает поля модели в зависимости от версии Pydantic.
    
    Args:
        model: Класс Pydantic модели
    
    Returns:
        Словарь полей модели (имя -> FieldInfo)
    """
    is_v2 = _is_pydantic_v2()
    if is_v2:
        # Pydantic v2: используем model_fields
        return getattr(model, "model_fields", {})
    else:
        # Pydantic v1: используем __fields__
        # В v2 окружении может быть предупреждение, но это нормально для v1 моделей
        # Используем getattr с fallback, чтобы избежать ошибок
        try:
            return getattr(model, "__fields__", {})
        except AttributeError:  # pragma: no cover
            # Если __fields__ недоступен, пробуем model_fields (для совместимости)
            return getattr(model, "model_fields", {})


def _generate_model_example(model: Type[BaseModel]) -> Dict[str, Any]:
    """Генерирует пример для модели на основе её полей.
    
    Использует ExampleGenerators для генерации примеров для каждого поля.
    Обрабатывает вложенные модели рекурсивно.
    
    Args:
        model: Класс Pydantic модели
    
    Returns:
        Словарь с примерами для всех полей модели
    """
    example = {}
    fields = _get_model_fields(model)
    
    for field_name, field_info in fields.items():
        # Получаем тип поля
        field_type = None
        if hasattr(field_info, "annotation"):
            # Pydantic v2
            field_type = field_info.annotation
        elif hasattr(field_info, "type_"):  # pragma: no cover
            # Pydantic v1
            field_type = field_info.type_
        
        # Генерируем пример для поля
        if field_type is not None:
            # Проверяем, является ли тип вложенной моделью
            if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                # Рекурсивно генерируем пример для вложенной модели
                nested_example = _generate_model_example(field_type)
                example[field_name] = nested_example
            else:
                # Генерируем пример через ExampleGenerators
                field_example = ExampleGenerators.generate_for_type(field_type)
                if field_example is not None:
                    example[field_name] = field_example
                # Если генератор не найден, поле отсутствует в примере
                # (или можно установить None, но лучше не включать)
    
    return example


def add_example_to_model(model: Type[T]) -> Type[T]:
    """Добавляет автоматически сгенерированный пример к Pydantic модели.
    
    Генерирует примеры для всех полей модели через ExampleGenerators
    и добавляет их в конфигурацию модели для отображения в OpenAPI.
    
    **КРИТИЧНО для Pydantic v2:** После изменения model_config
    обязательно вызывается model.model_rebuild().
    
    Поддерживает:
    - Pydantic v1: использует Config.schema_extra["example"]
    - Pydantic v2: использует model_config.json_schema_extra["example"] + model_rebuild()
    - Вложенные модели (рекурсивно)
    - Optional поля
    
    Args:
        model: Класс Pydantic модели
    
    Returns:
        Тот же класс модели с добавленным примером
    
    Пример:
        ```python
        from pydantic import BaseModel
        from fastapi_openapi_plus import add_example_to_model
        
        class UserModel(BaseModel):
            name: str
            age: int
        
        # Автоматически генерирует примеры
        add_example_to_model(UserModel)
        
        # Теперь в OpenAPI будет пример:
        # {"name": "example_string", "age": 1}
        ```
    """
    # Генерируем пример для модели
    example = _generate_model_example(model)
    
    if not example:
        # Если пример пустой, ничего не делаем
        return model
    
    is_v2 = _is_pydantic_v2()
    
    if is_v2:
        # Pydantic v2: безопасное обновление model_config
        # В v2 лучше заменять model_config целиком, а не мутировать inplace
        current = dict(getattr(model, "model_config", {}) or {})
        existing_jse = current.get("json_schema_extra")
        
        # Если json_schema_extra - это callable, создаем новый dict
        if callable(existing_jse):
            jse = {}
        else:
            jse = dict(existing_jse or {})
        
        jse["example"] = example
        current["json_schema_extra"] = jse
        model.model_config = current
        
        # КРИТИЧНО: вызываем model_rebuild() после изменения конфигурации
        model.model_rebuild()
    else:  # pragma: no cover
        # Pydantic v1: используем Config.schema_extra
        if not hasattr(model, "Config"):
            # Создаем Config класс если его нет
            class Config:
                pass
            model.Config = Config
        
        # Получаем или создаем schema_extra
        if not hasattr(model.Config, "schema_extra"):
            model.Config.schema_extra = {}
        
        schema_extra = model.Config.schema_extra
        if not isinstance(schema_extra, dict):
            schema_extra = {}
            model.Config.schema_extra = schema_extra
        
        # Добавляем example
        schema_extra["example"] = example
    
    return model
