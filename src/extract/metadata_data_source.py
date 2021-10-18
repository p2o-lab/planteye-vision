from abc import ABC, abstractmethod
from src.extract.data_source import DataSource
from src.common.cfg_provider import CfgProvider


class MetadataDataSource(DataSource, ABC):
    """
    This class describes generic metadata provider
    """
    @abstractmethod
    def __init__(self):
        self.cfg = None
        self.initialised = False
        self.configured = False

    @abstractmethod
    def receive_data(self):
        pass

    @abstractmethod
    def get_details(self):
        pass

    @abstractmethod
    def import_config(self, cfg_provider: CfgProvider):
        """
        Takes parameter set from configuration
        :return:
        """
        self.cfg = cfg_provider.provide_cfg()['metadata']

    @abstractmethod
    def configure(self):
        pass
