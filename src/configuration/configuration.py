from abc import ABC, abstractmethod
from src.configuration.config_provider import ConfigProvider


class Configuration(ABC):
    @abstractmethod
    def read(self, cfg_provider: ConfigProvider):
        pass


class GeneralConfiguration(Configuration):
    def __init__(self):
        self.type = 'unspecified'
        self.parameters = []
        self.metadata = {}
        self.access_data = {}
        self.cfg_dict = {}
        self.valid = True

    def read(self, cfg_provider: ConfigProvider):
        self.cfg_dict = cfg_provider.provide_config()
        if 'type' in self.cfg_dict.keys():
            self.type = self.cfg_dict['type']
        if 'parameters' in self.cfg_dict.keys():
            self.parameters = self.cfg_dict['parameters']
        if 'metadata' in self.cfg_dict.keys():
            self.metadata = self.cfg_dict['metadata']

    def is_valid(self):
        return self.valid
