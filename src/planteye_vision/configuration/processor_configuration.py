from planteye_vision.configuration.configuration import ComponentConfiguration


class ProcessorConfiguration(ComponentConfiguration):
    def __init__(self):
        super().__init__()
        self.seq_id = 0

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)


class TFModelInferenceProcessorConfiguration(ProcessorConfiguration):
    def __init__(self):
        super().__init__()

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'parameters' in self.cfg_dict.keys():
            if 'path_to_models' in self.cfg_dict['parameters']:
                self.parameters['path_to_models'] = self.cfg_dict['parameters']['path_to_models']
            else:
                self.parameters['path_to_models'] = None
                self.valid = False
            if 'model_name' in self.cfg_dict['parameters']:
                self.parameters['model_name'] = self.cfg_dict['parameters']['model_name']
            else:
                self.parameters['model_name'] = None
                self.valid = False
            if 'model_version' in self.cfg_dict['parameters']:
                self.parameters['model_version'] = self.cfg_dict['parameters']['model_version']
            else:
                self.parameters['model_version'] = None
                self.valid = False
        else:
            self.valid = False


class ImageResizeProcessorConfiguration(ProcessorConfiguration):
    def __init__(self):
        super().__init__()

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'parameters' in self.cfg_dict.keys():
            if 'width' in self.cfg_dict['parameters']:
                self.parameters['width'] = self.cfg_dict['parameters']['width']
            else:
                self.parameters['width'] = None
                self.valid = False
            if 'height' in self.cfg_dict['parameters']:
                self.parameters['height'] = self.cfg_dict['parameters']['height']
            else:
                self.parameters['height'] = None
                self.valid = False
            if 'interpolation' in self.cfg_dict['parameters']:
                self.parameters['interpolation'] = self.cfg_dict['parameters']['interpolation']
            else:
                self.parameters['height'] = 'INTER_NEAREST'
        else:
            self.valid = False


class ImageCropProcessorConfiguration(ProcessorConfiguration):
    def __init__(self):
        super().__init__()

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'parameters' in self.cfg_dict.keys():
            if 'x_init' in self.cfg_dict['parameters']:
                self.parameters['x_init'] = self.cfg_dict['parameters']['x_init']
            else:
                self.parameters['x_init'] = None
                self.valid = False
            if 'x_diff' in self.cfg_dict['parameters']:
                self.parameters['x_diff'] = self.cfg_dict['parameters']['x_diff']
            else:
                self.parameters['x_diff'] = None
                self.valid = False
            if 'y_init' in self.cfg_dict['parameters']:
                self.parameters['y_init'] = self.cfg_dict['parameters']['y_init']
            else:
                self.parameters['y_init'] = None
                self.valid = False
            if 'y_diff' in self.cfg_dict['parameters']:
                self.parameters['y_diff'] = self.cfg_dict['parameters']['y_diff']
            else:
                self.parameters['y_diff'] = None
                self.valid = False
        else:
            self.valid = False


class ColorConversionProcessorConfiguration(ProcessorConfiguration):
    def __init__(self):
        super().__init__()

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'parameters' in self.cfg_dict.keys():
            if 'conversion' in self.cfg_dict['parameters']:
                self.parameters['conversion'] = self.cfg_dict['parameters']['conversion']
            else:
                self.parameters['conversion'] = None
                self.valid = False
        else:
            self.valid = False


class InputProcessorConfiguration(ProcessorConfiguration):
    def __init__(self):
        super().__init__()
        self.parameters['input_inlets'] = []

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'input_inlets' in self.cfg_dict.keys():
            if self.cfg_dict['input_inlets'] is not None:
                self.parameters['input_inlets'] = self.cfg_dict['input_inlets']
            else:
                self.parameters['input_inlets'] = []
                self.valid = False
        else:
            self.parameters['input_inlets'] = []
            self.valid = False


class SaveOnDiskProcessorConfiguration(ProcessorConfiguration):
    def __init__(self):
        super().__init__()
        self.parameters['save_path'] = '../data/'

    def read(self, cfg_dict: dict):
        super().read(cfg_dict)
        if 'parameters' in self.cfg_dict.keys():
            if 'save_path' in self.cfg_dict['parameters']:
                self.parameters['save_path'] = self.cfg_dict['parameters']['save_path']
