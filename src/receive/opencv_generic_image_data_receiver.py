import logging
import cv2
import numpy as np
from time import time, sleep
from src.common.timestamp import get_timestamp

from src.receive.camera_image_data_receiver import CameraImageDataReceiver
from src.common.received_image_data import ReceivedImageData
from src.common.camera_received_data_status import CameraReceivedDataStatus
from src.common.image_frame import ImageFrame
from src.common.metadata_chunk import MetadataChunk


class OpenCVGenericImageDataReceiver(CameraImageDataReceiver):

    def __init__(self):
        """
        Represents a local capturing device
        """
        super().__init__()

    def import_config(self, cfg_provider, section):
        """
        Takes parameter set from configuration and apply them to capturing device
        :return:
        """
        super().import_config(cfg_provider, section)

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

        initial_value = self.camera_object.get(par)
        if not initial_value:
            logging.warning('Parameter (' + parameter + ') is not supported by VideoCapture instance')
            return False

        backend_support = self.camera_object.set(par, requested_value)
        if not backend_support:
            logging.warning('Parameter (' + parameter + ') cannot be changed (' + str(requested_value) + ')')
            return False

        new_value = self.camera_object.get(par)
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
        self.connect()

        while not self.camera_object.isOpened():
            self.connect()
            sleep(1)

        self.camera_status.initialised = True
        logging.info('Capturing device initialised successfully')
        logging.info(self.get_details())

    def connect(self):
        try:
            self.camera_object = cv2.VideoCapture(self.cfg.device_id)
        except Exception as exc:
            logging.error('Capturing device not connected... trying again', exc_info=exc)

    def release(self):
        """
        Releases capturing device.
        :return:
        """
        if not self.camera_status.initialised:
            logging.warning('No device initialised, nothing to release')
            return

        if self.camera_object.release():
            logging.info('Captured device released successfully')
            self.camera_status.initialised = False
            self.camera_object = None
        else:
            logging.warning('Capturing device could not be released')
            self.camera_status.initialised = True

    def receive_data(self) -> (bool, np.array, int):
        """
        Captures single frame.
        :return: Tuple of three variables:
        status: bool: True - frame captured successfully, False - otherwise
        frame: np.array: Frame in the form of np.array
        timestamp: int: Unix timestamp in milliseconds
        """
        if not self.camera_status.initialised:
            self.initialise()
        if not self.camera_status.initialised:
            logging.warning('Frame NOT captured')
            timestamp = get_timestamp()
            data = None
            status = CameraReceivedDataStatus(2)
            return ReceivedImageData(timestamp, data, status)

        if self.camera_status.capturing:
            logging.warning('Frame NOT captured')
            timestamp = get_timestamp()
            data = None
            status = CameraReceivedDataStatus(1)
            return ReceivedImageData(timestamp, data, status)

        self.camera_status.capturing = True
        captured, frame_np = self.camera_object.read()
        timestamp = get_timestamp()
        self.camera_status.capturing = False

        if captured:
            logging.info('Frame captured')
            frame_colormap = 'BGR'
            data = ImageFrame(frame_np, frame_colormap)
            status = CameraReceivedDataStatus(0)
            return ReceivedImageData(timestamp, data, status)
        else:
            logging.warning('Frame NOT captured')
            data = None
            status = CameraReceivedDataStatus(99)
            return ReceivedImageData(timestamp, data, status)

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

