"""Реестр генераторов примеров для различных типов.

Модуль предоставляет класс ExampleGenerators для регистрации и генерации примеров
для различных типов Python. Используется для автоматической генерации примеров
в OpenAPI документации FastAPI.

ВАЖНО: Реестр является глобальным shared state. Для тестов используйте
reset() или unregister() для изоляции тестовых сценариев.

Пример использования:
    ```python
    from fastapi_openapi_plus import ExampleGenerators
    
    # Регистрация кастомного генератора
    ExampleGenerators.register(MyType, lambda: MyType.example())
    
    # Генерация примера
    example = ExampleGenerators.generate_for_type(MyType)
    ```
"""

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Union, get_args, get_origin
from uuid import UUID, uuid4

# Для Python < 3.9 совместимость с typing_extensions
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


class ExampleGenerators:
    """Реестр генераторов примеров для различных типов.
    
    Класс предоставляет методы для регистрации и генерации примеров для типов.
    Реестр является глобальным shared state - все изменения применяются ко всем
    экземплярам и использованиям библиотеки.
    
    Предустановленные генераторы регистрируются при импорте модуля.
    
    Пример:
        ```python
        from fastapi_openapi_plus import ExampleGenerators
        
        # Регистрация кастомного генератора
        ExampleGenerators.register(MyType, lambda: MyType.example())
        
        # Генерация примера
        example = ExampleGenerators.generate_for_type(MyType)
        
        # Сброс реестра (для тестов)
        ExampleGenerators.reset()
        ```
    """
    
    # Глобальный реестр генераторов (shared state)
    _generators: Dict[type, Callable[[], Any]] = {}
    _default_generators: Dict[type, Callable[[], Any]] = {}
    
    @classmethod
    def register(cls, type_hint: type, generator: Callable[[], Any]) -> None:
        """Регистрирует генератор для указанного типа.
        
        Args:
            type_hint: Тип, для которого регистрируется генератор
            generator: Функция без параметров, возвращающая пример для типа
            
        Raises:
            TypeError: Если type_hint не является типом
            TypeError: Если generator не является callable
            
        Пример:
            ```python
            ExampleGenerators.register(str, lambda: "example_string")
            ExampleGenerators.register(int, lambda: 42)
            ```
        """
        if not isinstance(type_hint, type):
            raise TypeError(f"type_hint must be a type, got {type(type_hint).__name__}")
        if not callable(generator):
            raise TypeError(f"generator must be callable, got {type(generator).__name__}")
        
        cls._generators[type_hint] = generator
    
    @classmethod
    def _normalize_type(cls, type_hint: Any) -> Any:
        """Нормализует тип, извлекая базовый тип из Optional/Union/Annotated.
        
        Обрабатывает:
        - Optional[T] / Union[T, None] → T
        - Annotated[T, ...] → T
        
        Args:
            type_hint: Тип для нормализации
            
        Returns:
            Нормализованный тип или исходный тип, если нормализация не требуется
            
        Пример:
            ```python
            from typing import Optional, Union, Annotated
            
            # Optional[str] → str
            normalized = ExampleGenerators._normalize_type(Optional[str])
            
            # Union[int, None] → int
            normalized = ExampleGenerators._normalize_type(Union[int, None])
            
            # Annotated[str, ...] → str
            normalized = ExampleGenerators._normalize_type(Annotated[str, "description"])
            ```
        """
        # Обработка Annotated[T, ...]
        origin = get_origin(type_hint)
        if origin is not None:
            # Annotated[T, ...] имеет origin = Annotated
            if origin is Annotated:
                args = get_args(type_hint)
                if args:
                    # Извлекаем первый аргумент (базовый тип)
                    return cls._normalize_type(args[0])
            
            # Обработка Optional[T] и Union[T, None]
            # Optional[T] это Union[T, None] в Python
            # Используем сравнение для совместимости с разными версиями Python
            is_union = origin is Union or origin == Union
            if not is_union and hasattr(origin, '__name__'):
                is_union = origin.__name__ == 'Union'
            
            if is_union:
                args = get_args(type_hint)
                # Фильтруем None из Union
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    # Union[T, None] → T
                    return cls._normalize_type(non_none_args[0])
                elif len(non_none_args) > 1:
                    # Union[T1, T2, ...] - возвращаем первый не-None тип
                    return cls._normalize_type(non_none_args[0])
        
        # Если это обычный тип или уже нормализован
        return type_hint
    
    @classmethod
    def generate_for_type(cls, type_hint: Any) -> Optional[Any]:
        """Генерирует пример для указанного типа.
        
        Сначала нормализует тип (извлекает базовый тип из Optional/Union/Annotated),
        затем ищет зарегистрированный генератор. Если генератор не найден,
        возвращает None (не подставляет placeholder).
        
        Args:
            type_hint: Тип, для которого нужно сгенерировать пример
            
        Returns:
            Пример для типа или None, если генератор не найден
            
        Пример:
            ```python
            # Для зарегистрированного типа
            example = ExampleGenerators.generate_for_type(str)  # "example_string"
            
            # Для незарегистрированного типа
            example = ExampleGenerators.generate_for_type(MyType)  # None
            ```
        """
        # Нормализуем тип
        normalized_type = cls._normalize_type(type_hint)
        
        # Если после нормализации это не тип, возвращаем None
        if not isinstance(normalized_type, type):
            return None
        
        # Ищем генератор в реестре
        generator = cls._generators.get(normalized_type)
        if generator is not None:
            return generator()
        
        # Генератор не найден - возвращаем None (не подставляем placeholder)
        return None
    
    @classmethod
    def generate_for_default(cls, default: Any, **kwargs) -> Optional[Any]:
        """Генерирует пример на основе default значения.
        
        Если default не является Ellipsis (...), возвращает default как пример.
        Иначе пытается определить тип из kwargs и сгенерировать пример.
        
        Args:
            default: Значение по умолчанию
            **kwargs: Дополнительные параметры (например, type_hint)
            
        Returns:
            Пример на основе default или None
            
        Пример:
            ```python
            # Использование default как пример
            example = ExampleGenerators.generate_for_default(42)  # 42
            
            # Генерация на основе type_hint
            example = ExampleGenerators.generate_for_default(..., type_hint=str)  # "example_string"
            ```
        """
        # Если default не Ellipsis, используем его как пример
        if default is not ...:
            return default
        
        # Пытаемся получить тип из kwargs
        type_hint = kwargs.get("type_hint")
        if type_hint is not None:
            return cls.generate_for_type(type_hint)
        
        return None
    
    @classmethod
    def reset(cls) -> None:
        """Сбрасывает реестр генераторов к предустановленным значениям.
        
        Удаляет все пользовательские регистрации, оставляя только
        предустановленные генераторы. Используется для изоляции тестов.
        
        Пример:
            ```python
            # Регистрация пользовательского генератора
            ExampleGenerators.register(MyType, lambda: MyType.example())
            
            # Сброс к предустановленным
            ExampleGenerators.reset()
            # Теперь MyType больше не зарегистрирован
            ```
        """
        cls._generators = cls._default_generators.copy()
    
    @classmethod
    def unregister(cls, type_hint: type) -> None:
        """Удаляет генератор для указанного типа.
        
        Удаляет только указанный генератор, оставляя остальные без изменений.
        Используется для изоляции тестов.
        
        Args:
            type_hint: Тип, для которого нужно удалить генератор
            
        Пример:
            ```python
            # Удаление генератора для str
            ExampleGenerators.unregister(str)
            
            # Теперь generate_for_type(str) вернет None
            ```
        """
        if type_hint in cls._generators:
            del cls._generators[type_hint]


def _register_default_generators() -> None:
    """Регистрирует предустановленные генераторы.
    
    Вызывается при импорте модуля для регистрации стандартных генераторов:
    - str → "example_string"
    - int → 1
    - bool → False
    - float → 1.0
    - UUID → str(uuid4())
    - datetime → datetime.now(timezone.utc).isoformat()
    """
    ExampleGenerators.register(str, lambda: "example_string")
    ExampleGenerators.register(int, lambda: 1)
    ExampleGenerators.register(bool, lambda: False)
    ExampleGenerators.register(float, lambda: 1.0)
    ExampleGenerators.register(UUID, lambda: str(uuid4()))
    ExampleGenerators.register(datetime, lambda: datetime.now(timezone.utc).isoformat())
    
    # Сохраняем копию предустановленных генераторов для reset()
    ExampleGenerators._default_generators = ExampleGenerators._generators.copy()


# Регистрируем предустановленные генераторы при импорте модуля
_register_default_generators()
