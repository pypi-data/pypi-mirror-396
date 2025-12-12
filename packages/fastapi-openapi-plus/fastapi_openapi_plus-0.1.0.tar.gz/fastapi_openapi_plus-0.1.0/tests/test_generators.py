"""Тесты для generators.py.

Тесты для класса ExampleGenerators, включая регистрацию генераторов,
генерацию примеров, нормализацию типов и управление реестром.
"""

import pytest
from datetime import datetime
from typing import Annotated, Optional, Union
from uuid import UUID

from fastapi_openapi_plus.generators import ExampleGenerators


@pytest.mark.unit
class TestExampleGeneratorsRegister:
    """Тесты для метода register()."""
    
    def test_register_custom_generator(self):
        """Тест регистрации кастомного генератора."""
        ExampleGenerators.reset()  # Изоляция теста
        
        class MyType:
            pass
        
        ExampleGenerators.register(MyType, lambda: MyType())
        
        result = ExampleGenerators.generate_for_type(MyType)
        assert isinstance(result, MyType)
        
        ExampleGenerators.reset()  # Очистка
    
    def test_register_overwrites_existing(self):
        """Тест перезаписи существующего генератора."""
        ExampleGenerators.reset()
        
        # Регистрируем первый генератор
        ExampleGenerators.register(str, lambda: "first")
        assert ExampleGenerators.generate_for_type(str) == "first"
        
        # Перезаписываем генератор
        ExampleGenerators.register(str, lambda: "second")
        assert ExampleGenerators.generate_for_type(str) == "second"
        
        ExampleGenerators.reset()
    
    def test_register_raises_typeerror_for_non_type(self):
        """Тест, что register() выбрасывает TypeError для не-типа."""
        ExampleGenerators.reset()
        
        with pytest.raises(TypeError, match="type_hint must be a type"):
            ExampleGenerators.register("not_a_type", lambda: None)
        
        ExampleGenerators.reset()
    
    def test_register_raises_typeerror_for_non_callable(self):
        """Тест, что register() выбрасывает TypeError для не-callable."""
        ExampleGenerators.reset()
        
        with pytest.raises(TypeError, match="generator must be callable"):
            ExampleGenerators.register(str, "not_callable")
        
        ExampleGenerators.reset()


@pytest.mark.unit
class TestExampleGeneratorsGenerateForType:
    """Тесты для метода generate_for_type()."""
    
    def test_generate_for_predefined_str(self):
        """Тест генерации для предустановленного типа str."""
        result = ExampleGenerators.generate_for_type(str)
        assert result == "example_string"
    
    def test_generate_for_predefined_int(self):
        """Тест генерации для предустановленного типа int."""
        result = ExampleGenerators.generate_for_type(int)
        assert result == 1
    
    def test_generate_for_predefined_bool(self):
        """Тест генерации для предустановленного типа bool."""
        result = ExampleGenerators.generate_for_type(bool)
        assert result is False
    
    def test_generate_for_predefined_float(self):
        """Тест генерации для предустановленного типа float."""
        result = ExampleGenerators.generate_for_type(float)
        assert result == 1.0
    
    def test_generate_for_predefined_uuid(self):
        """Тест генерации для предустановленного типа UUID."""
        result = ExampleGenerators.generate_for_type(UUID)
        assert isinstance(result, str)
        # Проверяем, что это валидный UUID формат
        UUID(result)  # Не должно выбрасывать исключение
    
    def test_generate_for_predefined_datetime(self):
        """Тест генерации для предустановленного типа datetime."""
        result = ExampleGenerators.generate_for_type(datetime)
        assert isinstance(result, str)
        # Проверяем, что это валидный ISO формат
        datetime.fromisoformat(result)  # Не должно выбрасывать исключение
    
    def test_generate_for_unregistered_type_returns_none(self):
        """Тест, что для незарегистрированного типа возвращается None."""
        class UnregisteredType:
            pass
        
        result = ExampleGenerators.generate_for_type(UnregisteredType)
        assert result is None
    
    def test_generate_for_none_type_returns_none(self):
        """Тест генерации для None типа."""
        result = ExampleGenerators.generate_for_type(type(None))
        assert result is None


@pytest.mark.unit
class TestExampleGeneratorsNormalizeType:
    """Тесты для метода _normalize_type()."""
    
    def test_normalize_optional_str(self):
        """Тест нормализации Optional[str] → str."""
        normalized = ExampleGenerators._normalize_type(Optional[str])
        assert normalized == str
    
    def test_normalize_union_int_none(self):
        """Тест нормализации Union[int, None] → int."""
        normalized = ExampleGenerators._normalize_type(Union[int, None])
        assert normalized == int
    
    def test_normalize_annotated_str(self):
        """Тест нормализации Annotated[str, ...] → str."""
        normalized = ExampleGenerators._normalize_type(Annotated[str, "description"])
        assert normalized == str
    
    def test_normalize_annotated_with_multiple_metadata(self):
        """Тест нормализации Annotated с несколькими метаданными."""
        normalized = ExampleGenerators._normalize_type(
            Annotated[str, "desc1", "desc2"]
        )
        assert normalized == str
    
    def test_normalize_nested_optional(self):
        """Тест нормализации вложенного Optional."""
        # Optional[Optional[str]] → Optional[str] → str
        normalized = ExampleGenerators._normalize_type(Optional[Optional[str]])
        assert normalized == str
    
    def test_normalize_annotated_optional(self):
        """Тест нормализации Annotated[Optional[str], ...] → str."""
        normalized = ExampleGenerators._normalize_type(
            Annotated[Optional[str], "description"]
        )
        assert normalized == str
    
    def test_normalize_regular_type_unchanged(self):
        """Тест, что обычный тип не изменяется при нормализации."""
        normalized = ExampleGenerators._normalize_type(str)
        assert normalized == str
    
    def test_normalize_union_multiple_types(self):
        """Тест нормализации Union с несколькими типами (берется первый)."""
        normalized = ExampleGenerators._normalize_type(Union[int, str, None])
        assert normalized == int  # Берется первый не-None тип


@pytest.mark.unit
class TestExampleGeneratorsNormalizedGeneration:
    """Тесты генерации с нормализацией типов."""
    
    def test_generate_for_optional_str(self):
        """Тест генерации для Optional[str] (должен вернуть пример для str)."""
        result = ExampleGenerators.generate_for_type(Optional[str])
        assert result == "example_string"
    
    def test_generate_for_union_int_none(self):
        """Тест генерации для Union[int, None] (должен вернуть пример для int)."""
        result = ExampleGenerators.generate_for_type(Union[int, None])
        assert result == 1
    
    def test_generate_for_annotated_str(self):
        """Тест генерации для Annotated[str, ...] (должен вернуть пример для str)."""
        result = ExampleGenerators.generate_for_type(Annotated[str, "description"])
        assert result == "example_string"
    
    def test_generate_for_annotated_optional_str(self):
        """Тест генерации для Annotated[Optional[str], ...]."""
        result = ExampleGenerators.generate_for_type(
            Annotated[Optional[str], "description"]
        )
        assert result == "example_string"


@pytest.mark.unit
class TestExampleGeneratorsGenerateForDefault:
    """Тесты для метода generate_for_default()."""
    
    def test_generate_for_default_with_value(self):
        """Тест генерации для default значения (возвращает default)."""
        result = ExampleGenerators.generate_for_default(42)
        assert result == 42
    
    def test_generate_for_default_with_ellipsis_and_type_hint(self):
        """Тест генерации для Ellipsis с type_hint."""
        result = ExampleGenerators.generate_for_default(..., type_hint=str)
        assert result == "example_string"
    
    def test_generate_for_default_with_ellipsis_no_type_hint(self):
        """Тест генерации для Ellipsis без type_hint (возвращает None)."""
        result = ExampleGenerators.generate_for_default(...)
        assert result is None
    
    def test_generate_for_default_with_none(self):
        """Тест генерации для None как default."""
        result = ExampleGenerators.generate_for_default(None)
        assert result is None


@pytest.mark.unit
class TestExampleGeneratorsReset:
    """Тесты для метода reset()."""
    
    def test_reset_restores_default_generators(self):
        """Тест, что reset() восстанавливает предустановленные генераторы."""
        ExampleGenerators.reset()
        
        # Регистрируем кастомный генератор
        ExampleGenerators.register(str, lambda: "custom")
        assert ExampleGenerators.generate_for_type(str) == "custom"
        
        # Сбрасываем
        ExampleGenerators.reset()
        
        # Должен вернуться к предустановленному
        assert ExampleGenerators.generate_for_type(str) == "example_string"
    
    def test_reset_removes_custom_generators(self):
        """Тест, что reset() удаляет пользовательские генераторы."""
        ExampleGenerators.reset()
        
        class CustomType:
            pass
        
        # Регистрируем кастомный генератор
        ExampleGenerators.register(CustomType, lambda: CustomType())
        assert ExampleGenerators.generate_for_type(CustomType) is not None
        
        # Сбрасываем
        ExampleGenerators.reset()
        
        # Кастомный генератор должен быть удален
        assert ExampleGenerators.generate_for_type(CustomType) is None
    
    def test_reset_preserves_predefined_generators(self):
        """Тест, что reset() сохраняет все предустановленные генераторы."""
        ExampleGenerators.reset()
        
        # Проверяем все предустановленные генераторы
        assert ExampleGenerators.generate_for_type(str) == "example_string"
        assert ExampleGenerators.generate_for_type(int) == 1
        assert ExampleGenerators.generate_for_type(bool) is False
        assert ExampleGenerators.generate_for_type(float) == 1.0
        assert ExampleGenerators.generate_for_type(UUID) is not None
        assert ExampleGenerators.generate_for_type(datetime) is not None


@pytest.mark.unit
class TestExampleGeneratorsUnregister:
    """Тесты для метода unregister()."""
    
    def test_unregister_removes_generator(self):
        """Тест, что unregister() удаляет генератор."""
        ExampleGenerators.reset()
        
        # Регистрируем кастомный генератор
        ExampleGenerators.register(str, lambda: "custom")
        assert ExampleGenerators.generate_for_type(str) == "custom"
        
        # Удаляем генератор
        ExampleGenerators.unregister(str)
        
        # Генератор должен быть удален
        assert ExampleGenerators.generate_for_type(str) is None
        
        ExampleGenerators.reset()
    
    def test_unregister_does_not_affect_other_generators(self):
        """Тест, что unregister() не влияет на другие генераторы."""
        ExampleGenerators.reset()
        
        # Регистрируем два генератора
        class Type1:
            pass
        
        class Type2:
            pass
        
        ExampleGenerators.register(Type1, lambda: Type1())
        ExampleGenerators.register(Type2, lambda: Type2())
        
        # Удаляем только Type1
        ExampleGenerators.unregister(Type1)
        
        # Type1 должен быть удален
        assert ExampleGenerators.generate_for_type(Type1) is None
        
        # Type2 должен остаться
        assert ExampleGenerators.generate_for_type(Type2) is not None
        
        ExampleGenerators.reset()
    
    def test_unregister_nonexistent_type_no_error(self):
        """Тест, что unregister() не выбрасывает ошибку для несуществующего типа."""
        ExampleGenerators.reset()
        
        class NonExistentType:
            pass
        
        # Не должно выбрасывать исключение
        ExampleGenerators.unregister(NonExistentType)
        
        ExampleGenerators.reset()


@pytest.mark.unit
class TestExampleGeneratorsIsolation:
    """Тесты изоляции тестов (shared state)."""
    
    def test_test_isolation_with_reset(self):
        """Тест изоляции тестов через reset()."""
        ExampleGenerators.reset()
        
        class TestType:
            pass
        
        ExampleGenerators.register(TestType, lambda: TestType())
        assert ExampleGenerators.generate_for_type(TestType) is not None
        
        # Сбрасываем для изоляции
        ExampleGenerators.reset()
        
        # Генератор должен быть удален
        assert ExampleGenerators.generate_for_type(TestType) is None
    
    def test_test_isolation_with_unregister(self):
        """Тест изоляции тестов через unregister()."""
        ExampleGenerators.reset()
        
        class TestType:
            pass
        
        ExampleGenerators.register(TestType, lambda: TestType())
        assert ExampleGenerators.generate_for_type(TestType) is not None
        
        # Удаляем для изоляции
        ExampleGenerators.unregister(TestType)
        
        # Генератор должен быть удален
        assert ExampleGenerators.generate_for_type(TestType) is None
        
        ExampleGenerators.reset()
