from planteye_vision.configuration.configuration import ComponentConfiguration


class ShellConfiguration(ComponentConfiguration):
    def __init__(self):
        super().__init__()

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)


class PeriodicalLocalShellConfiguration(ShellConfiguration):
    def __init__(self):
        super().__init__()
        self.parameters = {'time_interval': 1000}

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'parameters' in self.cfg_dict.keys():
            if 'time_interval' in self.cfg_dict['parameters']:
                self.parameters['time_interval'] = self.cfg_dict['parameters']['time_interval']


class RestAPIShellConfiguration(ShellConfiguration):
    def __init__(self):
        super().__init__()
        self.parameters = {'host': '0.0.0.0', 'port': 5000, 'endpoint': '/get_frame'}

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'parameters' in self.cfg_dict.keys():
            if 'host' in self.cfg_dict['parameters']:
                self.parameters['host'] = self.cfg_dict['parameters']['host']
            if 'port' in self.cfg_dict['parameters']:
                self.parameters['port'] = self.cfg_dict['parameters']['port']
            if 'endpoint' in self.cfg_dict['parameters']:
                self.parameters['endpoint'] = self.cfg_dict['parameters']['endpoint']
