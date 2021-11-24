from src.inlet.inlet import Inlet
from src.common.configuration import StaticValueConfiguration
from src.common.data_chunk import GeneralDataChunk
from src.common.data_chunk_data import DataChunkValue
from src.common.metadata_chunk import MetadataChunkData


class StaticDataInlet(Inlet):
    """
    This class describes a static data inlet
    """
    def __init__(self):
        self.config = StaticValueConfiguration()
        self.variable_name = 'unnamed'

    def import_configuration(self, config_provider):
        self.config.read(config_provider)
        self.variable_name = config_provider.provide_name()

    def apply_configuration(self):
        pass

    def receive_data(self):
        data_chunk = GeneralDataChunk()
        data_chunk.add_data(DataChunkValue(self.variable_name, self.config.value))
        for metadata_variable, metadata_value in self.config.metadata.items():
            data_chunk.add_metadata(MetadataChunkData(metadata_variable, metadata_value))
        return data_chunk
