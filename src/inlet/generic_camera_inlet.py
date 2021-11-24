import logging
from time import sleep
import cv2

from src.inlet.camera_inlet import CameraInlet
from src.common.timestamp import get_timestamp
from src.common.data_chunk import GeneralDataChunk
from src.common.data_chunk_status import CapturingStatus
from src.common.metadata_chunk import MetadataChunkData
from src.common.data_chunk_data import DataChunkValue


class GenericCameraInlet(CameraInlet):
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

    def connect(self):
        while True:
            try:
                self.camera_object = cv2.VideoCapture(self.config.device_id)
            except Exception as exc:
                logging.error('Capturing device not connected... trying again', exc_info=exc)
            if self.camera_object.isOpened():
                break
            sleep(1)

        self.camera_status.initialised = True
        logging.info('Capturing device initialised successfully')
        logging.info(self.get_camera_info())

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
        data_chunk = GeneralDataChunk()

        if not self.camera_status.initialised:
            self.connect()

        timestamp = MetadataChunkData('timestamp', get_timestamp())
        data_chunk.add_metadata(timestamp)

        if not self.camera_status.initialised:
            status = CapturingStatus(1)
            data_chunk.add_status(status)
            logging.warning(status.get_message())
            return data_chunk

        if self.camera_status.capturing:
            status = CapturingStatus(2)
            data_chunk.add_status(status)
            logging.warning(status.get_message())
            return data_chunk

        self.camera_status.capturing = True
        captured, frame_np = self.camera_object.read()
        self.camera_status.capturing = False

        if captured:
            data_chunk.add_data(DataChunkValue('frame', frame_np))

            status = CapturingStatus(0)
            data_chunk.add_status(status)
            logging.warning(status.get_message())

            data_chunk.add_metadata(MetadataChunkData('colormap', 'BGR'))
            data_chunk.add_metadata(MetadataChunkData('shape', frame_np.shape))
            for metadata_variable, metadata_value in self.config.metadata.items():
                data_chunk.add_metadata(MetadataChunkData(metadata_variable, metadata_value))
            return data_chunk
        else:
            status = CapturingStatus(99)
            data_chunk.add_status(status)
            logging.warning(status.get_message())
            return data_chunk

    def get_camera_info(self):
        return 'Camera info'
