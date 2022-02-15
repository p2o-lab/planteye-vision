import logging
from time import sleep
import cv2

from planteye_vision.inlet.camera_inlet import CameraInlet
from planteye_vision.common.timestamp import get_timestamp
from planteye_vision.data_chunks.data_chunk import GeneralDataChunk
from planteye_vision.data_chunks.data_chunk_status import CapturingStatus
from planteye_vision.data_chunks.metadata_chunk import MetadataChunkData
from planteye_vision.data_chunks.data_chunk_data import DataChunkImage
from planteye_vision.configuration.inlet_configuration import CameraConfiguration


class GenericCameraInlet(CameraInlet):
    def __init__(self, config: CameraConfiguration):
        super().__init__(config)

    def __del__(self):
        if self.camera_object is not None:
            self.disconnect()

    def set_parameter(self, parameter: str, requested_value: object) -> bool:
        """
        Sets a single parameter of capturing device.
        :param parameter: str: Parameter identifier of VideoCaptureProperties from OpenCV.
        List of available parameters and their description is to find on
        on https://docs.opencv.org/3.4/d4/d15/groupvideoioflagsbase.html
        Please consider that not every capturing device supports all parameters.
        :param requested_value: any type: Desired value of the parameter
        :return: bool: True if the parameter is set successfully, False - if not
        """
        par = None
        try:
            par = exec("cv2.%s" % parameter)
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

    def connect(self):
        while True:
            try:
                self.camera_object = cv2.VideoCapture(self.config.parameters['device_id'])
            except Exception as exc:
                logging.error('Capturing device not connected... trying again', exc_info=exc)
            if self.camera_object.isOpened():
                break
            sleep(1)

        self.camera_status.initialised = True
        logging.info('Capturing device initialised successfully')

    def disconnect(self):
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
        captured, frame_np = self.camera_object.read()
        self.camera_status.capturing = False

        if captured:
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
