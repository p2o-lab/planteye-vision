from src.inlet.generic_camera_inlet import GenericCameraInlet
from src.inlet.static_data_inlet import StaticDataInlet
from src.inlet.opcua_data_inlet import OPCUADataInlet
from src.shell.rest_api_shell import RestAPIShell
from src.shell.local_shell import LocalShell
from src.processors.data_processor import EncodeImageChunksToBase64, ChunksToDict
from src.configuration.config_provider import ConfigProvider

from src.configuration.config_provider import DictConfigProvider
import json


class PipeLineExecutor:
    def __init__(self, config_provider: ConfigProvider):
        self.config_provider = config_provider
        self.config_dict = None
        self.shell = None
        self.inlets = []
        self.processors = []

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
            else:
                continue
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
            elif shell_config_dict['type'] == 'local':
                self.shell = LocalShell()
            shell_config_provider = DictConfigProvider(shell_name, shell_config_dict)
            self.shell.import_configuration(shell_config_provider)
            self.shell.attach_callback(self.single_execution)
            self.shell.apply_configuration()

    def single_execution(self):
        data_chunks = []
        for inlet in self.inlets:
            data_chunks.append(inlet.retrieve_data())
        for processor in self.processors:
            processor.apply_processor(data_chunks)
        if isinstance(self.shell, RestAPIShell):
            EncodeImageChunksToBase64().apply_processor(data_chunks)
            data_chunks_dict = ChunksToDict().apply_processor(data_chunks)
            return json.dumps(data_chunks_dict)
        elif isinstance(self.shell, LocalShell):
            return data_chunks

    def add_transformer(self, transformer):
        self.processors.append(transformer)

    def run(self):
        self.read_configuration()
        self.apply_configuration()
