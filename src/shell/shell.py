from abc import ABC, abstractmethod
from src.configuration.config_provider import ConfigProvider


class Shell(ABC):
    @abstractmethod
    def import_configuration(self, config_provider: ConfigProvider):
        pass

    @abstractmethod
    def apply_configuration(self):
        pass

    @abstractmethod
    def attach_callback(self, callback):
        pass
