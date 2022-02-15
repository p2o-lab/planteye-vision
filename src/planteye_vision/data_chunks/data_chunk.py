from abc import ABC, abstractmethod
from planteye_vision.data_chunks.data_chunk_data import DataChunkData
from planteye_vision.data_chunks.metadata_chunk import MetadataChunk, MetadataChunkData
from planteye_vision.data_chunks.data_chunk_status import DataChunkStatus


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
    def __init__(self, name: str, chunk_type: str, parameters: dict, hidden: bool = False):
        self.name = name
        self.chunk_type = chunk_type
        self.hidden = hidden
        self.parameters = parameters
        self.data = []
        self.metadata = []
        self.status = []

    def add_data(self, data_chunk: DataChunkData):
        self.data.append(data_chunk)

    def add_metadata(self, metadata_chunk: MetadataChunkData):
        self.metadata.append(metadata_chunk)

    def add_status(self, status_chunk: DataChunkStatus):
        self.status.append(status_chunk)

    def as_dict(self):
        data_dict = {}
        for data_chunk in self.data:
            data_dict.update({data_chunk.name: data_chunk.as_dict()})

        metadata_dict = {}
        for metadata_chunk in self.metadata:
            metadata_dict.update(metadata_chunk.as_dict())

        status_dict = {}
        for status_chunk in self.status:
            status_dict.update(status_chunk.as_dict())

        return {'type': self.chunk_type, 'name': self.name, 'parameters': self.parameters, 'data': data_dict,
                'metadata': metadata_dict, 'status': status_dict}
