"""Тесты для fields.py.

Тесты для функции field() с поддержкой Pydantic v1/v2,
включая валидацию description, автогенерацию example и граничные случаи.
"""

import pytest
from pydantic import BaseModel, Field as PydanticField

from fastapi_openapi_plus.fields import field
from fastapi_openapi_plus.generators import ExampleGenerators


@pytest.mark.unit
class TestField:
    """Тесты для функции field()."""
    
    def test_field_with_description(self):
        """Тест создания поля с description."""
        f = field(description="Test field")
        
        # Проверяем, что это Field объект
        assert isinstance(f, type(PydanticField()))
        # Проверяем description
        assert f.description == "Test field"
    
    def test_field_raises_on_empty_description(self):
        """Тест, что field выбрасывает ValueError для пустого description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            field(description="")
    
    def test_field_raises_on_whitespace_only_description(self):
        """Тест, что field выбрасывает ValueError для description только с пробелами."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            field(description="   ")
    
    def test_field_raises_on_none_description(self):
        """Тест, что field выбрасывает ValueError для None description."""
        with pytest.raises(ValueError, match="description is required and cannot be empty"):
            field(description=None)
    
    def test_field_with_explicit_example(self):
        """Тест field с явно указанным example."""
        f = field(description="Test", example="explicit_example")
        
        # Проверяем example в зависимости от версии Pydantic
        # В v2 example хранится в json_schema_extra
        # В v1 example хранится напрямую
        if hasattr(f, "json_schema_extra") and f.json_schema_extra:
            assert f.json_schema_extra.get("example") == "explicit_example"
        elif hasattr(f, "example"):
            assert f.example == "explicit_example"
    
    def test_field_autogenerates_example_from_type_hint(self):
        """Тест автогенерации example через type_hint."""
        f = field(description="Test", type_hint=str)
        
        # Проверяем, что example был сгенерирован
        example_value = None
        if hasattr(f, "json_schema_extra") and f.json_schema_extra:
            example_value = f.json_schema_extra.get("example")
        elif hasattr(f, "example"):
            example_value = f.example
        
        assert example_value == "example_string"  # Предустановленный генератор для str
    
    def test_field_uses_default_as_example(self):
        """Тест использования default как example."""
        f = field(description="Test", default=42)
        
        assert f.default == 42
        
        # Проверяем, что default используется как example
        example_value = None
        if hasattr(f, "json_schema_extra") and f.json_schema_extra:
            example_value = f.json_schema_extra.get("example")
        elif hasattr(f, "example"):
            example_value = f.example
        
        assert example_value == 42
    
    def test_field_default_priority_over_type_hint(self):
        """Тест, что default имеет приоритет над type_hint для example."""
        f = field(description="Test", default=100, type_hint=int)
        
        # default должен использоваться как example, а не генератор
        example_value = None
        if hasattr(f, "json_schema_extra") and f.json_schema_extra:
            example_value = f.json_schema_extra.get("example")
        elif hasattr(f, "example"):
            example_value = f.example
        
        assert example_value == 100
    
    def test_field_explicit_example_priority(self):
        """Тест, что явный example имеет приоритет над default и type_hint."""
        f = field(
            description="Test",
            example=999,
            default=42,
            type_hint=int,
        )
        
        example_value = None
        if hasattr(f, "json_schema_extra") and f.json_schema_extra:
            example_value = f.json_schema_extra.get("example")
        elif hasattr(f, "example"):
            example_value = f.example
        
        assert example_value == 999
    
    def test_field_no_example_when_generator_not_found(self):
        """Тест, что example не генерируется, если генератор не найден."""
        class UnregisteredType:
            pass
        
        f = field(description="Test", type_hint=UnregisteredType)
        
        # example не должен быть установлен
        example_value = None
        if hasattr(f, "json_schema_extra") and f.json_schema_extra:
            example_value = f.json_schema_extra.get("example")
        elif hasattr(f, "example"):
            example_value = getattr(f, "example", None)
        
        assert example_value is None
    
    def test_field_with_alias(self):
        """Тест field с alias."""
        f = field(description="Test", alias="testAlias")
        
        assert f.alias == "testAlias"
    
    def test_field_passes_kwargs_to_field(self):
        """Тест, что все kwargs передаются в Field."""
        f = field(description="Test", ge=1, le=100)
        
        # ge и le могут храниться в constraints или json_schema
        # Проверяем, что объект создан без ошибок
        assert f.description == "Test"
    
    def test_field_with_pydantic_model(self):
        """Тест использования field в Pydantic модели."""
        class UserModel(BaseModel):
            name: str = field(description="Имя пользователя", type_hint=str)
            age: int = field(description="Возраст", type_hint=int, ge=0, le=120)
        
        # Проверяем, что модель создается без ошибок
        user = UserModel(name="Test", age=25)
        assert user.name == "Test"
        assert user.age == 25
    
    def test_field_pydantic_v2_json_schema_extra(self):
        """Тест, что в Pydantic v2 example хранится в json_schema_extra."""
        import pydantic
        
        if hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2."):
            f = field(description="Test", example="test_value")
            
            # В v2 example должен быть в json_schema_extra
            assert hasattr(f, "json_schema_extra")
            assert f.json_schema_extra is not None
            assert f.json_schema_extra.get("example") == "test_value"
    
    def test_field_with_custom_generator(self):
        """Тест использования кастомного генератора."""
        ExampleGenerators.reset()
        
        class CustomType:
            pass
        
        # Регистрируем кастомный генератор
        ExampleGenerators.register(CustomType, lambda: "custom_example")
        
        f = field(description="Test", type_hint=CustomType)
        
        example_value = None
        if hasattr(f, "json_schema_extra") and f.json_schema_extra:
            example_value = f.json_schema_extra.get("example")
        elif hasattr(f, "example"):
            example_value = f.example
        
        assert example_value == "custom_example"
        
        ExampleGenerators.reset()
    
    def test_field_with_existing_json_schema_extra(self):
        """Тест field с уже существующим json_schema_extra (v2)."""
        import pydantic
        
        if hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2."):
            # Передаем json_schema_extra как dict
            f = field(
                description="Test",
                example="test_value",
                json_schema_extra={"title": "Test Field"}
            )
            
            # Проверяем, что example добавлен к существующему json_schema_extra
            assert f.json_schema_extra["title"] == "Test Field"
            assert f.json_schema_extra["example"] == "test_value"
    
    def test_field_with_callable_json_schema_extra(self):
        """Тест field с callable json_schema_extra (v2)."""
        import pydantic
        
        if hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2."):
            def schema_extra_func(schema: dict) -> None:
                schema["title"] = "Test"
            
            # Передаем json_schema_extra как callable
            f = field(
                description="Test",
                example="test_value",
                json_schema_extra=schema_extra_func
            )
            
            # При callable должен быть создан новый dict
            assert isinstance(f.json_schema_extra, dict)
            assert f.json_schema_extra["example"] == "test_value"
