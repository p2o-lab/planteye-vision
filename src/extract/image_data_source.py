from abc import ABC, abstractmethod
from src.extract.data_source import DataSource
from src.common.cfg_provider import CfgProvider


class ImageDataSource(DataSource, ABC):
    """
    This class describes generic capturing device
    """

    @abstractmethod
    def receive_data(self):
        pass

    @abstractmethod
    def get_details(self):
        pass

    @abstractmethod
    def import_config(self, cfg_provider: CfgProvider):
        pass

    @abstractmethod
    def configure(self):
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

