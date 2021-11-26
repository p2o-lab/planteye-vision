from src.inlet.inlet import Inlet
from src.configuration.configuration import StaticValueConfiguration
from src.data_chunks.data_chunk import GeneralDataChunk
from src.data_chunks.data_chunk_data import DataChunkValue
from src.data_chunks.metadata_chunk import MetadataChunkData
from src.configuration.config_provider import ConfigProvider


class StaticDataInlet(Inlet):
    """
    This class describes a static data inlet
    """
    def __init__(self):
        self.config = StaticValueConfiguration()
        self.name = None
        self.type = None

    def import_configuration(self, config_provider: ConfigProvider):
        self.name = config_provider.provide_name()
        self.config.read(config_provider)
        self.type = self.config.type

    def apply_configuration(self):
        pass

    def retrieve_data(self):
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.access_data)
        data_chunk.add_data(DataChunkValue(self.name, self.config.value))
        for metadata_variable, metadata_value in self.config.metadata.items():
            data_chunk.add_metadata(MetadataChunkData(metadata_variable, metadata_value))
        return data_chunk
