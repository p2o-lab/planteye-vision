import logging
import numpy as np
import neoapi
from time import time, sleep

import logging
from time import sleep
import cv2

from src.inlet.camera_inlet import CameraInlet
from src.common.timestamp import get_timestamp
from src.data_chunks.data_chunk import GeneralDataChunk
from src.data_chunks.data_chunk_status import CapturingStatus
from src.data_chunks.metadata_chunk import MetadataChunkData
from src.data_chunks.data_chunk_data import DataChunkImage
from src.configuration.inlet_configuration import CameraConfiguration

GET_IMAGE_TIMEOUT = 1000


class NeoApiImageDataReceiver(CameraInlet):

    def __init__(self, config: CameraConfiguration):
        super().__init__(config)
        self.camera_status.initialised = False

    def __del__(self):
        if self.camera_object is not None:
            self.disconnect()

    def apply_configuration(self):
        self.camera_object.SetSynchronFeatureMode(True)
        super().apply_configuration()

    def set_parameter(self, feature: str, requested_value) -> bool:
        """
        Sets a single parameter of the Baumer camera.
        :param feature: str: Feature name according to neoAPI documentation.
        List of available features and their description is to find in neoAPI and camera documentation.
        Please consider that not every capturing device supports all parameters.
        :param: requested_value: any type: Desired value of the feature
        :return: bool: True if the feature is set successfully, False - if not
        """

        if not self.camera_object.HasFeature(feature):
            logging.warning('Feature %s not detected' % feature)
            return False
        else:
            logging.info('Feature %s detected' % feature)

        if not self.camera_object.IsWritable(feature):
            logging.warning('Feature %s not available' % feature)
            return False
        else:
            logging.info('Feature %s writable' % feature)

        try:
            self.camera_object.SetFeature(feature, requested_value)
            new_value = str(self.camera_object.GetFeature(feature))
            logging.info('Feature %s set to %s' % (feature, new_value))
            return True
        except neoapi.FeatureAccessException as exc:
            logging.warning('Feature %s cannot be set to %s due to %s' % (feature, requested_value, exc))
            return False

    def connect(self):
        self.camera_object = neoapi.Cam()
        self.camera_status.initialised = False
        while not self.camera_object.IsConnected():
            self._connect_attempt()
            sleep(1)

        self.camera_status.initialised = True
        logging.info('Capturing device initialised successfully')
        logging.info(self.get_details())

    def _connect_attempt(self):
        logging.info('Trying to connect to capturing device...')
        try:
            self.camera_object.Connect(self.config.parameters['device_id'])
        except neoapi.NotConnectedException as exc:
            logging.error('Capturing device not connected... trying again', exc_info=exc)
        except neoapi.NoAccessException as exc:
            logging.error('Capturing device not connected... trying again', exc_info=exc)

    def disconnect(self):
        if not self.camera_status.initialised:
            logging.warning('No device initialised, nothing to release')
            return

        self.camera_object = None
        logging.info('Captured device released')
        self.camera_status.initialised = True

    def retrieve_data(self):
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.parameters, hidden=self.config.hidden)

        if not self.config.is_valid():
            status = CapturingStatus(100)
            data_chunk.add_status(status)
            print('Step %s : No execution due to invalid configuration' % self.name)
            return [data_chunk]

        if not self.camera_status.initialised:
            self.connect()

        timestamp = MetadataChunkData('timestamp', get_timestamp())
        data_chunk.add_metadata(timestamp)

        if not self.camera_status.initialised:
            status = CapturingStatus(1)
            data_chunk.add_status(status)
            logging.warning(status.get_message())
            self.camera_status.initialised = False
            return [data_chunk]

        if self.camera_status.capturing:
            status = CapturingStatus(2)
            data_chunk.add_status(status)
            logging.warning(status.get_message())
            self.camera_status.initialised = False
            return [data_chunk]

        self.camera_status.capturing = True
        frame_raw = self.camera_object.GetImage(GET_IMAGE_TIMEOUT)
        self.camera_status.capturing = False

        frame_shape = frame_raw.shape
        frame_colormap = 'BGR'
        frame_np = frame_raw.GetNPArray()

        if frame_raw is not None:
            data_chunk.add_data(DataChunkImage('frame', frame_np, 'base64_png'))

            status = CapturingStatus(0)
            data_chunk.add_status(status)
            logging.warning(status.get_message())

            data_chunk.add_metadata(MetadataChunkData('colormap', 'BGR'))
            data_chunk.add_metadata(MetadataChunkData('shape', frame_np.shape))
            for metadata_variable, metadata_value in self.config.metadata.items():
                data_chunk.add_metadata(MetadataChunkData(metadata_variable, metadata_value))
            return [data_chunk]
        else:
            status = CapturingStatus(99)
            data_chunk.add_status(status)
            logging.warning(status.get_message())
            self.camera_status.initialised = False
            return [data_chunk]

    def execute(self):
        return super().execute()

    def get_details(self):
        if not self.camera_object.IsConnected():
            return {}
        return {
            'id': neoapi.CamInfo().GetId(),
            'model_name': neoapi.CamInfo().GetModelName(),
            'serial_number': neoapi.CamInfo().GetSerialNumber(),
            'vendor_name': neoapi.CamInfo().GetVendorName(),
        }

    def get_configuration(self):
        if not self.camera_object.IsConnected():
            return {}
        return {f.GetName(): f.GetValue() for f in neoapi.FeatureList}
