import logging
import numpy as np
import neoapi
from time import time, sleep

from src.capturing_device import CapturingDevice

GET_IMAGE_TIMEOUT = 1000


class CapturingDeviceBaumerVAX(CapturingDevice):
    def __init__(self, cfg: dict):
        """
        Represents a local capturing device
        :param cfg: dict: Configuration
        """
        self.__cfg = cfg
        self.__camera = None
        self.__configured = False
        self.__capturing = False

        self.__initialise()
        self.__configure()

    def __configure(self):
        """
        Takes parameter set from configuration and apply them to capturing device
        :return:
        """
        configured = True
        self.__camera.SetSynchronFeatureMode(True)
        for feature, value in self.__cfg['capturing_device']['parameters'].items():
            configured *= self.__set_parameter(feature, value)

        if configured:
            logging.info('All parameters set to successfully')
        else:
            logging.warning('At least one parameter not set')
        self.__configured = configured

    def __set_parameter(self, feature: str, requested_value: object) -> bool:
        """
        Sets a single parameter of the Baumer camera.
        :param feature: str: Feature name according to neoAPI documentation.
        List of available features and their description is to find in neoAPI and camera documentation.
        Please consider that not every capturing device supports all parameters.
        :param: any type: requested_value: Desired value of the feature
        :return: bool: True if the feature is set successfully, False - if not
        """

        if not self.__camera.HasFeature(feature):
            logging.warning('Feature %s not detected' % feature)
            return False
        else:
            logging.info('Feature %s detected' % feature)

        if not self.__camera.IsWritable(feature):
            logging.warning('Feature %s not available' % feature)
            return False
        else:
            logging.info('Feature %s writable' % feature)

        try:
            self.__camera.SetFeature(feature, requested_value)
            new_value = str(self.__camera.GetFeature(feature))
            logging.info('Feature %s set to %s' % (feature, new_value))
            return True
        except neoapi.FeatureAccessException as exc:
            logging.warning('Feature %s cannot be set to %s due to %s' % (feature, requested_value, exc))
            return False

    def __initialise(self):
        """
        Initialises capturing device.
        :return:
        """
        self.__camera = neoapi.Cam()

        while not self.__camera.IsConnected():
            self.__connect()
            sleep(1)

        logging.info('Capturing device initialised successfully')
        logging.info(self.get_camera_details())

    def get_camera_details(self):
        if not self.__camera.IsConnected():
            return {}
        return {
            'id': self.__camera.GetId(),
            'model_name': self.__camera.GetModelName(),
            'serial_number': self.__camera.GetSerialNumber(),
            'vendor_name': self.__camera.GetVendorName(),
        }

    def get_camera_configuration(self):
        if not self.__camera.IsConnected():
            return {}
        return {f.GetName(): f.GetValue() for f in neoapi.FeatureList}

    def __connect(self):
        try:
            self.__camera.Connect(self.__cfg['capturing_device']['connection']['device_id'])
        except neoapi.NotConnectedException:
            logging.error('Capturing device not connected... trying again')

    def capture_frame(self) -> (bool, np.array, int):
        """
        Captures single frame and returns it as a numpy array
        :return: Tuple of three variables:
        status: dict: Status in a json format as a python dict
        frame: np.array: Frame in the form of np.array
        timestamp: int: Unix timestamp in milliseconds
        """
        if self.__capturing:
            status = {'code': 500, 'message': 'Capturing device busy'}
            return status, None, int(round(time() * 1000))

        if not self.__camera.IsConnected():
            self.__connect()

        if not self.__camera.IsConnected():
            status = {'code': 500, 'message': 'Connection to capturing device cannot be established'}
            return status, None, int(round(time() * 1000))

        self.__capturing = True
        frame_raw = self.__camera.GetImage(GET_IMAGE_TIMEOUT)
        self.__capturing = False
        timestamp = int(round(time() * 1000))

        if frame_raw.IsEmpty():
            status = {'code': 500, 'message': 'Error capturing frame'}
            return status, None, timestamp

        logging.info('Frame captured')
        status = {'code': 200, 'message': 'Frame captured'}
        return status, frame_raw.GetNPArray(), timestamp

    def get_status(self) -> dict:
        """
        Gets status of capturing device including whether the device initialised or not, is currently capturing or idle
        along with unix timestamp in milliseconds.
        :return: dict: Status in form of {'status: {'connected': Value, 'capturing': Value}, 'timestamp': Value}
        """
        if self.__camera.IsConnected():
            msg = 'camera connected'
        else:
            msg = 'camera not connected'
        connection_status = {'status': self.__camera.IsConnected(), 'message': msg}

        if self.__capturing:
            msg = 'camera capturing'
        else:
            msg = 'camera idle'
        capturing_status = {'status': self.__capturing, 'message': msg}

        return {'status': {'connected': connection_status,
                           'capturing': capturing_status},
                'timestamp': int(round(time() * 1000))}
