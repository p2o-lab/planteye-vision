from abc import ABC, abstractmethod
from src.receive.image_data_receiver import ImageDataReceiver
from src.common.cfg_provider import CfgProvider
from src.common.camera_status import CameraStatus
from src.common.configuration import CameraConfiguration
from src.common.timestamp import get_timestamp
import logging
from time import time


class CameraImageDataReceiver(ImageDataReceiver):
    """
    This class describes a generic capturing device connected via OpenCV
    """

    def __init__(self):
        self.cfg = CameraConfiguration()
        self.camera_object = None
        self.camera_status = CameraStatus()

    @abstractmethod
    def receive_data(self):
        pass

    @abstractmethod
    def get_details(self):
        pass

    def import_config(self, cfg_provider, section):
        self.cfg.read(cfg_provider, section)

    def configure(self):
        configured_all_parameters = True

        for parameter, value in self.cfg.parameters.items():
            configured_all_parameters *= self.set_parameter(parameter, value)
        self.camera_status.fully_configured = configured_all_parameters
        self.camera_status.configured = True

    @abstractmethod
    def initialise(self):
        pass

    @abstractmethod
    def get_configuration(self):
        pass

    def get_status(self):
        return self.camera_status.as_dict()

    @abstractmethod
    def set_parameter(self, parameter, value):
        pass

