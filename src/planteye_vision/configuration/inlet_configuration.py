from planteye_vision.configuration.configuration import ComponentConfiguration


class InletConfiguration(ComponentConfiguration):
    def __init__(self):
        super().__init__()

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)


class CameraConfiguration(InletConfiguration):
    def __init__(self):
        super().__init__()
        self.parameters = {'device_id': 0}

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'parameters' in self.cfg_dict.keys():
            if 'device_id' in self.cfg_dict['parameters']:
                self.parameters['device_id'] = self.cfg_dict['parameters']['device_id']


class StaticValueConfiguration(InletConfiguration):
    def __init__(self):
        super().__init__()

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'parameters' in self.cfg_dict.keys():
            if 'value' in self.cfg_dict['parameters']:
                self.parameters['value'] = self.cfg_dict['parameters']['value']
            else:
                self.valid = False
        else:
            self.valid = False


class OPCUAValueConfiguration(InletConfiguration):
    def __init__(self):
        super().__init__()
        self.parameters = {'server': '0.0.0.0', 'username': '', 'password': '', 'node_ns': None, 'node_id': None}

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'parameters' in self.cfg_dict.keys():
            if 'server' in self.cfg_dict['parameters']:
                self.parameters['server'] = self.cfg_dict['parameters']['server']
            if 'username' in self.cfg_dict['parameters']:
                self.parameters['username'] = self.cfg_dict['parameters']['username']
            if 'password' in self.cfg_dict['parameters']:
                self.parameters['password'] = self.cfg_dict['parameters']['password']
            if 'node_ns' in self.cfg_dict['parameters']:
                self.parameters['node_ns'] = self.cfg_dict['parameters']['node_ns']
            else:
                self.valid = False
            if 'node_id' in self.cfg_dict['parameters']:
                self.parameters['node_id'] = self.cfg_dict['parameters']['node_id']
            else:
                self.valid = False
        else:
            self.valid = False


class RestAPIInletConfiguration(InletConfiguration):
    def __init__(self):
        super().__init__()

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'parameters' in self.cfg_dict.keys():
            if 'endpoint' in self.cfg_dict['parameters']:
                self.parameters['endpoint'] = self.cfg_dict['parameters']['endpoint']
            else:
                self.valid = False
        else:
            self.valid = False
