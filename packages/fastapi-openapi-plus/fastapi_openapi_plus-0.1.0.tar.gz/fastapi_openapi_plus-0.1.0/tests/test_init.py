"""Тесты для __init__.py.

Тесты проверяют корректность экспортов публичного API библиотеки.
"""

import pytest

import fastapi_openapi_plus


@pytest.mark.unit
class TestPublicAPI:
    """Тесты публичного API библиотеки."""
    
    def test_version_is_defined(self):
        """Тест, что __version__ определен."""
        assert hasattr(fastapi_openapi_plus, "__version__")
        assert fastapi_openapi_plus.__version__ == "0.1.0"
    
    def test_all_is_defined(self):
        """Тест, что __all__ определен."""
        assert hasattr(fastapi_openapi_plus, "__all__")
        assert isinstance(fastapi_openapi_plus.__all__, list)
        assert len(fastapi_openapi_plus.__all__) > 0
    
    def test_all_contains_expected_exports(self):
        """Тест, что __all__ содержит ожидаемые экспорты."""
        expected_exports = [
            "query_param",
            "path_param",
            "body_param",
            "query_uuid",
            "path_uuid",
            "query_bool",
            "query_int",
            "ExampleGenerators",
            "__version__",
        ]
        
        for export in expected_exports:
            assert export in fastapi_openapi_plus.__all__, f"{export} должен быть в __all__"
    
    def test_query_param_importable(self):
        """Тест, что query_param импортируется."""
        from fastapi_openapi_plus import query_param
        
        assert callable(query_param)
    
    def test_path_param_importable(self):
        """Тест, что path_param импортируется."""
        from fastapi_openapi_plus import path_param
        
        assert callable(path_param)
    
    def test_body_param_importable(self):
        """Тест, что body_param импортируется."""
        from fastapi_openapi_plus import body_param
        
        assert callable(body_param)
    
    def test_query_uuid_importable(self):
        """Тест, что query_uuid импортируется."""
        from fastapi_openapi_plus import query_uuid
        
        assert callable(query_uuid)
    
    def test_path_uuid_importable(self):
        """Тест, что path_uuid импортируется."""
        from fastapi_openapi_plus import path_uuid
        
        assert callable(path_uuid)
    
    def test_query_bool_importable(self):
        """Тест, что query_bool импортируется."""
        from fastapi_openapi_plus import query_bool
        
        assert callable(query_bool)
    
    def test_query_int_importable(self):
        """Тест, что query_int импортируется."""
        from fastapi_openapi_plus import query_int
        
        assert callable(query_int)
    
    def test_example_generators_importable(self):
        """Тест, что ExampleGenerators импортируется."""
        from fastapi_openapi_plus import ExampleGenerators
        
        assert ExampleGenerators is not None
        assert hasattr(ExampleGenerators, "register")
        assert hasattr(ExampleGenerators, "generate_for_type")
        assert hasattr(ExampleGenerators, "reset")
    
    def test_version_importable(self):
        """Тест, что __version__ импортируется."""
        from fastapi_openapi_plus import __version__
        
        assert __version__ == "0.1.0"
    
    def test_all_exports_are_available(self):
        """Тест, что все экспорты из __all__ доступны."""
        for export_name in fastapi_openapi_plus.__all__:
            assert hasattr(fastapi_openapi_plus, export_name), (
                f"{export_name} должен быть доступен в модуле"
            )
    
    def test_import_from_package(self):
        """Тест импорта всех функций из пакета."""
        from fastapi_openapi_plus import (
            ExampleGenerators,
            __version__,
            body_param,
            path_param,
            path_uuid,
            query_bool,
            query_int,
            query_param,
            query_uuid,
        )
        
        # Проверяем, что все импортированы
        assert query_param is not None
        assert path_param is not None
        assert body_param is not None
        assert query_uuid is not None
        assert path_uuid is not None
        assert query_bool is not None
        assert query_int is not None
        assert ExampleGenerators is not None
        assert __version__ == "0.1.0"


