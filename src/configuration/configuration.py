from abc import ABC, abstractmethod


class Configuration(ABC):
    @abstractmethod
    def read(self, cfg_provider):
        pass


class GeneralConfiguration(Configuration):
    def __init__(self):
        self.type = 'unspecified'
        self.parameters = []
        self.metadata = {}
        self.access_data = {}
        self.cfg_dict = {}

    def read(self, cfg_provider):
        self.cfg_dict = cfg_provider.provide_config()
        if 'type' in self.cfg_dict.keys():
            self.type = self.cfg_dict['type']
        if 'parameters' in self.cfg_dict.keys():
            self.parameters = self.cfg_dict['parameters']
        if 'metadata' in self.cfg_dict.keys():
            self.metadata = self.cfg_dict['metadata']


class CameraConfiguration(GeneralConfiguration):
    def __init__(self):
        super().__init__()
        self.access_data = {'device_id': 0}

    def read(self, cfg_provider):
        super().read(cfg_provider)
        if 'access' in self.cfg_dict.keys():
            if 'device_id' in self.cfg_dict['access']:
                self.access_data['device_id'] = self.cfg_dict['access']['device_id']


class StaticValueConfiguration(GeneralConfiguration):
    def __init__(self):
        super().__init__()
        self.value = None

    def read(self, cfg_provider):
        super().read(cfg_provider)
        if 'value' in self.cfg_dict.keys():
            self.value = self.cfg_dict['value']


class OPCUAValueConfiguration(GeneralConfiguration):
    def __init__(self):
        super().__init__()
        self.value = None
        self.access_data = {'server': '0.0.0.0', 'username': '', 'password': '', 'node_ns': None, 'node_id': None}

    def read(self, cfg_provider):
        super().read(cfg_provider)
        if 'access' in self.cfg_dict.keys():
            if 'server' in self.cfg_dict['access']:
                self.access_data['server'] = self.cfg_dict['access']['server']
            if 'username' in self.cfg_dict['access']:
                self.access_data['username'] = self.cfg_dict['access']['username']
            if 'password' in self.cfg_dict['access']:
                self.access_data['password'] = self.cfg_dict['access']['password']
            if 'node_ns' in self.cfg_dict['access']:
                self.access_data['node_ns'] = self.cfg_dict['access']['node_ns']
            if 'node_id' in self.cfg_dict['access']:
                self.access_data['node_id'] = self.cfg_dict['access']['node_id']


class RestAPIConfiguration(GeneralConfiguration):
    def __init__(self):
        super().__init__()
        self.value = None
        self.access_data = {'host': '0.0.0.0', 'port': 5000, 'endpoint_name': 'RestAPI PlantEye/Vision', 'endpoint': '/get_frame'}
        self.metadata = {}

    def read(self, cfg_provider):
        if 'access' in self.cfg_dict.keys():
            if 'server' in self.cfg_dict['access']:
                self.access_data['host'] = self.cfg_dict['access']['host']
            if 'port' in self.cfg_dict['access']:
                self.access_data['port'] = self.cfg_dict['access']['port']
            if 'server_password' in self.cfg_dict['access']:
                self.access_data['server_url'] = self.cfg_dict['access']['password']
            if 'endpoint_name' in self.cfg_dict['access']:
                self.access_data['endpoint_name'] = self.cfg_dict['access']['endpoint_name']
            if 'endpoint' in self.cfg_dict['access']:
                self.access_data['endpoint'] = self.cfg_dict['access']['endpoint']


class LocalShellConfiguration(GeneralConfiguration):
    def __init__(self):
        super().__init__()
        self.storage_path = '../data/'
        self.time_interval = 1000

    def read(self, cfg_provider):
        if 'access' in self.cfg_dict.keys():
            if 'storage_path' in self.cfg_dict['access']:
                self.access_data['storage_path'] = self.cfg_dict['access']['storage_path']
            if 'time_interval' in self.cfg_dict['access']:
                self.access_data['time_interval'] = self.cfg_dict['access']['time_interval']
