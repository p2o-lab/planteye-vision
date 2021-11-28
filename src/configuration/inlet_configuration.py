from src.configuration.config_provider import ConfigProvider
from src.configuration.configuration import GeneralConfiguration


class InletConfiguration(GeneralConfiguration):
    def __init__(self):
        super().__init__()

    def read(self, cfg_provider: ConfigProvider):
        super().read(cfg_provider)


class CameraConfiguration(InletConfiguration):
    def __init__(self):
        super().__init__()
        self.access_data = {'device_id': 0}

    def read(self, cfg_provider: ConfigProvider):
        super().read(cfg_provider)
        if 'access' in self.cfg_dict.keys():
            if 'device_id' in self.cfg_dict['access']:
                self.access_data['device_id'] = self.cfg_dict['access']['device_id']


class StaticValueConfiguration(InletConfiguration):
    def __init__(self):
        super().__init__()
        self.value = None

    def read(self, cfg_provider: ConfigProvider):
        super().read(cfg_provider)
        if 'value' in self.cfg_dict.keys():
            self.value = self.cfg_dict['value']


class OPCUAValueConfiguration(InletConfiguration):
    def __init__(self):
        super().__init__()
        self.access_data = {'server': '0.0.0.0', 'username': '', 'password': '', 'node_ns': None, 'node_id': None}

    def read(self, cfg_provider: ConfigProvider):
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