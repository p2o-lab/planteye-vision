import neoapi
import logging
from time import sleep
from planteye_vision.inlet.camera_inlet import CameraInlet
from planteye_vision.common.timestamp import get_timestamp
from planteye_vision.data_chunks.data_chunk import GeneralDataChunk
from planteye_vision.data_chunks.data_chunk_status import CapturingStatus
from planteye_vision.data_chunks.metadata_chunk import MetadataChunkData
from planteye_vision.data_chunks.data_chunk_data import DataChunkImage
from planteye_vision.configuration.inlet_configuration import CameraConfiguration
import numpy as np


GET_IMAGE_TIMEOUT = 1000
DEBUG = False


class BaumerCameraInlet(CameraInlet):

    def __init__(self, config: CameraConfiguration):
        super().__init__(config)
        self.camera_status.initialised = False
        self.current_frame = None

    def __del__(self):
        if self.camera_object is not None:
            self.disconnect()

    def apply_configuration(self):
        if not DEBUG:
            self.connect()
            self.camera_object.SetSynchronFeatureMode(True)
        super().apply_configuration()

    def set_parameter(self, parameter: str, requested_value: object) -> bool:
        """
        Sets a single parameter of the Baumer camera.
        :param parameter: str: Feature name according to neoAPI documentation.
        List of available features and their description is to find in neoAPI and camera documentation.
        Please consider that not every capturing device supports all parameters.
        :param: requested_value: any type: Desired value of the feature
        :return: bool: True if the feature is set successfully, False - if not
        """
        if DEBUG:
            logging.info('Parameter (' + parameter + ') is set to ' + str(requested_value))
            return True

        if not self.camera_object.HasFeature(parameter):
            logging.warning('Feature %s not detected' % parameter)
            return False
        else:
            logging.debug('Feature %s detected' % parameter)

        if not self.camera_object.IsWritable(parameter):
            logging.warning('Feature %s not available' % parameter)
            return False
        else:
            logging.debug('Feature %s writable' % parameter)

        try:
            self.camera_object.SetFeature(parameter, requested_value)
            new_value = str(self.camera_object.GetFeature(parameter).value)
            logging.info('Feature %s set to %s' % (parameter, new_value))
            return True
        except neoapi.FeatureAccessException as exc:
            logging.warning('Feature %s cannot be set to %s due to %s' % (parameter, requested_value, exc))
            return False

    def connect(self):
        if DEBUG:
            print('Connect')
            self.camera_status.initialised = True
            return True

        self.camera_object = neoapi.Cam()
        self.camera_status.initialised = False
        while not self.camera_object.IsConnected():
            self._connect_attempt()
            sleep(1)

        self.camera_status.initialised = True
        logging.info('Capturing device initialised successfully')
        logging.info(self.get_details())

    def _connect_attempt(self):
        logging.debug('Trying to connect to capturing device...')
        try:
            self.camera_object.Connect()
        except neoapi.NotConnectedException as exc:
            logging.error('Capturing device not connected... trying again', exc_info=exc)
        except neoapi.NoAccessException as exc:
            logging.error('Capturing device not connected... trying again', exc_info=exc)

    def disconnect(self):
        if not self.camera_status.initialised:
            logging.warning('No device initialised, nothing to release')
            return

        self.camera_object = None
        logging.debug('Captured device released')
        self.camera_status.initialised = True

    def retrieve_data(self):
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.parameters, hidden=self.config.hidden)

        if not self.config.is_valid():
            status = CapturingStatus(100)
            data_chunk.add_status(status)
            logging.error('Step %s : No execution due to invalid configuration' % self.name)
            return [data_chunk]

        if not self.camera_status.initialised:
            self.connect()

        timestamp = MetadataChunkData('timestamp', get_timestamp())
        data_chunk.add_metadata(timestamp)

        camera_configuration = self.get_configuration()
        for feature_name, feature_value in camera_configuration.items():
            feature_metadata_chunk = MetadataChunkData(feature_name, feature_value)
            data_chunk.add_metadata(feature_metadata_chunk)

        if not self.camera_status.initialised:
            status = CapturingStatus(1)
            data_chunk.add_status(status)
            logging.warning(status.get_message())
            self.camera_status.initialised = False
            return [data_chunk]

        if self.camera_status.capturing:
            if self.current_frame:
                frame_raw = True
                frame_np = self.current_frame
            else:
                status = CapturingStatus(2)
                data_chunk.add_status(status)
                logging.warning(status.get_message())
                self.camera_status.initialised = False
                return [data_chunk]
        else:
            self.camera_status.capturing = True
            if DEBUG:
                self.camera_status.initialised = True
                frame_raw = True
                frame_np = np.random.rand(2500, 2500, 3)
            else:
                frame_raw = self.camera_object.GetImage(GET_IMAGE_TIMEOUT)
                frame_np = frame_raw.GetNPArray()
                self.current_frame = frame_np
            self.camera_status.capturing = False

        if frame_raw is None:
            status = CapturingStatus(99)
            data_chunk.add_status(status)
            logging.warning(status.get_message())
            self.camera_status.initialised = False
            return [data_chunk]

        data_chunk.add_data(DataChunkImage('frame', frame_np, 'base64_png'))

        status = CapturingStatus(0)
        data_chunk.add_status(status)
        logging.warning(status.get_message())

        data_chunk.add_metadata(MetadataChunkData('colormap', self.get_pixel_format()))
        data_chunk.add_metadata(MetadataChunkData('shape', frame_np.shape))
        for metadata_variable, metadata_value in self.config.metadata.items():
            data_chunk.add_metadata(MetadataChunkData(metadata_variable, metadata_value))
        return [data_chunk]

    def execute(self):
        return super().execute()

    def get_details(self):
        if not self.camera_object.IsConnected():
            return {}
        return {
            'model': self.camera_object.f.DeviceModelName.value
        }

    def get_configuration(self):
        if not self.camera_object.IsConnected():
            return {}
        feature_list = ['ExposureAuto', 'ExposureTime', 'Gain', 'GainAuto', 'Gamma',
                        'Width', 'Height', 'OffsetX', 'OffsetY', 'BalanceWhiteAuto', 'PixelFormat']
        feature_dict = {}
        for f_name in feature_list:
            feature_dict[f_name] = eval(f"self.camera_object.f.{f_name}.value")
        return feature_dict

    def get_pixel_format(self):
        if not self.camera_object.IsConnected():
            return None
        try:
            return self.camera_object.f.PixelFormat.value
        except Exception as exc:
            return None
