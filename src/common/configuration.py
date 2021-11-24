from abc import ABC, abstractmethod


class Configuration(ABC):
    @abstractmethod
    def read(self, cfg_provider):
        pass


class CameraConfiguration(Configuration):
    def __init__(self):
        self.type = 'unspecified'
        self.device_id = 0
        self.parameters = []
        self.metadata = {}

    def read(self, cfg_provider):
        cfg_dict = cfg_provider.provide_config()
        self.type = cfg_dict['type']
        self.device_id = cfg_dict['access']['device_id']
        self.parameters = cfg_dict['parameters']
        self.metadata = cfg_dict['metadata']


class StaticValueConfiguration:
    def __init__(self):
        self.value = None
        self.metadata = {}

    def read(self, cfg_provider):
        cfg_dict = cfg_provider.provide_config()
        self.value = cfg_dict['value']
        self.metadata = cfg_dict['metadata']


class OPCUAValueConfiguration:
    def __init__(self):
        self.server_url = None
        self.server_user = ''
        self.server_password = ''
        self.namespace = None
        self.node_id = None
        self.metadata = {}

    def read(self, cfg_provider):
        cfg_dict = cfg_provider.provide_config()
        self.server_url = cfg_dict['access']['server']
        self.server_user = cfg_dict['access']['username']
        self.server_password = cfg_dict['access']['password']
        self.namespace = cfg_dict['access']['node_ns']
        self.node_id = cfg_dict['access']['node_id']
        self.metadata = cfg_dict['metadata']
