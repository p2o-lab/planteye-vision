from abc import ABC, abstractmethod


class MetadataChunk(ABC):
    @abstractmethod
    def as_dict(self):
        pass


class MetadataChunkData(MetadataChunk):
    def __init__(self, name: str, value):
        self.name = name
        self.value = value

    def as_dict(self):
        return {self.name: {'parameter': self.name, 'value': self.value}}
