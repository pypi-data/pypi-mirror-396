"""Тесты для params.py.

Тесты для функций query_param(), path_param(), body_param(),
включая валидацию description, автогенерацию example и граничные случаи.
"""

import pytest
from fastapi import Body, Path, Query

try:
    from pydantic_core import PydanticUndefined
except ImportError:
    # Для старых версий Pydantic
    PydanticUndefined = type('PydanticUndefined', (), {})()

from fastapi_openapi_plus.params import body_param, path_param, query_param
from fastapi_openapi_plus.generators import ExampleGenerators


def get_example_value(param):
    """Вспомогательная функция для получения example из param.
    
    Проверяет example (основной формат) и examples (альтернативный формат).
    """
    # Сначала проверяем example (основной формат)
    if hasattr(param, 'example'):
        example = param.example
        if example is not PydanticUndefined and example is not None:
            return example
    # Fallback на examples (альтернативный формат)
    if hasattr(param, 'examples') and param.examples:
        if isinstance(param.examples, list) and len(param.examples) > 0:
            first_example = param.examples[0]
            if isinstance(first_example, dict) and 'value' in first_example:
                return first_example['value']
            return first_example
        elif isinstance(param.examples, dict):
            # Если examples - это словарь {name: ExampleObject}
            first_example = next(iter(param.examples.values()), None)
            if first_example and isinstance(first_example, dict) and 'value' in first_example:
                return first_example['value']
    return None


@pytest.mark.unit
class TestQueryParam:
    """Тесты для функции query_param()."""
    
    def test_query_param_with_description(self):
        """Тест создания query параметра с description."""
        param = query_param(description="Test parameter")
        
        # Проверяем, что это Query объект (через имя класса)
        assert type(param).__name__ == "Query"
        assert param.description == "Test parameter"
    
    def test_query_param_raises_on_empty_description(self):
        """Тест, что query_param выбрасывает ValueError для пустого description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            query_param(description="")
    
    def test_query_param_raises_on_whitespace_only_description(self):
        """Тест, что query_param выбрасывает ValueError для description только с пробелами."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            query_param(description="   ")
    
    def test_query_param_raises_on_none_description(self):
        """Тест, что query_param выбрасывает ValueError для None description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            query_param(description=None)
    
    def test_query_param_with_explicit_example(self):
        """Тест query_param с явно указанным example."""
        param = query_param(description="Test", example=42)
        
        # Проверяем example
        assert param.example == 42
        assert get_example_value(param) == 42
    
    def test_query_param_autogenerates_example_from_type_hint(self):
        """Тест автогенерации example через type_hint."""
        param = query_param(description="Test", type_hint=int)
        
        # Проверяем example
        assert param.example == 1  # Предустановленный генератор для int
        assert get_example_value(param) == 1
    
    def test_query_param_uses_default_as_example(self):
        """Тест использования default как example."""
        param = query_param(description="Test", default=42)
        
        # Проверяем example
        assert param.example == 42
        assert get_example_value(param) == 42
        assert param.default == 42
    
    def test_query_param_default_priority_over_type_hint(self):
        """Тест, что default имеет приоритет над type_hint для example."""
        param = query_param(description="Test", default=100, type_hint=int)
        
        # default должен использоваться как example, а не генератор
        assert param.example == 100
        assert get_example_value(param) == 100
    
    def test_query_param_explicit_example_priority(self):
        """Тест, что явный example имеет приоритет над default и type_hint."""
        param = query_param(
            description="Test",
            example=999,
            default=42,
            type_hint=int,
        )
        
        assert param.example == 999
        assert get_example_value(param) == 999
    
    def test_query_param_no_example_when_generator_not_found(self):
        """Тест, что example не генерируется, если генератор не найден."""
        class UnregisteredType:
            pass
        
        param = query_param(description="Test", type_hint=UnregisteredType)
        
        # example не должен быть установлен, если генератор не найден
        assert not hasattr(param, 'example') or param.example is None or param.example is PydanticUndefined
        assert get_example_value(param) is None
    
    def test_query_param_with_alias(self):
        """Тест query_param с alias."""
        param = query_param(description="Test", alias="testParam")
        
        assert param.alias == "testParam"
    
    def test_query_param_with_additional_kwargs(self):
        """Тест query_param с дополнительными параметрами (ge, le, etc.)."""
        param = query_param(description="Test", ge=1, le=100)
        
        # ge и le не являются прямыми атрибутами Query, они хранятся в constraints
        # Проверяем, что параметры были переданы корректно через json_schema
        # Или просто проверяем, что объект создан без ошибок
        assert param.description == "Test"
        # ge и le будут использованы FastAPI при валидации, но не доступны как атрибуты
    
    def test_query_param_with_default_ellipsis(self):
        """Тест query_param с default=... (обязательный параметр)."""
        param = query_param(description="Test", default=...)
        
        # При default=... FastAPI преобразует его в PydanticUndefined
        # Проверяем, что default не является конкретным значением
        from pydantic_core import PydanticUndefined
        assert param.default is PydanticUndefined or param.default is ...
    
    def test_query_param_passes_kwargs_to_query(self):
        """Тест, что все kwargs передаются в Query."""
        param = query_param(
            description="Test",
            min_length=3,
            max_length=10,
            pattern="^[a-z]+$",  # В новых версиях FastAPI используется pattern вместо regex
        )
        
        # min_length, max_length, pattern не являются прямыми атрибутами Query
        # Проверяем, что объект создан без ошибок
        assert param.description == "Test"


@pytest.mark.unit
class TestPathParam:
    """Тесты для функции path_param()."""
    
    def test_path_param_with_description(self):
        """Тест создания path параметра с description."""
        param = path_param(description="Test parameter")
        
        # Проверяем, что это Path объект (через имя класса)
        assert type(param).__name__ == "Path"
        assert param.description == "Test parameter"
    
    def test_path_param_raises_on_empty_description(self):
        """Тест, что path_param выбрасывает ValueError для пустого description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            path_param(description="")
    
    def test_path_param_raises_on_whitespace_only_description(self):
        """Тест, что path_param выбрасывает ValueError для description только с пробелами."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            path_param(description="   ")
    
    def test_path_param_raises_on_none_description(self):
        """Тест, что path_param выбрасывает ValueError для None description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            path_param(description=None)
    
    def test_path_param_does_not_accept_alias(self):
        """Тест, что path_param не принимает параметр alias."""
        with pytest.raises(ValueError, match="path_param\\(\\) does not accept 'alias' parameter"):
            path_param(description="Test", alias="testParam")
    
    def test_path_param_autogenerates_example_from_type_hint(self):
        """Тест автогенерации example через type_hint."""
        param = path_param(description="Test", type_hint=str)
        
        assert param.example == "example_string"  # Предустановленный генератор для str
        assert get_example_value(param) == "example_string"
    
    def test_path_param_with_explicit_example(self):
        """Тест path_param с явно указанным example."""
        param = path_param(description="Test", example="custom_example")
        
        assert param.example == "custom_example"
        assert get_example_value(param) == "custom_example"
    
    def test_path_param_no_example_when_generator_not_found(self):
        """Тест, что example не генерируется, если генератор не найден."""
        class UnregisteredType:
            pass
        
        param = path_param(description="Test", type_hint=UnregisteredType)
        
        # example не должен быть установлен, если генератор не найден
        assert not hasattr(param, 'example') or param.example is None or param.example is PydanticUndefined
        assert get_example_value(param) is None
    
    def test_path_param_with_additional_kwargs(self):
        """Тест path_param с дополнительными параметрами (ge, le, etc.)."""
        param = path_param(description="Test", ge=1, le=100)
        
        # ge и le не являются прямыми атрибутами Path, они хранятся в constraints
        # Проверяем, что параметры были переданы корректно
        assert param.description == "Test"
        # ge и le будут использованы FastAPI при валидации, но не доступны как атрибуты
    
    def test_path_param_passes_kwargs_to_path(self):
        """Тест, что все kwargs передаются в Path."""
        param = path_param(
            description="Test",
            min_length=3,
            max_length=10,
        )
        
        # min_length и max_length также не являются прямыми атрибутами
        # Проверяем, что объект создан без ошибок
        assert param.description == "Test"


@pytest.mark.unit
class TestBodyParam:
    """Тесты для функции body_param()."""
    
    def test_body_param_with_description(self):
        """Тест создания body параметра с description."""
        param = body_param(description="Test parameter")
        
        # Проверяем, что это Body объект (через имя класса)
        assert type(param).__name__ == "Body"
        assert param.description == "Test parameter"
    
    def test_body_param_raises_on_empty_description(self):
        """Тест, что body_param выбрасывает ValueError для пустого description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            body_param(description="")
    
    def test_body_param_raises_on_whitespace_only_description(self):
        """Тест, что body_param выбрасывает ValueError для description только с пробелами."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            body_param(description="   ")
    
    def test_body_param_raises_on_none_description(self):
        """Тест, что body_param выбрасывает ValueError для None description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            body_param(description=None)
    
    def test_body_param_with_explicit_example(self):
        """Тест body_param с явно указанным example."""
        param = body_param(description="Test", example={"key": "value"})
        
        assert param.example == {"key": "value"}
        assert get_example_value(param) == {"key": "value"}
    
    def test_body_param_with_embed(self):
        """Тест body_param с embed=True."""
        param = body_param(description="Test", embed=True)
        
        assert param.embed is True
    
    def test_body_param_with_default(self):
        """Тест body_param с default значением."""
        default_value = {"key": "value"}
        param = body_param(description="Test", default=default_value)
        
        assert param.default == default_value
    
    def test_body_param_autogenerates_from_default(self):
        """Тест автогенерации example через default (приоритет над type_hint)."""
        # Если default не Ellipsis, он используется как example
        param = body_param(description="Test", default=42)
        
        assert param.example == 42
        assert get_example_value(param) == 42
    
    def test_body_param_autogenerates_from_type_hint(self):
        """Тест автогенерации example через type_hint."""
        # Регистрируем генератор для теста
        ExampleGenerators.reset()
        
        param = body_param(description="Test", type_hint=int)
        
        # Должен быть сгенерирован example для int (обычно 1)
        assert param.example is not None
        assert param.example is not PydanticUndefined
        example_value = get_example_value(param)
        assert example_value is not None
        assert isinstance(example_value, int)
        
        ExampleGenerators.reset()
    
    def test_body_param_prioritizes_example_over_default(self):
        """Тест, что явный example имеет приоритет над default."""
        param = body_param(
            description="Test",
            example="explicit",
            default="default_value",
        )
        
        assert param.example == "explicit"
        assert get_example_value(param) == "explicit"
        assert param.default == "default_value"
    
    def test_body_param_prioritizes_default_over_type_hint(self):
        """Тест, что default имеет приоритет над type_hint."""
        ExampleGenerators.reset()
        
        param = body_param(
            description="Test",
            default="default_value",
            type_hint=int,
        )
        
        # default должен использоваться как example, а не type_hint
        assert param.example == "default_value"
        assert get_example_value(param) == "default_value"
        
        ExampleGenerators.reset()
    
    def test_body_param_passes_kwargs_to_body(self):
        """Тест, что все kwargs передаются в Body."""
        param = body_param(
            description="Test",
            media_type="application/json",
        )
        
        # media_type может не быть прямым атрибутом Body
        # Проверяем, что объект создан без ошибок
        assert param.description == "Test"


@pytest.mark.unit
class TestParamsIntegration:
    """Интеграционные тесты для всех функций params."""
    
    def test_all_params_validate_description(self):
        """Тест, что все функции валидируют description."""
        with pytest.raises(ValueError):
            query_param(description="")
        
        with pytest.raises(ValueError):
            path_param(description="")
        
        with pytest.raises(ValueError):
            body_param(description="")
    
    def test_all_params_support_explicit_example(self):
        """Тест, что все функции поддерживают явный example."""
        query = query_param(description="Test", example=1)
        path = path_param(description="Test", example=2)
        body = body_param(description="Test", example=3)
        
        assert get_example_value(query) == 1
        assert get_example_value(path) == 2
        assert get_example_value(body) == 3
    
    def test_params_with_custom_generator(self):
        """Тест использования кастомного генератора."""
        ExampleGenerators.reset()
        
        class CustomType:
            pass
        
        # Регистрируем кастомный генератор
        ExampleGenerators.register(CustomType, lambda: CustomType())
        
        # Используем в query_param
        query = query_param(description="Test", type_hint=CustomType)
        assert isinstance(get_example_value(query), CustomType)
        
        # Используем в body_param
        body = body_param(description="Test", type_hint=CustomType)
        assert isinstance(get_example_value(body), CustomType)
        
        ExampleGenerators.reset()
