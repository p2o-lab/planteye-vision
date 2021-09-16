import logging
import cv2
import numpy as np
from time import time

from src.capturing_device import CapturingDevice


class CapturingDeviceLocalCamera(CapturingDevice):
    def __init__(self, cfg: dict):
        """
        Represents a local capturing device
        :param cfg: dict: Configuration
        """
        self.__cfg = cfg
        self.__camera = None
        self.__initialised = False
        self.__configured = False
        self.__connected = False
        self.__capturing = False

        self.__initialise()
        self.__configure()

    def __configure(self):
        """
        Takes parameter set from configuration and apply them to capturing device
        :return:
        """
        configured = True
        for parameter, value in self.__cfg['capturing_device']['parameters'].items():
            configured *= self.__set_parameter(parameter, value)

        if configured:
            logging.info('All parameters set to successfully')
        else:
            logging.warning('At least one parameter not set')
        self.__configured = configured

    def __set_parameter(self, parameter: str, requested_value: object) -> bool:
        """
        Sets a single parameter of capturing device.
        :param parameter: str: Parameter identificator of VideoCaptureProperties from OpenCV.
        List of available parameters and their description is to find on
        on https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html
        Please consider that not every capturing device supports all parameters.
        :param: any type: requested_value: Desired value of the parameter
        :return: bool: True if the parameter is set successfully, False - if not
        """
        par = None
        try:
            exec("par = cv2.%s" % parameter)
        except Exception:
            logging.warning('Parameter (' + parameter + ') is not found by name')
            return False

        initial_value = self.__camera.get(par)
        if not initial_value:
            logging.warning('Parameter (' + parameter + ') is not supported by VideoCapture instance')
            return False

        backend_support = self.__camera.set(par, requested_value)
        if not backend_support:
            logging.warning('Parameter (' + parameter + ') cannot be changed (' + str(requested_value) + ')')
            return False

        new_value = self.__camera.get(par)
        if new_value == requested_value:
            logging.info('Parameter (' + parameter + ') set to ' + str(new_value))
            return True
        else:
            logging.warning('Setting parameter (' + parameter + ') unsuccessful. Actual value ' + str(new_value))
            return False

    def __initialise(self):
        """
        Initialises capturing device.
        :return:
        """
        self.__camera = cv2.VideoCapture(self.__cfg['capturing_device']['connection']['device_id'])
        if self.__camera.isOpened():
            logging.info('Capturing device initialised successfully')
            self.__initialised = True
        else:
            logging.error('Capturing device initialisation failed')
            self.__initialised = False

    def __release(self):
        """
        Releases capturing device.
        :return:
        """
        if not self.__initialised:
            logging.warning('No device initialised, nothing to release')
            return

        if self.__camera.release():
            logging.info('Captured device released successfully')
            self.__initialised = False
            self.__camera = None
        else:
            logging.warning('Capturing device could not be released')
            self.__initialised = True

    def capture_frame(self) -> (bool, np.array, int):
        """
        Captures single frame.
        :return: Tuple of three variables:
        status: bool: True - frame captured successfully, False - otherwise
        frame: np.array: Frame in the form of np.array
        timestamp: int: Unix timestamp in milliseconds
        """
        if self.__capturing:
            status = {'code': 500, 'message': 'Capturing device busy'}
            return status, None, int(round(time() * 1000))

        if not self.__initialised:
            self.__initialise()

        if not self.__initialised:
            status = {'code': 500, 'message': 'Capturing device could not be initialised'}
            return status, None, int(round(time() * 1000))

        self.__capturing = True
        captured, frame_raw = self.__camera.read()
        timestamp = int(round(time() * 1000))
        self.__capturing = False

        if captured:
            logging.info('Frame captured')
            status = {'code': 200, 'message': 'Frame captured'}
            return status, frame_raw, timestamp
        else:
            status = {'code': 500, 'message': 'Error capturing frame'}
            return status, None, timestamp

    def get_status(self) -> dict:
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
