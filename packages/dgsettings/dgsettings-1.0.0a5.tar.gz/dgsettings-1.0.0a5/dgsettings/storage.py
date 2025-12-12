from abc import ABC, abstractmethod

class ConfigStorageBase(ABC):
    """Абстрактный класс для источника конфигов."""

    def __init__(self, auto_reload: bool = False):
        self.auto_reload = auto_reload

    @abstractmethod
    def load(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def save(self, data: dict):
        raise NotImplementedError

    def supports_auto_reload(self) -> bool:
        """Поддерживает ли слой отслеживание изменений (например, для файлов)."""
        return self.auto_reload

    def has_changed(self) -> bool:
        """Есть ли изменения источника (например, обновился файл на диске)."""
        return False
