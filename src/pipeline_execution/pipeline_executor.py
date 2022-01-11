from src.inlet.generic_camera_inlet import GenericCameraInlet
from src.inlet.static_data_inlet import StaticDataInlet
from src.inlet.opcua_data_inlet import OPCUADataInlet
from src.shell.rest_api_shell import RestAPIShell
from src.shell.local_shell import LocalShell
from src.processors.data_processors import EncodeImageChunksToBase64, ChunksToDict, InputProcessor, TFModelInference, ImageResize, ImageCrop, ImageColorConversion
from src.configuration.config_provider import ConfigProvider
from src.processors.data_processor import NonConfigurableDataProcessor, ConfigurableDataProcessor

from src.data_chunks.data_chunk import GeneralDataChunk
from src.data_chunks.data_chunk_data import DataChunkValue, DataChunkImage
from src.data_chunks.metadata_chunk import MetadataChunkData

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
        self.configure_processors()

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

    def configure_processors(self):
        processors = self.config_dict['processor']

        processors_obj = []
        seq_id = 0
        for processor_name, processor_config_dict in processors.items():
            if processor_config_dict['type'] == 'input':
                processor = InputProcessor()
                processor.seq_id = seq_id
            elif processor_config_dict['type'] == 'tf_inference':
                processor = TFModelInference()
                processor.seq_id = seq_id
            elif processor_config_dict['type'] == 'image_resize':
                processor = ImageResize()
                processor.seq_id = seq_id
            elif processor_config_dict['type'] == 'image_crop':
                processor = ImageCrop()
                processor.seq_id = seq_id
            elif processor_config_dict['type'] == 'color_conversion':
                processor = ImageColorConversion()
                processor.seq_id = seq_id
            else:
                continue
            if isinstance(processor, ConfigurableDataProcessor):
                processor_config_provider = DictConfigProvider(processor_name, processor_config_dict)
                processor.import_configuration(processor_config_provider)
                processor.apply_configuration()
            processors_obj.append(processor)
            seq_id += 1
        self.processors = processors_obj

    def single_execution(self):
        data_chunks = []
        for inlet in self.inlets:
            data_chunks.append(inlet.retrieve_data())

        processing_result = data_chunks
        for processor in self.processors:
            if isinstance(processor, InputProcessor):
                processing_result = processor.apply_processor(processing_result)
                continue
            processor_chunk = processor.apply_processor(processing_result)
            if len(processor_chunk.data) == 0:
                break
            data_chunks.append(processor_chunk)
            processing_result = processor_chunk.data[0].value

        print('Pipeline result: ')
        print(processing_result)

        if isinstance(self.shell, RestAPIShell):
            EncodeImageChunksToBase64().apply_processor(data_chunks)
            data_chunks_dict = ChunksToDict().apply_processor(data_chunks)
            return json.dumps(data_chunks_dict)
        elif isinstance(self.shell, LocalShell):
            return data_chunks

    def run(self):
        self.read_configuration()
        self.apply_configuration()
