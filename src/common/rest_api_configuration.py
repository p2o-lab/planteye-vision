class CameraConfiguration:
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 5000
        self.name = 'unnamed'
        self.endpoint = '/get_frame'

    def read(self, cfg):
        cfg_dict = cfg.provide_cfg()
        self.host = cfg_dict['host']
        self.port = cfg_dict['port']
        self.name = cfg_dict['name']
        self.endpoint = cfg_dict['endpoint']
