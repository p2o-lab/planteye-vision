from abc import ABC, abstractmethod
from src.extract.image_data_source import ImageDataSource
from src.common.cfg_provider import CfgProvider
import logging
from time import time


class CameraImageDataSource(ImageDataSource, ABC):
    """
    This class describes generic capturing device
    """

    @abstractmethod
    def __init__(self):
        self.cfg = None
        self.camera = None
        self.initialised = False
        self.configured = False
        self.configure_all_parameters = False
        self.connected = False
        self.capturing = False

    @abstractmethod
    def receive_data(self):
        pass

    @abstractmethod
    def get_details(self):
        pass

    @abstractmethod
    def import_config(self, cfg_provider: CfgProvider):
        """
        Takes parameter set from configuration and apply them to capturing device
        :return:
        """
        self.cfg = cfg_provider.provide_cfg()['data_source']

    @abstractmethod
    def configure(self):
        configured_all_parameters = True

        for parameter, value in self.cfg['parameters'].items():
            configured_all_parameters *= self.set_parameter(parameter, value)

        if configured_all_parameters:
            logging.info('All parameters set to successfully')
        else:
            logging.warning('At least one parameter not set')
        self.configure_all_parameters = configured_all_parameters
        self.configured = True

    @abstractmethod
    def initialise(self):
        pass

    @abstractmethod
    def get_configuration(self):
        pass

    @abstractmethod
    def get_status(self):
        """
        Gets status of capturing device including whether the device initialised or not, is currently capturing or idle
        along with unix timestamp in milliseconds.
        :return: dict: Status in form of {'status: {'initialised': Value, 'capturing': Value}, 'timestamp': Value}
        """
        if self.initialised:
            msg = 'camera initialised'
        else:
            msg = 'camera not initialised'
        initialisation_status = {'status': self.initialised, 'message': msg}

        if self.capturing:
            msg = 'camera capturing'
        else:
            msg = 'camera idle'
        capturing_status = {'status': self.capturing, 'message': msg}

        return {'status': {'initialised': initialisation_status,
                           'capturing': capturing_status},
                'timestamp': int(round(time() * 1000))}

    @abstractmethod
    def set_parameter(self, parameter, value):
        pass

