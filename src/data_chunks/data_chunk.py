from abc import ABC, abstractmethod
from src.data_chunks.data_chunk_data import DataChunkData
from src.data_chunks.metadata_chunk import MetadataChunk, MetadataChunkData
from src.data_chunks.data_chunk_status import DataChunkStatus


class DataChunk(ABC):
    @abstractmethod
    def add_data(self, data: DataChunkData):
        pass

    @abstractmethod
    def add_metadata(self, metadata: MetadataChunk):
        pass

    @abstractmethod
    def add_status(self, status: DataChunkStatus):
        pass

    @abstractmethod
    def as_dict(self):
        pass


class GeneralDataChunk(DataChunk):
    def __init__(self, name, type, access_data):
        self.name = name
        self.type = type
        self.data = []
        self.metadata = []
        self.status = []
        self.access_data = access_data

    def add_data(self, data_chunk: DataChunkData):
        self.data.append(data_chunk)

    def add_metadata(self, metadata_chunk: MetadataChunkData):
        self.metadata.append(metadata_chunk)

    def add_status(self, status_chunk: DataChunkStatus):
        self.status.append(status_chunk)

    def as_dict(self):
        data_dict = {}
        for data_chunk in self.data:
            data_dict.update(data_chunk.as_dict())

        metadata_dict = {}
        for metadata_chunk in self.metadata:
            metadata_dict.update(metadata_chunk.as_dict())

        status_dict = {}
        for status_chunk in self.status:
            status_dict.update(status_chunk.as_dict())

        return {'inlet_type': self.type, 'inlet_name': self.name, 'inlet_access_data': self.access_data, 'data': data_dict, 'metadata': metadata_dict, 'status': status_dict}
