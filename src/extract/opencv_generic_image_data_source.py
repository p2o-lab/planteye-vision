import logging
import cv2
import numpy as np
from time import time, sleep

from src.extract.camera_image_data_provider import CameraImageDataSource


class OpenCVGenericImageDataSource(CameraImageDataSource):

    def __init__(self):
        """
        Represents a local capturing device
        """
        super().__init__()

    def import_config(self, cfg_provider):
        """
        Takes parameter set from configuration and apply them to capturing device
        :return:
        """
        super().import_config(cfg_provider)

    def configure(self):
        """
        Takes parameter set from configuration and apply them to capturing device
        :return:
        """
        super().configure()

    def set_parameter(self, parameter: str, requested_value: object) -> bool:
        """
        Sets a single parameter of capturing device.
        :param parameter: str: Parameter identificator of VideoCaptureProperties from OpenCV.
        List of available parameters and their description is to find on
        on https://docs.opencv.org/3.4/d4/d15/groupvideoioflagsbase.html
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

        initial_value = self.camera.get(par)
        if not initial_value:
            logging.warning('Parameter (' + parameter + ') is not supported by VideoCapture instance')
            return False

        backend_support = self.camera.set(par, requested_value)
        if not backend_support:
            logging.warning('Parameter (' + parameter + ') cannot be changed (' + str(requested_value) + ')')
            return False

        new_value = self.camera.get(par)
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

        self.camera = cv2.VideoCapture(self.cfg['connection']['device_id'])

        while not self.camera.isOpened():
            self.connect()
            sleep(1)

        self.initialised = True
        logging.info('Capturing device initialised successfully')
        logging.info(self.get_details())

    def connect(self):
        try:
            self.camera = cv2.VideoCapture(self.cfg['connection']['device_id'])
        except Exception as exc:
            logging.error('Capturing device not connected... trying again', exc_info=exc)

    def release(self):
        """
        Releases capturing device.
        :return:
        """
        if not self.initialised:
            logging.warning('No device initialised, nothing to release')
            return

        if self.camera.release():
            logging.info('Captured device released successfully')
            self.initialised = False
            self.camera = None
        else:
            logging.warning('Capturing device could not be released')
            self.initialised = True

    def receive_data(self) -> (bool, np.array, int):
        """
        Captures single frame.
        :return: Tuple of three variables:
        status: bool: True - frame captured successfully, False - otherwise
        frame: np.array: Frame in the form of np.array
        timestamp: int: Unix timestamp in milliseconds
        """
        if self.capturing:
            status = {'code': 500, 'message': 'Capturing device busy'}
            return status, None, int(round(time() * 1000))

        if not self.initialised:
            self.initialise()

        if not self.initialised:
            status = {'code': 500, 'message': 'Capturing device could not be initialised'}
            return status, None, int(round(time() * 1000))

        self.capturing = True
        captured, frame_np = self.camera.read()
        timestamp = int(round(time() * 1000))
        self.capturing = False

        frame_shape = frame_np.shape
        frame_colormap = 'BGR'
        frame = {'frame': frame_np, 'frame_shape': frame_shape, 'frame_colormap': frame_colormap}

        if captured:
            logging.info('Frame captured')
            status = {'code': 200, 'message': 'Frame captured'}
            return status, frame, timestamp
        else:
            status = {'code': 500, 'message': 'Error capturing frame'}
            return status, None, timestamp

    def get_configuration(self):
        return {}

    def get_status(self) -> dict:
        return super().get_status()

    def get_details(self):
        return {
            'id': self.cfg['connection']['device_id'],
            'model_name': 'Generic OpenCV camera',
            'serial_number': 'no data',
            'vendor_name': 'no data',
        }

