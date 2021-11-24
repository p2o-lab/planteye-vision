from src.inlet.inlet import Inlet
from src.configuration.configuration import StaticValueConfiguration
from src.data_chunks.data_chunk import GeneralDataChunk
from src.data_chunks.data_chunk_data import DataChunkValue
from src.data_chunks.metadata_chunk import MetadataChunkData


class StaticDataInlet(Inlet):
    """
    This class describes a static data inlet
    """
    def __init__(self):
        self.config = StaticValueConfiguration()
        self.name = None

    def import_configuration(self, config_provider):
        self.config.read(config_provider)
        self.name = config_provider.provide_name()

    def apply_configuration(self):
        pass

    def retrieve_data(self):
        data_chunk = GeneralDataChunk(self.name)
        data_chunk.add_data(DataChunkValue(self.name, self.config.value))
        for metadata_variable, metadata_value in self.config.metadata.items():
            data_chunk.add_metadata(MetadataChunkData(metadata_variable, metadata_value))
        return data_chunk
