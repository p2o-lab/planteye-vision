from abc import ABC, abstractmethod
from src.receive.data_receiver import DataReceiver
from src.common.cfg_provider import CfgProvider


class ImageDataReceiver(DataReceiver, ABC):
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
    def import_config(self):
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

