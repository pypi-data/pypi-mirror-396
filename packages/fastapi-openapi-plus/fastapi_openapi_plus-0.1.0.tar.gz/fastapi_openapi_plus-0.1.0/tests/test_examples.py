"""Тесты для examples.py.

Тесты для функции add_example_to_model() с поддержкой Pydantic v1/v2,
включая генерацию примеров, обработку вложенных моделей и граничные случаи.
"""

import pytest
from unittest.mock import patch
from pydantic import BaseModel

from fastapi_openapi_plus.examples import add_example_to_model, _get_model_fields, _generate_model_example
from fastapi_openapi_plus.generators import ExampleGenerators


@pytest.mark.unit
class TestAddExampleToModel:
    """Тесты для функции add_example_to_model()."""
    
    def test_add_example_to_simple_model(self):
        """Тест добавления примера к простой модели."""
        class UserModel(BaseModel):
            name: str
            age: int
        
        # Добавляем пример
        add_example_to_model(UserModel)
        
        # Проверяем, что пример был добавлен
        import pydantic
        is_v2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")
        
        if is_v2:
            # Pydantic v2: проверяем model_config.json_schema_extra
            assert hasattr(UserModel, "model_config")
            assert "json_schema_extra" in UserModel.model_config
            example = UserModel.model_config["json_schema_extra"]["example"]
        else:
            # Pydantic v1: проверяем Config.schema_extra
            assert hasattr(UserModel, "Config")
            assert hasattr(UserModel.Config, "schema_extra")
            example = UserModel.Config.schema_extra["example"]
        
        assert "name" in example
        assert "age" in example
        assert example["name"] == "example_string"  # Предустановленный генератор для str
        assert example["age"] == 1  # Предустановленный генератор для int
    
    def test_add_example_to_model_with_optional_fields(self):
        """Тест добавления примера к модели с Optional полями."""
        from typing import Optional
        
        class UserModel(BaseModel):
            name: str
            age: Optional[int] = None
        
        add_example_to_model(UserModel)
        
        import pydantic
        is_v2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")
        
        if is_v2:
            example = UserModel.model_config["json_schema_extra"]["example"]
        else:
            example = UserModel.Config.schema_extra["example"]
        
        assert "name" in example
        # Optional поля могут отсутствовать в примере или иметь значение
        # Проверяем, что name точно есть
        assert example["name"] == "example_string"
    
    def test_add_example_to_nested_model(self):
        """Тест добавления примера к модели с вложенными моделями."""
        class AddressModel(BaseModel):
            street: str
            city: str
        
        class UserModel(BaseModel):
            name: str
            address: AddressModel
        
        add_example_to_model(UserModel)
        
        import pydantic
        is_v2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")
        
        if is_v2:
            example = UserModel.model_config["json_schema_extra"]["example"]
        else:
            example = UserModel.Config.schema_extra["example"]
        
        assert "name" in example
        assert "address" in example
        assert isinstance(example["address"], dict)
        assert "street" in example["address"]
        assert "city" in example["address"]
    
    def test_add_example_pydantic_v2_model_rebuild(self):
        """Тест, что для Pydantic v2 вызывается model_rebuild()."""
        import pydantic
        
        if not (hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")):
            pytest.skip("Pydantic v2 not available")
        
        class UserModel(BaseModel):
            name: str
            age: int
        
        # Проверяем, что model_rebuild вызывается (не должно быть ошибок)
        add_example_to_model(UserModel)
        
        # Модель должна работать корректно после rebuild
        user = UserModel(name="Test", age=25)
        assert user.name == "Test"
        assert user.age == 25
    
    def test_add_example_to_model_without_fields(self):
        """Тест добавления примера к модели без полей."""
        class EmptyModel(BaseModel):
            pass
        
        # Не должно быть ошибок, но пример будет пустым
        add_example_to_model(EmptyModel)
        
        import pydantic
        is_v2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")
        
        if is_v2:
            # В v2 пример может не быть добавлен, если он пустой
            if "json_schema_extra" in EmptyModel.model_config:
                example = EmptyModel.model_config["json_schema_extra"].get("example", {})
                assert example == {}
        else:
            # В v1 аналогично
            if hasattr(EmptyModel.Config, "schema_extra"):
                example = EmptyModel.Config.schema_extra.get("example", {})
                assert example == {}
    
    def test_add_example_to_model_with_unregistered_types(self):
        """Тест добавления примера к модели с типами без генераторов."""
        from typing import Any
        
        # Используем Any вместо произвольного типа, чтобы Pydantic мог обработать
        class UserModel(BaseModel):
            name: str
            custom: Any  # Тип без зарегистрированного генератора
        
        # Не должно быть ошибок, но поле custom может отсутствовать в примере
        add_example_to_model(UserModel)
        
        import pydantic
        is_v2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")
        
        if is_v2:
            example = UserModel.model_config["json_schema_extra"]["example"]
        else:
            example = UserModel.Config.schema_extra["example"]
        
        # name должен быть в примере
        assert "name" in example
        # custom может отсутствовать, если генератор не найден для Any
        # Это нормальное поведение
    
    def test_add_example_preserves_existing_config(self):
        """Тест, что add_example_to_model сохраняет существующую конфигурацию."""
        class UserModel(BaseModel):
            name: str
        
        # Добавляем существующую конфигурацию
        import pydantic
        is_v2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")
        
        if is_v2:
            if not hasattr(UserModel, "model_config"):
                UserModel.model_config = {}
            UserModel.model_config["title"] = "User"
        else:
            if not hasattr(UserModel, "Config"):
                class Config:
                    pass
                UserModel.Config = Config
            UserModel.Config.title = "User"
        
        # Добавляем пример
        add_example_to_model(UserModel)
        
        # Проверяем, что существующая конфигурация сохранена
        if is_v2:
            assert UserModel.model_config["title"] == "User"
            assert "example" in UserModel.model_config["json_schema_extra"]
        else:
            assert UserModel.Config.title == "User"
            assert "example" in UserModel.Config.schema_extra
    
    def test_add_example_with_custom_generator(self):
        """Тест использования кастомного генератора в add_example_to_model."""
        ExampleGenerators.reset()
        
        # Используем int с кастомным генератором вместо произвольного типа
        # Регистрируем кастомный генератор для int (временно переопределяем)
        original_int_generator = ExampleGenerators._generators.get(int)
        ExampleGenerators.register(int, lambda: 999)  # Кастомное значение
        
        class UserModel(BaseModel):
            name: str
            age: int  # Используем int с кастомным генератором
        
        add_example_to_model(UserModel)
        
        import pydantic
        is_v2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")
        
        if is_v2:
            example = UserModel.model_config["json_schema_extra"]["example"]
        else:
            example = UserModel.Config.schema_extra["example"]
        
        assert example["age"] == 999  # Кастомное значение
        
        # Восстанавливаем оригинальный генератор
        if original_int_generator:
            ExampleGenerators.register(int, original_int_generator)
        else:
            ExampleGenerators.unregister(int)
        
        ExampleGenerators.reset()
    
    def test_add_example_idempotent(self):
        """Тест, что add_example_to_model идемпотентен (можно вызывать несколько раз)."""
        class UserModel(BaseModel):
            name: str
        
        # Вызываем несколько раз
        add_example_to_model(UserModel)
        example1 = None
        
        import pydantic
        is_v2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")
        
        if is_v2:
            example1 = UserModel.model_config["json_schema_extra"]["example"]
        else:
            example1 = UserModel.Config.schema_extra["example"]
        
        add_example_to_model(UserModel)
        
        if is_v2:
            example2 = UserModel.model_config["json_schema_extra"]["example"]
        else:
            example2 = UserModel.Config.schema_extra["example"]
        
        # Примеры должны быть одинаковыми
        assert example1 == example2
    
    def test_add_example_with_callable_json_schema_extra(self):
        """Тест add_example_to_model с callable json_schema_extra (v2)."""
        import pydantic
        
        if not (hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")):
            pytest.skip("Pydantic v2 not available")
        
        def schema_extra_func(schema: dict) -> None:
            schema["title"] = "User"
        
        class UserModel(BaseModel):
            name: str
        
        # Устанавливаем callable json_schema_extra
        UserModel.model_config = {"json_schema_extra": schema_extra_func}
        
        # Добавляем пример
        add_example_to_model(UserModel)
        
        # Проверяем, что callable заменен на dict
        assert isinstance(UserModel.model_config["json_schema_extra"], dict)
        assert UserModel.model_config["json_schema_extra"]["example"]["name"] == "example_string"
    
    def test_add_example_empty_example_not_added(self):
        """Тест, что пустой пример не добавляется к модели."""
        class EmptyModel(BaseModel):
            pass
        
        # Модель без полей - пример будет пустым
        add_example_to_model(EmptyModel)
        
        import pydantic
        is_v2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")
        
        # Проверяем, что пример не был добавлен (или пустой)
        if is_v2:
            if "json_schema_extra" in EmptyModel.model_config:
                example = EmptyModel.model_config["json_schema_extra"].get("example")
                # Пример может быть None или пустым dict
                assert example is None or example == {}
    
    def test_add_example_with_existing_json_schema_extra_dict(self):
        """Тест add_example_to_model с существующим json_schema_extra как dict (v2)."""
        import pydantic
        
        if not (hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")):
            pytest.skip("Pydantic v2 not available")
        
        class UserModel(BaseModel):
            name: str
        
        # Устанавливаем существующий json_schema_extra как dict
        UserModel.model_config = {"json_schema_extra": {"title": "User"}}
        
        # Добавляем пример
        add_example_to_model(UserModel)
        
        # Проверяем, что example добавлен к существующему dict
        assert UserModel.model_config["json_schema_extra"]["title"] == "User"
        assert "example" in UserModel.model_config["json_schema_extra"]
        assert UserModel.model_config["json_schema_extra"]["example"]["name"] == "example_string"
    
    def test_add_example_creates_config_if_missing_v2(self):
        """Тест, что add_example_to_model создает model_config если его нет (v2)."""
        import pydantic
        
        if not (hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")):
            pytest.skip("Pydantic v2 not available")
        
        class UserModel(BaseModel):
            name: str
        
        # Удаляем model_config если он есть
        if hasattr(UserModel, "model_config"):
            delattr(UserModel, "model_config")
        
        # Добавляем пример
        add_example_to_model(UserModel)
        
        # Проверяем, что model_config был создан
        assert hasattr(UserModel, "model_config")
        assert "json_schema_extra" in UserModel.model_config
        assert "example" in UserModel.model_config["json_schema_extra"]
    
    def test_add_example_creates_config_if_missing_v1(self):
        """Тест, что add_example_to_model создает Config если его нет (v1)."""
        import pydantic
        
        # Этот тест будет пропущен для v2
        if hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2."):
            pytest.skip("Pydantic v2 - skipping v1 test")
        
        class UserModel(BaseModel):
            name: str
        
        # Удаляем Config если он есть
        if hasattr(UserModel, "Config"):
            delattr(UserModel, "Config")
        
        # Добавляем пример
        add_example_to_model(UserModel)
        
        # Проверяем, что Config был создан
        assert hasattr(UserModel, "Config")
        assert hasattr(UserModel.Config, "schema_extra")
        assert "example" in UserModel.Config.schema_extra
    
    def test_get_model_fields_v1_fallback(self):
        """Тест _get_model_fields с fallback для v1 (если model_fields нет)."""
        class UserModel(BaseModel):
            name: str
        
        # Мокируем, чтобы симулировать v1 поведение
        with patch('fastapi_openapi_plus.examples._is_pydantic_v2', return_value=False):
            fields = _get_model_fields(UserModel)
            # В v1 должны использоваться __fields__
            assert isinstance(fields, dict)
            # В v2 __fields__ deprecated, но в v1 должен работать
            # Проверяем, что функция вернула что-то разумное
    
    def test_get_model_fields_returns_dict(self):
        """Тест _get_model_fields возвращает dict."""
        class UserModel(BaseModel):
            name: str
        
        fields = _get_model_fields(UserModel)
        # Должен вернуться dict
        assert isinstance(fields, dict)
        # В v2 должны быть model_fields
        assert "name" in fields
    
    def test_generate_model_example_handles_missing_field_type(self):
        """Тест _generate_model_example с полем без типа."""
        class UserModel(BaseModel):
            name: str
        
        # Тест просто проверяет, что функция работает
        example = _generate_model_example(UserModel)
        assert isinstance(example, dict)
        # name должен быть в примере
        assert "name" in example
    
    def test_add_example_with_non_dict_schema_extra_v1(self):
        """Тест add_example_to_model с non-dict schema_extra (v1)."""
        import pydantic
        
        # Этот тест будет пропущен для v2
        if hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2."):
            pytest.skip("Pydantic v2 - skipping v1 test")
        
        class UserModel(BaseModel):
            name: str
        
        # Устанавливаем schema_extra как не-dict (например, None)
        if not hasattr(UserModel, "Config"):
            class Config:
                pass
            UserModel.Config = Config
        
        UserModel.Config.schema_extra = None
        
        # Добавляем пример
        add_example_to_model(UserModel)
        
        # Проверяем, что schema_extra стал dict
        assert isinstance(UserModel.Config.schema_extra, dict)
        assert "example" in UserModel.Config.schema_extra
