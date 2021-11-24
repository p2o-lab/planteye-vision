from abc import ABC, abstractmethod


class DataChunkData(ABC):
    @abstractmethod
    def as_dict(self):
        pass


class DataChunkValue(DataChunkData):
    def __init__(self, name: str, value):
        self.name = name
        self.value = value

    def as_dict(self):
        return {self.name: self.value}
