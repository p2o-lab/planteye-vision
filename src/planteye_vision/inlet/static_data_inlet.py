from planteye_vision.inlet.inlet import Inlet
from planteye_vision.configuration.inlet_configuration import StaticValueConfiguration
from planteye_vision.data_chunks.data_chunk import GeneralDataChunk
from planteye_vision.data_chunks.data_chunk_data import DataChunkValue
from planteye_vision.data_chunks.metadata_chunk import MetadataChunkData


class StaticDataInlet(Inlet):
    """
    This class describes a static data inlet
    """
    def __init__(self, config: StaticValueConfiguration):
        self.config = config
        self.name = None
        self.type = None

    def apply_configuration(self):
        self.name = self.config.name
        self.type = self.config.type

    def retrieve_data(self):
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.parameters, hidden=self.config.hidden)
        data_type = 'diverse'
        data_chunk.add_data(DataChunkValue('static_value', self.config.parameters['value'], data_type))
        for metadata_variable, metadata_value in self.config.metadata.items():
            data_chunk.add_metadata(MetadataChunkData(metadata_variable, metadata_value))
        return [data_chunk]

    def execute(self):
        return super().execute()
