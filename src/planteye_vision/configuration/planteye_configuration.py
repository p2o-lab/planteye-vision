from planteye_vision.configuration.configuration import Configuration
from planteye_vision.configuration.shell_configuration import *
from planteye_vision.configuration.inlet_configuration import *
from planteye_vision.configuration.processor_configuration import *
import logging


class PlantEyeConfiguration(Configuration):
    def __init__(self):
        self.type = 'PlantEye'
        self.name = 'unnamed'
        self.shell = None
        self.inlets = []
        self.processors = []
        self.cfg_dict = {}
        self.configured_once = False
        self.valid_structure = True
        self.ongoing_config = False

    def read(self, cfg_dict: dict):
        self.ongoing_config = True
        self.shell = None
        self.inlets = []
        self.processors = []

        if not isinstance(cfg_dict, dict):
            self.valid_structure = False
        self.cfg_dict = cfg_dict

        if 'shell' in self.cfg_dict.keys():
            shell_cfg_dict = self.cfg_dict['shell']
            shell_cfg = self._read_shell_config(shell_cfg_dict)
            if shell_cfg is not None:
                self.shell = shell_cfg
            else:
                self.valid_structure = False
        else:
            self.valid_structure = False

        if 'inlets' in self.cfg_dict.keys():
            inlets_cfg_list = list(self.cfg_dict['inlets'].values())
            self.inlets = self._read_inlet_configs(inlets_cfg_list)

        if 'processors' in self.cfg_dict.keys():
            processors_cfg_list = list(self.cfg_dict['processors'].values())
            self.processors = self._read_processor_configs(processors_cfg_list)

        self.ongoing_config = False
        self.configured_once = True

    def update(self, cfg_dict):
        self.ongoing_config = True
        self.cfg_dict = cfg_dict
        if 'inlets' in cfg_dict.keys():
            if len(cfg_dict['inlets']) > 0:
                inlets_cfg_list = list(cfg_dict['inlets'].values())
                self.inlets = self._read_inlet_configs(inlets_cfg_list)
            else:
                self.inlets = []

        if 'processors' in cfg_dict.keys():
            if len(cfg_dict['processors']) > 0:
                processors_cfg_list = list(cfg_dict['processors'].values())
                self.processors = self._read_processor_configs(processors_cfg_list)
            else:
                self.processors = []

        self.ongoing_config = True

    def _read_shell_config(self, shell_cfg_dict):
        logging.info('Shell configuration import...')
        if 'type' in shell_cfg_dict.keys():
            if shell_cfg_dict['type'] == 'periodical_local':
                shell_cfg = PeriodicalLocalShellConfiguration()
            elif shell_cfg_dict['type'] == 'rest_api':
                shell_cfg = RestAPIShellConfiguration()
            else:
                logging.info('Fail to import shell configuration')
                return None
            logging.info('Shell configuration imported')
            shell_cfg.read(shell_cfg_dict)
            return shell_cfg
        else:
            logging.info('Fail to import shell configuration')
            return None

    def _read_inlet_configs(self, inlets_cfg_list):
        logging.info('Inlet configurations import...')
        inlet_configs = []
        for inlet_cfg_dict in inlets_cfg_list:
            if 'type' in inlet_cfg_dict.keys():
                if inlet_cfg_dict['type'] == 'static_variable':
                    inlet_cfg = StaticValueConfiguration()
                elif inlet_cfg_dict['type'] == 'opcua_variable':
                    inlet_cfg = OPCUAValueConfiguration()
                elif inlet_cfg_dict['type'] in ['local_camera_cv2', 'baumer_camera_neoapi']:
                    inlet_cfg = CameraConfiguration()
                elif inlet_cfg_dict['type'] == 'restapi':
                    inlet_cfg = RestAPIInletConfiguration()
                else:
                    continue
                inlet_cfg.read(inlet_cfg_dict)
                inlet_configs.append(inlet_cfg)
        logging.info('Inlets configuration imported')
        return inlet_configs

    def _read_processor_configs(self, processors_cfg_list):
        logging.info('Processors configurations import...')
        processor_configs = []
        for processor_cfg_dict in processors_cfg_list:
            if 'type' in processor_cfg_dict.keys():
                if processor_cfg_dict['type'] == 'input':
                    processor_cfg = InputProcessorConfiguration()
                elif processor_cfg_dict['type'] == 'image_resize':
                    processor_cfg = ImageResizeProcessorConfiguration()
                elif processor_cfg_dict['type'] == 'image_crop':
                    processor_cfg = ImageCropProcessorConfiguration()
                elif processor_cfg_dict['type'] == 'color_conversion':
                    processor_cfg = ColorConversionProcessorConfiguration()
                elif processor_cfg_dict['type'] == 'tf_inference':
                    processor_cfg = TFModelInferenceProcessorConfiguration()
                elif processor_cfg_dict['type'] == 'save_on_disk':
                    processor_cfg = SaveOnDiskProcessorConfiguration()
                else:
                    continue
                processor_cfg.read(processor_cfg_dict)
                processor_configs.append(processor_cfg)
        logging.info('Processors configuration imported')
        return processor_configs

    def is_valid(self):
        return self.valid_structure * self._components_are_valid() * self.configured_once

    def _components_are_valid(self):
        if self.shell is not None:
            if not self.shell.is_valid():
                return False

        if len(self.inlets) > 0:
            for inlet in self.inlets:
                if not inlet.is_valid():
                    return False

        if len(self.processors) > 0:
            for processor in self.processors:
                if not processor.is_valid():
                    return False

        return True

    def get_shell_config(self):
        return self.shell

    def get_inlet_configs(self):
        return self.inlets

    def get_processor_configs(self):
        return self.processors
