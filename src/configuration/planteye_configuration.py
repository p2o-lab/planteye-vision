from src.configuration.configuration import Configuration
from src.configuration.shell_configuration import *
from src.configuration.inlet_configuration import *
from src.configuration.processor_configuration import *
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
            self._read_shell_config(shell_cfg_dict)
        else:
            self.valid_structure = False

        if 'inlets' in self.cfg_dict.keys():
            inlets_cfg_list = list(self.cfg_dict['inlets'].values())
            self._read_inlet_configs(inlets_cfg_list)

        if 'processors' in self.cfg_dict.keys():
            processors_cfg_list = list(self.cfg_dict['processors'].values())
            self._read_processor_configs(processors_cfg_list)

        self.ongoing_config = False
        self.configured_once = True

    def _read_shell_config(self, shell_cfg_dict):
        logging.info('Shell configuration import...')
        if 'type' in shell_cfg_dict.keys():
            if shell_cfg_dict['type'] == 'periodical_local':
                shell_cfg = PeriodicalLocalShellConfiguration()
            elif shell_cfg_dict['type'] == 'rest_api':
                shell_cfg = RestAPIShellConfiguration()
            else:
                self.valid_structure = False
                return
            shell_cfg.read(shell_cfg_dict)
            self.shell = shell_cfg
        else:
            self.valid_structure = False
        logging.info('Shell configuration imported')

    def _read_inlet_configs(self, inlets_cfg_list):
        logging.info('Inlet configurations import...')
        if len(inlets_cfg_list) == 0:
            logging.info('No inlets specified in configuration')
            return

        for inlet_cfg_dict in inlets_cfg_list:
            if 'type' in inlet_cfg_dict.keys():
                if inlet_cfg_dict['type'] == 'static_variable':
                    inlet_cfg = StaticValueConfiguration()
                elif inlet_cfg_dict['type'] == 'opcua_variable':
                    inlet_cfg = OPCUAValueConfiguration()
                elif inlet_cfg_dict['type'] in ['local_camera_cv2', 'baumer_camera_neo']:
                    inlet_cfg = CameraConfiguration()
                else:
                    self.valid_structure = False
                    return
                inlet_cfg.read(inlet_cfg_dict)
                self.inlets.append(inlet_cfg)
            else:
                self.valid_structure = False

        logging.info('Inlets configuration imported')

    def _read_processor_configs(self, processors_cfg_list):
        logging.info('Processor configurations import...')
        if len(processors_cfg_list) == 0:
            logging.info('No processors specified in configuration')
            return

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
                    self.valid_structure = False
                    return
                processor_cfg.read(processor_cfg_dict)
                self.processors.append(processor_cfg)
            else:
                self.valid_structure = False

        logging.info('Processors configuration imported')

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
