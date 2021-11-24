from src.inlet.generic_camera_inlet import GenericCameraInlet
from src.inlet.static_data_inlet import StaticDataInlet
from src.inlet.opcua_data_inlet import OPCUADataInlet
from src.shell.rest_api_shell import RestAPIShell

from src.common.config_provider import FileConfigProvider, DictConfigProvider
import time
import json


class PipeLineExecutor:
    def __init__(self, config_provider):
        self.config_provider = config_provider
        self.config_dict = None
        self.inlets = []
        self.transformers = []
        self.outlets = []
        self.shell = None

    def read_configuration(self):
        self.config_dict = self.config_provider.provide_config()

    def apply_configuration(self):
        self.configure_inlets()
        self.configure_shell()

    def configure_inlets(self):
        inlets = self.config_dict['inlet']

        inlets_obj = []
        for inlet_name, inlet_config_dict in inlets.items():
            if inlet_config_dict['type'] == 'local_camera_cv2':
                inlet = GenericCameraInlet()
            elif inlet_config_dict['type'] == 'static_variable':
                inlet = StaticDataInlet()
            elif inlet_config_dict['type'] == 'opcua_variable':
                inlet = OPCUADataInlet()
            inlet_config_provider = DictConfigProvider(inlet_name, inlet_config_dict)
            inlet.import_configuration(inlet_config_provider)
            inlet.apply_configuration()
            inlets_obj.append(inlet)
            self.inlets = inlets_obj

    def configure_shell(self):
        shells = self.config_dict['shell']

        for shell_name, shell_config_dict in shells.items():
            if shell_config_dict['type'] == 'rest_api':
                self.shell = RestAPIShell()
            shell_config_provider = DictConfigProvider(shell_name, shell_config_dict)
            self.shell.import_configuration(shell_config_provider)
            self.shell.attach_callback(self.single_execution)
            self.shell.apply_configuration()

    def single_execution(self):
        data_chunks = []
        for inlet in self.inlets:
            data_chunks.append(inlet.retrieve_data().as_dict())
        print(data_chunks)
        return json.dumps({'data': 'some data'})


cfg_provider = FileConfigProvider('config', '../config.yaml')
pipeline_exec = PipeLineExecutor(cfg_provider)
pipeline_exec.read_configuration()
pipeline_exec.apply_configuration()
