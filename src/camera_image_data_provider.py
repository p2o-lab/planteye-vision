from abc import ABC, abstractmethod
from src.image_data_provider import ImageDataProvider
from src.cfg_provider import CfgProvider
import logging
from time import time


class CameraImageDataProvider(ImageDataProvider, ABC):
    """
    This class describes generic capturing device
    """

    @abstractmethod
    def __init__(self):
        self.__cfg = None
        self.__camera = None
        self.__initialised = False
        self.__configured = False
        self.__configure_all_parameters = False
        self.__connected = False
        self.__capturing = False

    @abstractmethod
    def provide_data(self):
        pass

    @abstractmethod
    def get_data_source_details(self):
        pass

    @abstractmethod
    def configure(self, cfg_provider: CfgProvider):
        """
        Takes parameter set from configuration and apply them to capturing device
        :return:
        """

        self.__cfg = cfg_provider.provide_cfg()
        configured_all_parameters = True

        for parameter, value in self.__cfg['parameters'].items():
            configured_all_parameters *= self.set_parameter(parameter, value)

        if configured_all_parameters:
            logging.info('All parameters set to successfully')
        else:
            logging.warning('At least one parameter not set')
        self.__configure_all_parameters = configured_all_parameters
        self.__configured = True

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
        if self.__initialised:
            msg = 'camera initialised'
        else:
            msg = 'camera not initialised'
        initialisation_status = {'status': self.__initialised, 'message': msg}

        if self.__capturing:
            msg = 'camera capturing'
        else:
            msg = 'camera idle'
        capturing_status = {'status': self.__capturing, 'message': msg}

        return {'status': {'initialised': initialisation_status,
                           'capturing': capturing_status},
                'timestamp': int(round(time() * 1000))}

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def set_parameter(self, parameter, value):
        pass

