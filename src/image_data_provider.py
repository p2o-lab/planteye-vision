from abc import ABC, abstractmethod
from src.data_provider import DataProvider
from src.cfg_provider import CfgProvider


class ImageDataProvider(DataProvider, ABC):
    """
    This class describes generic capturing device
    """

    @abstractmethod
    def provide_data(self):
        pass

    @abstractmethod
    def get_data_source_details(self):
        pass

    @abstractmethod
    def configure(self, cfg_provider: CfgProvider):
        pass

    @abstractmethod
    def initialise(self):
        pass

    @abstractmethod
    def get_configuration(self):
        pass

    @abstractmethod
    def get_status(self):
        pass

