from abc import ABC, abstractmethod
import numpy as np
from src.common.data_chunk_data import DataChunkData, DataChunkValue
from src.common.metadata_chunk import MetadataChunk, MetadataChunkData
from src.common.data_chunk_status import DataChunkStatus


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
    def __init__(self):
        self.data = {}
        self.metadata = {}
        self.status = {}

    def add_data(self, data: DataChunkValue):
        self.data.update(data.as_dict())

    def add_metadata(self, metadata: MetadataChunkData):
        self.metadata.update(metadata.as_dict())

    def add_status(self, status: DataChunkStatus):
        self.status.update(status.as_dict())

    def as_dict(self):
        return {'data': self.data, 'metadata': self.metadata, 'status': self.status}
