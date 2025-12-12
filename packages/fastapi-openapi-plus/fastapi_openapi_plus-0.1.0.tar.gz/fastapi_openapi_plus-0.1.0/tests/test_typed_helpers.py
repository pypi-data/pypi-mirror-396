"""Тесты для typed_helpers.py.

Тесты для функций query_uuid(), path_uuid(), query_bool(), query_int(),
включая валидацию description, автогенерацию example и граничные случаи.
"""

import pytest
from fastapi import Path, Query
from uuid import UUID

try:
    from pydantic_core import PydanticUndefined
except ImportError:
    # Для старых версий Pydantic
    PydanticUndefined = type('PydanticUndefined', (), {})()

from fastapi_openapi_plus.typed_helpers import (
    path_uuid,
    query_bool,
    query_int,
    query_uuid,
)


def get_example_value(param):
    """Вспомогательная функция для получения example из param.
    
    Проверяет examples (новый формат) и example (старый формат, deprecated).
    """
    # Сначала проверяем examples (новый формат)
    if hasattr(param, 'examples') and param.examples:
        if isinstance(param.examples, list) and len(param.examples) > 0:
            first_example = param.examples[0]
            if isinstance(first_example, dict) and 'value' in first_example:
                return first_example['value']
            # Если examples - это просто список значений
            return first_example
    # Fallback на старый формат (deprecated)
    if hasattr(param, 'example'):
        example = param.example
        if example is not PydanticUndefined:
            return example
    return None


@pytest.mark.unit
class TestQueryUuid:
    """Тесты для функции query_uuid()."""
    
    def test_query_uuid_with_description(self):
        """Тест создания query UUID параметра с description."""
        param = query_uuid(description="Test UUID parameter")
        
        # Проверяем, что это Query объект (через имя класса)
        assert type(param).__name__ == "Query"
        assert param.description == "Test UUID parameter"
    
    def test_query_uuid_raises_on_empty_description(self):
        """Тест, что query_uuid выбрасывает ValueError для пустого description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            query_uuid(description="")
    
    def test_query_uuid_raises_on_whitespace_only_description(self):
        """Тест, что query_uuid выбрасывает ValueError для description только с пробелами."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            query_uuid(description="   ")
    
    def test_query_uuid_generates_valid_uuid_example(self):
        """Тест, что query_uuid генерирует валидный UUID example."""
        param = query_uuid(description="Test")
        
        # Проверяем, что example - это валидный UUID в формате строки
        example_value = get_example_value(param)
        assert isinstance(example_value, str)
        # Проверяем, что это валидный UUID
        UUID(example_value)  # Не должно выбрасывать исключение
    
    def test_query_uuid_generates_different_examples(self):
        """Тест, что query_uuid генерирует разные UUID для разных вызовов."""
        param1 = query_uuid(description="Test 1")
        param2 = query_uuid(description="Test 2")
        
        # UUID должны быть разными
        assert get_example_value(param1) != get_example_value(param2)
    
    def test_query_uuid_with_alias(self):
        """Тест query_uuid с alias."""
        param = query_uuid(description="Test", alias="testId")
        
        assert param.alias == "testId"
    
    def test_query_uuid_with_default(self):
        """Тест query_uuid с default значением."""
        default_uuid = str(UUID('12345678-1234-5678-1234-567812345678'))
        param = query_uuid(description="Test", default=default_uuid)
        
        assert param.default == default_uuid
        # example все равно генерируется автоматически
        assert isinstance(get_example_value(param), str)
    
    def test_query_uuid_passes_kwargs_to_query(self):
        """Тест, что все kwargs передаются в Query."""
        param = query_uuid(description="Test", min_length=36, max_length=36)
        
        # min_length и max_length не являются прямыми атрибутами Query
        # Проверяем, что объект создан без ошибок
        assert param.description == "Test"


@pytest.mark.unit
class TestPathUuid:
    """Тесты для функции path_uuid()."""
    
    def test_path_uuid_with_description(self):
        """Тест создания path UUID параметра с description."""
        param = path_uuid(description="Test UUID parameter")
        
        # Проверяем, что это Path объект (через имя класса)
        assert type(param).__name__ == "Path"
        assert param.description == "Test UUID parameter"
    
    def test_path_uuid_raises_on_empty_description(self):
        """Тест, что path_uuid выбрасывает ValueError для пустого description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            path_uuid(description="")
    
    def test_path_uuid_raises_on_whitespace_only_description(self):
        """Тест, что path_uuid выбрасывает ValueError для description только с пробелами."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            path_uuid(description="   ")
    
    def test_path_uuid_does_not_accept_alias(self):
        """Тест, что path_uuid не принимает параметр alias."""
        with pytest.raises(ValueError, match="path_uuid\\(\\) does not accept 'alias' parameter"):
            path_uuid(description="Test", alias="testId")
    
    def test_path_uuid_generates_valid_uuid_example(self):
        """Тест, что path_uuid генерирует валидный UUID example."""
        param = path_uuid(description="Test")
        
        # Проверяем, что example - это валидный UUID в формате строки
        assert isinstance(get_example_value(param), str)
        # Проверяем, что это валидный UUID
        UUID(get_example_value(param))  # Не должно выбрасывать исключение
    
    def test_path_uuid_generates_different_examples(self):
        """Тест, что path_uuid генерирует разные UUID для разных вызовов."""
        param1 = path_uuid(description="Test 1")
        param2 = path_uuid(description="Test 2")
        
        # UUID должны быть разными
        assert get_example_value(param1) != get_example_value(param2)
    
    def test_path_uuid_passes_kwargs_to_path(self):
        """Тест, что все kwargs передаются в Path."""
        param = path_uuid(description="Test", min_length=36, max_length=36)
        
        # min_length и max_length не являются прямыми атрибутами Path
        # Проверяем, что объект создан без ошибок
        assert param.description == "Test"


@pytest.mark.unit
class TestQueryBool:
    """Тесты для функции query_bool()."""
    
    def test_query_bool_with_description(self):
        """Тест создания query bool параметра с description."""
        param = query_bool(description="Test boolean parameter")
        
        # Проверяем, что это Query объект (через имя класса)
        assert type(param).__name__ == "Query"
        assert param.description == "Test boolean parameter"
    
    def test_query_bool_raises_on_empty_description(self):
        """Тест, что query_bool выбрасывает ValueError для пустого description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            query_bool(description="")
    
    def test_query_bool_raises_on_whitespace_only_description(self):
        """Тест, что query_bool выбрасывает ValueError для description только с пробелами."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            query_bool(description="   ")
    
    def test_query_bool_uses_default_as_example(self):
        """Тест, что query_bool использует default как example."""
        param = query_bool(description="Test", default=False)
        
        assert get_example_value(param) is False
        assert param.default is False
    
    def test_query_bool_with_default_true(self):
        """Тест query_bool с default=True."""
        param = query_bool(description="Test", default=True)
        
        assert get_example_value(param) is True
        assert param.default is True
    
    def test_query_bool_default_false_by_default(self):
        """Тест, что query_bool использует False по умолчанию."""
        param = query_bool(description="Test")
        
        assert get_example_value(param) is False
        assert param.default is False
    
    def test_query_bool_with_alias(self):
        """Тест query_bool с alias."""
        param = query_bool(description="Test", alias="includeStats")
        
        assert param.alias == "includeStats"
    
    def test_query_bool_passes_kwargs_to_query(self):
        """Тест, что все kwargs передаются в Query."""
        param = query_bool(description="Test", deprecated=True)
        
        assert param.deprecated is True


@pytest.mark.unit
class TestQueryInt:
    """Тесты для функции query_int()."""
    
    def test_query_int_with_description(self):
        """Тест создания query int параметра с description."""
        param = query_int(description="Test integer parameter")
        
        # Проверяем, что это Query объект (через имя класса)
        assert type(param).__name__ == "Query"
        assert param.description == "Test integer parameter"
    
    def test_query_int_raises_on_empty_description(self):
        """Тест, что query_int выбрасывает ValueError для пустого description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            query_int(description="")
    
    def test_query_int_raises_on_whitespace_only_description(self):
        """Тест, что query_int выбрасывает ValueError для description только с пробелами."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            query_int(description="   ")
    
    def test_query_int_default_example(self):
        """Тест query_int с default значением (example = default)."""
        param = query_int(description="Test", default=42)
        
        assert get_example_value(param) == 42
        assert param.default == 42
    
    def test_query_int_with_ge_constraint(self):
        """Тест query_int с ограничением ge."""
        param = query_int(description="Test", ge=10)
        
        # example должен быть >= ge
        assert get_example_value(param) >= 10
        # ge не является прямым атрибутом Query, но передается в constraints
    
    def test_query_int_with_le_constraint(self):
        """Тест query_int с ограничением le."""
        param = query_int(description="Test", le=100)
        
        # example должен быть <= le
        assert get_example_value(param) <= 100
        # le не является прямым атрибутом Query, но передается в constraints
    
    def test_query_int_with_ge_and_le_constraints(self):
        """Тест query_int с ограничениями ge и le."""
        param = query_int(description="Test", ge=10, le=100)
        
        # example должен быть в диапазоне [ge, le]
        assert get_example_value(param) >= 10
        assert get_example_value(param) <= 100
        # ge и le не являются прямыми атрибутами Query, но передаются в constraints
    
    def test_query_int_with_default_in_range(self):
        """Тест query_int с default в диапазоне ограничений."""
        param = query_int(description="Test", default=50, ge=10, le=100)
        
        # Если default в диапазоне, используется default
        assert get_example_value(param) == 50
        assert param.default == 50
    
    def test_query_int_with_default_outside_range(self):
        """Тест query_int с default вне диапазона ограничений."""
        param = query_int(description="Test", default=5, ge=10, le=100)
        
        # Если default вне диапазона, используется середина диапазона
        assert get_example_value(param) >= 10
        assert get_example_value(param) <= 100
        assert param.default == 5  # default остается исходным
    
    def test_query_int_raises_on_invalid_constraints(self):
        """Тест, что query_int выбрасывает ValueError при ge > le."""
        with pytest.raises(ValueError, match="Invalid constraints: ge \\(100\\) > le \\(10\\)"):
            query_int(description="Test", ge=100, le=10)
    
    def test_query_int_with_ge_and_default_below_ge(self):
        """Тест query_int с ge и default < ge."""
        param = query_int(description="Test", default=5, ge=10)
        
        # example должен быть >= ge
        assert get_example_value(param) >= 10
        assert param.default == 5
    
    def test_query_int_with_le_and_default_above_le(self):
        """Тест query_int с le и default > le."""
        param = query_int(description="Test", default=200, le=100)
        
        # example должен быть <= le
        assert get_example_value(param) <= 100
        assert param.default == 200
    
    def test_query_int_with_equal_ge_and_le(self):
        """Тест query_int с ge == le (фиксированное значение)."""
        param = query_int(description="Test", ge=50, le=50)
        
        # example должен быть равен ge и le
        assert get_example_value(param) == 50
        # ge и le не являются прямыми атрибутами Query, но передаются в constraints
    
    def test_query_int_with_negative_values(self):
        """Тест query_int с отрицательными значениями."""
        param = query_int(description="Test", ge=-100, le=-10)
        
        # example должен быть в диапазоне [-100, -10]
        assert get_example_value(param) >= -100
        assert get_example_value(param) <= -10
    
    def test_query_int_with_alias(self):
        """Тест query_int с alias."""
        param = query_int(description="Test", alias="page")
        
        assert param.alias == "page"
    
    def test_query_int_passes_kwargs_to_query(self):
        """Тест, что все kwargs передаются в Query."""
        param = query_int(description="Test", multiple_of=5)
        
        # multiple_of не является прямым атрибутом Query
        # Проверяем, что объект создан без ошибок
        assert param.description == "Test"


@pytest.mark.unit
class TestTypedHelpersIntegration:
    """Интеграционные тесты для всех typed helpers."""
    
    def test_all_helpers_validate_description(self):
        """Тест, что все helpers валидируют description."""
        with pytest.raises(ValueError):
            query_uuid(description="")
        
        with pytest.raises(ValueError):
            path_uuid(description="")
        
        with pytest.raises(ValueError):
            query_bool(description="")
        
        with pytest.raises(ValueError):
            query_int(description="")
    
    def test_uuid_helpers_generate_valid_examples(self):
        """Тест, что UUID helpers генерируют валидные примеры."""
        query = query_uuid(description="Test")
        path = path_uuid(description="Test")
        
        # Оба должны генерировать валидные UUID
        UUID(get_example_value(query))
        UUID(get_example_value(path))
    
    def test_bool_helper_uses_default(self):
        """Тест, что bool helper использует default как example."""
        param = query_bool(description="Test", default=True)
        
        assert get_example_value(param) is True
        assert param.default is True
