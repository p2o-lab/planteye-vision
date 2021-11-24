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


class RestAPIConfiguration:
    def __init__(self):
        self.host = None
        self.port = 5000
        self.endpoint_name = 'Rest API'
        self.endpoint = '/endpoint'
        self.metadata = {}

    def read(self, cfg_provider):
        cfg_dict = cfg_provider.provide_config()
        self.host = cfg_dict['access']['host']
        self.port = cfg_dict['access']['port']
        self.endpoint_name = cfg_dict['access']['name']
        self.endpoint = cfg_dict['access']['endpoint']
        if 'metadata' in cfg_dict.keys():
            self.metadata = cfg_dict['metadata']
        else:
            self.metadata = {}
