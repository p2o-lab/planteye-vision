from src.configuration.config_provider import ConfigProvider
from src.configuration.configuration import GeneralConfiguration
import cv2


class ProcessorConfiguration(GeneralConfiguration):
    def __init__(self):
        super().__init__()
        self.seq_id = 0

    def read(self, cfg_provider: ConfigProvider):
        super().read(cfg_provider)


class TFModelInferenceProcessorConfiguration(ProcessorConfiguration):
    def __init__(self):
        super().__init__()
        self.path_to_models = None
        self.model_name = None
        self.model_version = None

    def read(self, cfg_provider: ConfigProvider):
        super().read(cfg_provider)
        if 'access' in self.cfg_dict.keys():
            if 'path_to_models' in self.cfg_dict['access']:
                self.access_data['path_to_models'] = self.cfg_dict['access']['path_to_models']
            if 'model_name' in self.cfg_dict['access']:
                self.access_data['model_name'] = self.cfg_dict['access']['model_name']
            if 'model_version' in self.cfg_dict['access']:
                self.access_data['model_version'] = self.cfg_dict['access']['model_version']


class ImageResizeProcessorConfiguration(ProcessorConfiguration):
    def __init__(self):
        super().__init__()
        self.width = None
        self.height = None
        self.interpolation_method = 'INTER_NEAREST'

    def read(self, cfg_provider: ConfigProvider):
        super().read(cfg_provider)
        if 'parameters' in self.cfg_dict.keys():
            if 'width' in self.cfg_dict['parameters']:
                self.access_data['width'] = self.cfg_dict['parameters']['width']
            if 'height' in self.cfg_dict['parameters']:
                self.access_data['height'] = self.cfg_dict['parameters']['height']
            if 'interpolation' in self.cfg_dict['parameters']:
                self.access_data['interpolation'] = self.cfg_dict['parameters']['interpolation']


class ImageCropProcessorConfiguration(ProcessorConfiguration):
    def __init__(self):
        super().__init__()
        self.x_init = None
        self.x_diff = None
        self.y_init = None
        self.y_diff = None

    def read(self, cfg_provider: ConfigProvider):
        super().read(cfg_provider)
        if 'parameters' in self.cfg_dict.keys():
            if 'x_init' in self.cfg_dict['parameters']:
                self.access_data['x_init'] = self.cfg_dict['parameters']['x_init']
            if 'x_diff' in self.cfg_dict['parameters']:
                self.access_data['x_diff'] = self.cfg_dict['parameters']['x_diff']
            if 'y_init' in self.cfg_dict['parameters']:
                self.access_data['y_init'] = self.cfg_dict['parameters']['y_init']
            if 'y_diff' in self.cfg_dict['parameters']:
                self.access_data['y_diff'] = self.cfg_dict['parameters']['y_diff']


class ColorConversionProcessorConfiguration(ProcessorConfiguration):
    def __init__(self):
        super().__init__()
        self.conversion = None

    def read(self, cfg_provider: ConfigProvider):
        super().read(cfg_provider)
        if 'parameters' in self.cfg_dict.keys():
            if 'conversion' in self.cfg_dict['parameters']:
                self.access_data['conversion'] = self.cfg_dict['parameters']['conversion']


class InputProcessorConfiguration(ProcessorConfiguration):
    def __init__(self):
        super().__init__()
        self.input_inlets = []

    def read(self, cfg_provider: ConfigProvider):
        super().read(cfg_provider)
        if 'input_inlets' in self.cfg_dict.keys():
            self.access_data['input_inlets'] = self.cfg_dict['input_inlets']
