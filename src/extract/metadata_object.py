from abc import ABC, abstractmethod


class MetadataObject(ABC):
    """
    This class describes generic metadata provider
    """
    @abstractmethod
    def __init__(self, item_name, item_dict):
        self.item_name = item_name
        self.item_dict = item_dict

    @abstractmethod
    def receive_data(self):
        pass

    @abstractmethod
    def get_source_type(self):
        return self.item_dict['source']
