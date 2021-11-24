from abc import ABC, abstractmethod
from src.receive.data_receiver import DataReceiver
from src.common.cfg_provider import CfgProvider


class MetadataDataReceiver(DataReceiver, ABC):
    """
    This class describes generic metadata provider
    """
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

    def import_config(self, cfg_provider: CfgProvider):
        """
        Takes parameter set from configuration
        :return:
        """
        self.cfg = cfg_provider.provide_cfg()['metadata']

    @abstractmethod
    def configure(self):
        pass
