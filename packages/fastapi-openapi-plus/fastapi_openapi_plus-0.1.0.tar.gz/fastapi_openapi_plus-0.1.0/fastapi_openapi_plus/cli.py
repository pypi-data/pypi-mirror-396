"""CLI-утилита для аудита OpenAPI документации.

Модуль предоставляет команду audit() для проверки полноты OpenAPI документации.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import click
except ImportError:  # pragma: no cover
    raise ImportError(
        "click is required for CLI functionality. "
        "Install it with: pip install fastapi-openapi-plus[audit]"
    )

try:
    from fastapi import FastAPI
except ImportError:  # pragma: no cover
    raise ImportError("fastapi is required. Install it with: pip install fastapi>=0.104.0")


def _check_parameter(param: Dict[str, Any], param_name: str, path: str, method: str) -> List[Dict[str, str]]:
    """Проверяет параметр на наличие description и example.
    
    Args:
        param: Словарь параметра из OpenAPI схемы
        param_name: Имя параметра
        path: Путь эндпоинта
        method: HTTP метод
    
    Returns:
        Список найденных проблем
    """
    issues = []
    
    # Проверка description
    if "description" not in param or not param.get("description", "").strip():
        issues.append({
            "type": "missing_description",
            "path": path,
            "method": method.upper(),
            "parameter": param_name,
            "message": f"{method.upper()} {path}: parameter '{param_name}' missing description"
        })
    
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
        issues.append({
            "type": "missing_example",
            "path": path,
            "method": method.upper(),
            "parameter": param_name,
            "message": f"{method.upper()} {path}: parameter '{param_name}' missing example"
        })
    
    return issues


def _check_request_body(request_body: Dict[str, Any], path: str, method: str) -> List[Dict[str, str]]:
    """Проверяет request body на наличие description и example.
    
    Args:
        request_body: Словарь request body из OpenAPI схемы
        path: Путь эндпоинта
        method: HTTP метод
    
    Returns:
        Список найденных проблем
    """
    issues = []
    
    # Проверка description
    if "description" not in request_body or not request_body.get("description", "").strip():
        issues.append({
            "type": "missing_description",
            "path": path,
            "method": method.upper(),
            "parameter": "requestBody",
            "message": f"{method.upper()} {path}: request body missing description"
        })
    
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
        issues.append({
            "type": "missing_example",
            "path": path,
            "method": method.upper(),
            "parameter": "requestBody",
            "message": f"{method.upper()} {path}: request body missing example"
        })
    
    return issues


def _audit_openapi_schema(openapi_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Аудит OpenAPI схемы на полноту документации.
    
    Args:
        openapi_schema: OpenAPI схема
    
    Returns:
        Словарь с результатами аудита
    """
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
    
    # Группируем проблемы по типам
    missing_descriptions = [i for i in issues if i["type"] == "missing_description"]
    missing_examples = [i for i in issues if i["type"] == "missing_example"]
    
    return {
        "total_issues": len(issues),
        "missing_descriptions": len(missing_descriptions),
        "missing_examples": len(missing_examples),
        "issues": issues
    }


def _get_app_from_import_path(import_path: str) -> FastAPI:
    """Получает FastAPI приложение из строки импорта.
    
    Args:
        import_path: Строка вида "module.path:app"
    
    Returns:
        FastAPI приложение
    
    Raises:
        ImportError: Если не удалось импортировать приложение
    """
    if ":" not in import_path:
        raise ValueError(f"Invalid import path format: {import_path}. Expected 'module.path:app'")
    
    module_path, app_name = import_path.rsplit(":", 1)
    
    try:
        from importlib import import_module
        
        module = import_module(module_path)
        app = getattr(module, app_name)
        
        if not isinstance(app, FastAPI):
            raise ValueError(f"{app_name} is not a FastAPI application")
        
        return app
    except ImportError as e:
        raise ImportError(f"Failed to import {import_path}: {e}")


@click.command()
@click.argument('app_import', required=False)
@click.option(
    '--openapi-url',
    help='URL для получения OpenAPI схемы (например, http://localhost:8000/openapi.json)'
)
@click.option(
    '-o', '--output',
    type=click.Path(),
    help='Путь к файлу для сохранения JSON отчета'
)
def audit(app_import: Optional[str], openapi_url: Optional[str], output: Optional[str]) -> None:
    """Аудит OpenAPI документации FastAPI приложения.
    
    Проверяет полноту документации (наличие description и example у параметров).
    
    Можно использовать в двух режимах:
    1. Через импорт приложения: python -m fastapi_openapi_plus audit "myapp.main:app"
    2. Через URL OpenAPI схемы: python -m fastapi_openapi_plus audit --openapi-url http://localhost:8000/openapi.json
    
    Args:
        app_import: Путь импорта к FastAPI приложению (например, "myapp.main:app")
        openapi_url: URL для получения OpenAPI схемы
        output: Путь к файлу для сохранения JSON отчета
    
    Примеры:
        ```bash
        # Через импорт приложения
        python -m fastapi_openapi_plus audit "myapp.main:app"
        
        # Через URL
        python -m fastapi_openapi_plus audit --openapi-url http://localhost:8000/openapi.json
        
        # С сохранением отчета
        python -m fastapi_openapi_plus audit "myapp.main:app" -o report.json
        ```
    """
    openapi_schema = None
    
    # Получаем OpenAPI схему
    if openapi_url:
        try:
            import urllib.request
            with urllib.request.urlopen(openapi_url) as response:
                openapi_schema = json.loads(response.read().decode())
        except Exception as e:  # pragma: no cover
            click.echo(f"Error fetching OpenAPI schema from {openapi_url}: {e}", err=True)
            sys.exit(1)
    elif app_import:
        try:
            app = _get_app_from_import_path(app_import)
            openapi_schema = app.openapi()
        except Exception as e:  # pragma: no cover
            click.echo(f"Error importing application from {app_import}: {e}", err=True)
            sys.exit(1)
    else:  # pragma: no cover
        click.echo("Error: Either app_import or --openapi-url must be provided", err=True)
        click.echo(audit.get_help(click.Context(audit)))
        sys.exit(1)
    
    # Выполняем аудит
    report = _audit_openapi_schema(openapi_schema)
    
    # Выводим результаты
    if report["total_issues"] == 0:
        click.echo("✅ OpenAPI documentation is complete. No issues found.")
        exit_code = 0
    else:
        click.echo(f"⚠️  Found {report['total_issues']} issue(s):")
        click.echo(f"   - Missing descriptions: {report['missing_descriptions']}")
        click.echo(f"   - Missing examples: {report['missing_examples']}")
        click.echo("\nIssues:")
        for issue in report["issues"]:
            click.echo(f"  • {issue['message']}")
        exit_code = 1
    
    # Сохраняем отчет, если указан output
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        click.echo(f"\nReport saved to {output_path}")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    audit()
