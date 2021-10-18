import logging
import numpy as np
import neoapi
from time import time, sleep

from src.extract.camera_image_data_provider import CameraImageDataSource

GET_IMAGE_TIMEOUT = 1000


class NeoApiImageDataSource(CameraImageDataSource):
    def __init__(self, cfg: dict):
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
        self.camera.SetSynchronFeatureMode(True)

    def set_parameter(self, feature: str, requested_value) -> bool:
        """
        Sets a single parameter of the Baumer camera.
        :param feature: str: Feature name according to neoAPI documentation.
        List of available features and their description is to find in neoAPI and camera documentation.
        Please consider that not every capturing device supports all parameters.
        :param: requested_value: any type: Desired value of the feature
        :return: bool: True if the feature is set successfully, False - if not
        """

        if not self.camera.HasFeature(feature):
            logging.warning('Feature %s not detected' % feature)
            return False
        else:
            logging.info('Feature %s detected' % feature)

        if not self.camera.IsWritable(feature):
            logging.warning('Feature %s not available' % feature)
            return False
        else:
            logging.info('Feature %s writable' % feature)

        try:
            self.camera.SetFeature(feature, requested_value)
            new_value = str(self.camera.GetFeature(feature))
            logging.info('Feature %s set to %s' % (feature, new_value))
            return True
        except neoapi.FeatureAccessException as exc:
            logging.warning('Feature %s cannot be set to %s due to %s' % (feature, requested_value, exc))
            return False

    def initialise(self):
        """
        Initialises capturing device.
        :return:
        """
        self.camera = neoapi.Cam()

        while not self.camera.IsConnected():
            self.connect()
            sleep(1)

        self.initialised = True
        logging.info('Capturing device initialised successfully')
        logging.info(self.get_details())

    def get_details(self):
        if not self.camera.IsConnected():
            return {}
        return {
            'id': neoapi.CamInfo().GetId(),
            'model_name': neoapi.CamInfo().GetModelName(),
            'serial_number': neoapi.CamInfo().GetSerialNumber(),
            'vendor_name': neoapi.CamInfo().GetVendorName(),
        }

    def get_configuration(self):
        if not self.camera.IsConnected():
            return {}
        return {f.GetName(): f.GetValue() for f in neoapi.FeatureList}

    def connect(self):
        try:
            self.camera.Connect(self.cfg['connection']['device_id'])
        except neoapi.NotConnectedException as exc:
            logging.error('Capturing device not connected... trying again', exc_info=exc)
        except neoapi.NoAccessException as exc:
            logging.error('Capturing device not connected... trying again', exc_info=exc)

    def receive_data(self) -> (bool, np.array, int):
        """
        Captures single frame and returns it as a numpy array
        :return: Tuple of three variables:
        status: dict: Status in a json format as a python dict
        frame: np.array: Frame in the form of np.array
        timestamp: int: Unix timestamp in milliseconds
        """
        if self.capturing:
            status = {'code': 500, 'message': 'Capturing device busy'}
            return status, None, int(round(time() * 1000))

        if not self.camera.IsConnected():
            self.connect()

        if not self.camera.IsConnected():
            status = {'code': 500, 'message': 'Connection to capturing device cannot be established'}
            return status, None, int(round(time() * 1000))

        self.capturing = True
        frame_raw = self.camera.GetImage(GET_IMAGE_TIMEOUT)
        timestamp = int(round(time() * 1000))
        self.capturing = False

        frame_shape = frame_raw.shape
        frame_colormap = 'BGR'
        frame = {'frame': frame_raw.GetNPArray(), 'frame_shape': frame_shape, 'frame_colormap': frame_colormap}

        if frame_raw.IsEmpty():
            status = {'code': 500, 'message': 'Error capturing frame'}
            return status, None, timestamp

        logging.info('Frame captured')
        status = {'code': 200, 'message': 'Frame captured'}
        return status, frame, timestamp

    def get_status(self) -> dict:
        """
        Gets status of capturing device including whether the device initialised or not, is currently capturing or idle
        along with unix timestamp in milliseconds.
        :return: dict: Status in form of {'status: {'connected': Value, 'capturing': Value}, 'timestamp': Value}
        """
        if self.camera.IsConnected():
            msg = 'camera connected'
        else:
            msg = 'camera not connected'
        connection_status = {'status': self.camera.IsConnected(), 'message': msg}

        if self.capturing:
            msg = 'camera capturing'
        else:
            msg = 'camera idle'
        capturing_status = {'status': self.capturing, 'message': msg}

        return {'status': {'connected': connection_status,
                           'capturing': capturing_status},
                'timestamp': int(round(time() * 1000))}
