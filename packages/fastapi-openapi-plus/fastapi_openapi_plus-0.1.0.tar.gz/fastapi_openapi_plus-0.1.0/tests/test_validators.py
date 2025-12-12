"""Тесты для validators.py.

Тесты для функции validate_on_startup() с проверкой вывода warnings
и отсутствия исключений при проблемах с документацией.
"""

import warnings
import pytest
from fastapi import FastAPI

from fastapi_openapi_plus.validators import validate_on_startup


@pytest.mark.unit
class TestValidateOnStartup:
    """Тесты для функции validate_on_startup()."""
    
    def test_validate_on_startup_no_issues(self):
        """Тест валидации приложения без проблем."""
        from fastapi_openapi_plus import query_param, path_param
        
        app = FastAPI()
        
        @app.get("/items/{item_id}")
        async def get_item(
            item_id: int = path_param(description="Item ID", type_hint=int),
            page: int = query_param(description="Page number", type_hint=int),
        ):
            return {"item_id": item_id, "page": page}
        
        # Не должно быть warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_on_startup(app)
            
            # Фильтруем только наши warnings
            validation_warnings = [warn for warn in w if "OpenAPI validation" in str(warn.message)]
            assert len(validation_warnings) == 0
    
    def test_validate_on_startup_missing_description(self):
        """Тест валидации при отсутствии description у параметра."""
        from fastapi import Query
        
        app = FastAPI()
        
        @app.get("/items")
        async def get_items(
            page: int = Query(),  # Нет description
        ):
            return {"page": page}
        
        # Должен быть warning о missing description
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_on_startup(app)
            
            validation_warnings = [warn for warn in w if "OpenAPI validation" in str(warn.message)]
            assert len(validation_warnings) > 0
            assert any("missing description" in str(warn.message).lower() for warn in validation_warnings)
    
    def test_validate_on_startup_missing_example(self):
        """Тест валидации при отсутствии example у параметра."""
        from fastapi import Query
        
        app = FastAPI()
        
        @app.get("/items")
        async def get_items(
            page: int = Query(description="Page number"),  # Нет example
        ):
            return {"page": page}
        
        # Должен быть warning о missing example
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_on_startup(app)
            
            validation_warnings = [warn for warn in w if "OpenAPI validation" in str(warn.message)]
            assert len(validation_warnings) > 0
            assert any("missing example" in str(warn.message).lower() for warn in validation_warnings)
    
    def test_validate_on_startup_does_not_raise_exception(self):
        """Тест, что validate_on_startup не выбрасывает исключения."""
        from fastapi import Query
        
        app = FastAPI()
        
        @app.get("/items")
        async def get_items(
            page: int = Query(),  # Нет description и example
        ):
            return {"page": page}
        
        # Не должно быть исключений, только warnings
        try:
            validate_on_startup(app)
        except Exception as e:
            pytest.fail(f"validate_on_startup raised {type(e).__name__}: {e}")
    
    def test_validate_on_startup_with_good_documentation(self):
        """Тест валидации с полной документацией."""
        from fastapi_openapi_plus import query_param, path_param
        
        app = FastAPI()
        
        @app.get("/items/{item_id}")
        async def get_item(
            item_id: int = path_param(description="Item ID", type_hint=int),
            page: int = query_param(description="Page number", type_hint=int),
        ):
            return {"item_id": item_id, "page": page}
        
        # Не должно быть warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_on_startup(app)
            
            validation_warnings = [warn for warn in w if "OpenAPI validation" in str(warn.message)]
            assert len(validation_warnings) == 0
    
    def test_validate_on_startup_request_body_missing_description(self):
        """Тест валидации request body без description."""
        from pydantic import BaseModel
        from fastapi import Body
        
        class ItemModel(BaseModel):
            name: str
        
        app = FastAPI()
        
        @app.post("/items")
        async def create_item(
            item: ItemModel = Body(),  # Нет description
        ):
            return {"item": item}
        
        # Должен быть warning о missing description
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_on_startup(app)
            
            validation_warnings = [warn for warn in w if "OpenAPI validation" in str(warn.message)]
            assert len(validation_warnings) > 0
            assert any("request body" in str(warn.message).lower() and "description" in str(warn.message).lower() 
                      for warn in validation_warnings)
    
    def test_validate_on_startup_multiple_issues(self):
        """Тест валидации с несколькими проблемами."""
        from fastapi import Query
        
        app = FastAPI()
        
        @app.get("/items")
        async def get_items(
            page: int = Query(),  # Нет description и example
            size: int = Query(),  # Нет description и example
        ):
            return {"page": page, "size": size}
        
        # Должно быть несколько warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_on_startup(app)
            
            validation_warnings = [warn for warn in w if "OpenAPI validation" in str(warn.message)]
            assert len(validation_warnings) >= 2  # Минимум 2 проблемы (по одной на параметр)
    
    def test_validate_on_startup_handles_invalid_schema_gracefully(self):
        """Тест, что validate_on_startup обрабатывает ошибки получения схемы."""
        # Создаем мок приложения, которое не может сгенерировать схему
        class MockApp:
            def openapi(self):
                raise Exception("Failed to generate schema")
        
        app = MockApp()
        
        # Не должно быть исключений, только warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_on_startup(app)
            
            # Должен быть warning о проблеме генерации схемы
            schema_warnings = [warn for warn in w if "Failed to generate OpenAPI schema" in str(warn.message)]
            assert len(schema_warnings) > 0
