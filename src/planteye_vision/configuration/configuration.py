from abc import ABC, abstractmethod


class Configuration(ABC):
    @abstractmethod
    def read(self, cfg_dict: dict):
        pass


class ComponentConfiguration(Configuration):
    def __init__(self):
        self.name = 'unnamed'
        self.type = 'unspecified'
        self.hidden = False
        self.parameters = {}
        self.metadata = {}
        self.cfg_dict = {}
        self.valid = True

    def read(self, cfg_dict):
        self.cfg_dict = cfg_dict
        if 'name' in self.cfg_dict.keys():
            self.name = self.cfg_dict['name']
        if 'type' in self.cfg_dict.keys():
            self.type = self.cfg_dict['type']
        else:
            self.valid = False
        if 'hidden' in self.cfg_dict.keys():
            self.hidden = self.cfg_dict['hidden']
        if 'parameters' in self.cfg_dict.keys():
            self.parameters = self.cfg_dict['parameters']
        if 'metadata' in self.cfg_dict.keys():
            self.metadata = self.cfg_dict['metadata']

    def is_valid(self):
        return self.valid
