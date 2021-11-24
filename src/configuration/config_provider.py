from abc import ABC, abstractmethod
from yaml import safe_load


class ConfigProvider(ABC):
    @abstractmethod
    def provide_config(self):
        pass

    @abstractmethod
    def provide_name(self):
        pass


class FileConfigProvider(ConfigProvider):
    def __init__(self, cfg_name, cfg_file):
        self.cfg_name = cfg_name
        self.cfg_file = cfg_file

    def provide_config(self):
        with open(self.cfg_file) as config_file:
            cfg = safe_load(config_file)
        return cfg

    def provide_name(self):
        return self.cfg_name


class DictConfigProvider(ConfigProvider):
    def __init__(self, cfg_name, cfg_dict):
        self.cfg_name = cfg_name
        self.cfg_dict = cfg_dict

    def provide_config(self):
        return self.cfg_dict

    def provide_name(self):
        return self.cfg_name
