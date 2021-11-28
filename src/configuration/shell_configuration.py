from src.configuration.config_provider import ConfigProvider
from src.configuration.configuration import GeneralConfiguration


class ShellConfiguration(GeneralConfiguration):
    def __init__(self):
        super().__init__()

    def read(self, cfg_provider: ConfigProvider):
        super().read(cfg_provider)


class RestAPIShellConfiguration(ShellConfiguration):
    def __init__(self):
        super().__init__()
        self.access_data = {'host': '0.0.0.0', 'port': 5000, 'endpoint_name': 'RestAPI PlantEye/Vision', 'endpoint': '/get_frame'}

    def read(self, cfg_provider: ConfigProvider):
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


class LocalShellConfiguration(ShellConfiguration):
    def __init__(self):
        super().__init__()
        self.storage_path = '../data/'
        self.time_interval = 1000

    def read(self, cfg_provider: ConfigProvider):
        if 'access' in self.cfg_dict.keys():
            if 'storage_path' in self.cfg_dict['access']:
                self.access_data['storage_path'] = self.cfg_dict['access']['storage_path']
            if 'time_interval' in self.cfg_dict['access']:
                self.access_data['time_interval'] = self.cfg_dict['access']['time_interval']
