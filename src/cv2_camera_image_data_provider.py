import logging
import cv2
import numpy as np
from time import time

from src.camera_image_data_provider import CameraImageDataProvider


class CV2CameraImageDataProvider(CameraImageDataProvider):

    def __init__(self):
        """
        Represents a local capturing device
        """
        super().__init__()

    def configure(self, cfg_provider):
        """
        Takes parameter set from configuration and apply them to capturing device
        :return:
        """
        super().configure(cfg_provider)

    def set_parameter(self, parameter: str, requested_value: object) -> bool:
        """
        Sets a single parameter of capturing device.
        :param parameter: str: Parameter identificator of VideoCaptureProperties from OpenCV.
        List of available parameters and their description is to find on
        on https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html
        Please consider that not every capturing device supports all parameters.
        :param requested_value: any type: Desired value of the parameter
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

    def initialise(self):
        """
        Initialises capturing device.
        :return:
        """
        self.__camera = cv2.VideoCapture(self.__cfg['connection']['device_id'])
        if self.__camera.isOpened():
            logging.info('Capturing device initialised successfully')
            self.__initialised = True
        else:
            logging.error('Capturing device initialisation failed')
            self.__initialised = False

    def release(self):
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

    def provide_data(self) -> (bool, np.array, int):
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
            self.initialise()

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

    def get_configuration(self):
        return {}

    def get_status(self) -> dict:
        return super().get_status()

    def get_data_source_details(self):
        return {
            'id': 'no data',
            'model_name': 'generic',
            'serial_number': 'no data',
            'vendor_name': 'generic',
        }

