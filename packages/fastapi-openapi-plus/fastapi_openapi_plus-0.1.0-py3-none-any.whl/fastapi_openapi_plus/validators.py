"""Валидация полноты OpenAPI документации.

Модуль предоставляет функцию validate_on_startup() для мягкой валидации
OpenAPI документации при старте FastAPI приложения.

Валидация выводит warnings при обнаружении проблем, но не ломает приложение.
"""

import warnings
from typing import Any, Dict, List

try:
    from fastapi import FastAPI
except ImportError:  # pragma: no cover
    raise ImportError("fastapi is required. Install it with: pip install fastapi>=0.104.0")


def _check_parameter(param: Dict[str, Any], param_name: str, path: str, method: str) -> List[str]:
    """Проверяет параметр на наличие description и example.
    
    Args:
        param: Словарь параметра из OpenAPI схемы
        param_name: Имя параметра
        path: Путь эндпоинта
        method: HTTP метод
    
    Returns:
        Список найденных проблем (пустой, если проблем нет)
    """
    issues = []
    
    # Проверка description
    if "description" not in param or not param.get("description", "").strip():
        issues.append(
            f"{method.upper()} {path}: parameter '{param_name}' missing description"
        )
    
    # Проверка example/examples
    # FastAPI может хранить examples в разных местах:
    # 1. На верхнем уровне параметра: param["example"] или param["examples"]
    # 2. Внутри schema: param["schema"]["example"] или param["schema"]["examples"]
    has_example = (
        "example" in param or
        ("examples" in param and param.get("examples"))
    )
    
    # Проверяем также внутри schema
    schema = param.get("schema", {})
    if not has_example:
        has_example = (
            "example" in schema or
            ("examples" in schema and schema.get("examples"))
        )
    
    if not has_example:
        issues.append(
            f"{method.upper()} {path}: parameter '{param_name}' missing example"
        )
    
    return issues


def _check_request_body(request_body: Dict[str, Any], path: str, method: str) -> List[str]:
    """Проверяет request body на наличие description и example.
    
    Args:
        request_body: Словарь request body из OpenAPI схемы
        path: Путь эндпоинта
        method: HTTP метод
    
    Returns:
        Список найденных проблем (пустой, если проблем нет)
    """
    issues = []
    
    # Проверка description
    if "description" not in request_body or not request_body.get("description", "").strip():
        issues.append(
            f"{method.upper()} {path}: request body missing description"
        )
    
    # Проверка example/examples в content
    content = request_body.get("content", {})
    has_example = False
    
    for media_type, media_schema in content.items():
        # 1) Проверяем пример на уровне content
        if media_schema.get("example") or media_schema.get("examples"):
            has_example = True
            break
        # 2) Проверяем пример внутри schema
        schema = media_schema.get("schema", {})
        if "example" in schema or ("examples" in schema and schema.get("examples")):
            has_example = True
            break
    
    if not has_example:
        issues.append(
            f"{method.upper()} {path}: request body missing example"
        )
    
    return issues


def validate_on_startup(app: FastAPI) -> None:
    """Валидация полноты OpenAPI документации при старте приложения.
    
    Проверяет наличие description и example у всех параметров и request body.
    Выводит warnings при обнаружении проблем, но не ломает приложение.
    
    **ВАЖНО:** Функция не выбрасывает исключения, только выводит warnings.
    Это позволяет приложению запускаться даже при неполной документации.
    
    Args:
        app: FastAPI приложение для валидации
    
    Пример:
        ```python
        from fastapi import FastAPI
        from fastapi_openapi_plus import validate_on_startup
        
        app = FastAPI()
        
        @app.get("/items/{item_id}")
        async def get_item(item_id: int):
            return {"item_id": item_id}
        
        # Валидация при старте
        validate_on_startup(app)
        ```
    """
    try:
        openapi_schema = app.openapi()
    except Exception as e:  # pragma: no cover
        # Если не удалось получить схему, выводим предупреждение и выходим
        warnings.warn(
            f"Failed to generate OpenAPI schema: {e}. Skipping validation.",
            UserWarning,
            stacklevel=2
        )
        return
    
    issues = []
    paths = openapi_schema.get("paths", {})
    
    for path, methods in paths.items():
        if not isinstance(methods, dict):  # pragma: no cover
            continue
        
        # Извлекаем path-level параметры
        path_level_params = methods.get("parameters", [])
        
        for method, endpoint in methods.items():
            if not isinstance(endpoint, dict):  # pragma: no cover
                continue
            
            # Пропускаем не-HTTP методы
            if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head", "trace"}:
                continue
            
            # Объединяем path-level и operation-level параметры
            parameters = list(path_level_params) + endpoint.get("parameters", [])
            for param in parameters:
                if not isinstance(param, dict):  # pragma: no cover
                    continue
                
                param_name = param.get("name", "unknown")
                param_issues = _check_parameter(param, param_name, path, method)
                issues.extend(param_issues)
            
            # Проверка request body
            request_body = endpoint.get("requestBody")
            if request_body and isinstance(request_body, dict):
                body_issues = _check_request_body(request_body, path, method)
                issues.extend(body_issues)
    
    # Выводим warnings для всех найденных проблем
    for issue in issues:
        warnings.warn(
            f"OpenAPI validation: {issue}",
            UserWarning,
            stacklevel=2
        )
