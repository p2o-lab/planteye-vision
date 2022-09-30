import logging
from time import sleep

from planteye_vision.inlet.generic_camera_inlet import GenericCameraInlet
from planteye_vision.common.timestamp import get_timestamp
from planteye_vision.data_chunks.data_chunk import GeneralDataChunk
from planteye_vision.data_chunks.data_chunk_status import CapturingStatus
from planteye_vision.data_chunks.metadata_chunk import MetadataChunkData
from planteye_vision.data_chunks.data_chunk_data import DataChunkImage
from planteye_vision.configuration.inlet_configuration import VideoCameraConfiguration


class GenericCameraVideoInlet(GenericCameraInlet):
    def __init__(self, config: VideoCameraConfiguration):
        super().__init__(config)

    def retrieve_data(self):
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.parameters, hidden=self.config.hidden)

        if not self.config.is_valid():
            status = CapturingStatus(100)
            data_chunk.add_status(status)
            logging.debug(f'Step {self.name} : No execution due to invalid configuration')
            return [data_chunk]

        if not self.camera_status.initialised:
            self.connect()

        timestamp = MetadataChunkData('timestamp', get_timestamp())
        data_chunk.add_metadata(timestamp)

        if not self.camera_status.initialised:
            status = CapturingStatus(1)
            data_chunk.add_status(status)
            logging.debug(status.get_message())
            self.camera_status.initialised = False
            return [data_chunk]

        if self.camera_status.capturing:
            status = CapturingStatus(2)
            data_chunk.add_status(status)
            logging.debug(status.get_message())
            self.camera_status.initialised = False
            return [data_chunk]

        self.camera_status.capturing = True
        frames = []
        interval_btw_frames = 1/self.config.parameters['fps']
        for _ in range(self.config.parameters['no_frames']):
            captured, frame_np = self.camera_object.read()
            if captured:
                frames.append(frame_np)
                sleep(interval_btw_frames)
            else:
                status = CapturingStatus(99)
                data_chunk.add_status(status)
                logging.debug(status.get_message())
                self.camera_status.initialised = False
                return [data_chunk]

        self.camera_status.capturing = False

        frame_no = 0
        for frame in frames:
            frame_name = f'frame{str(frame_no).zfill(3)}'
            data_chunk.add_data(DataChunkImage(frame_name, frame, 'base64_png'))
            frame_no += 1

        frame_shape = frames[0].shape

        status = CapturingStatus(0)
        data_chunk.add_status(status)
        logging.debug(status.get_message())

        data_chunk.add_metadata(MetadataChunkData('colormap', 'BGR'))
        data_chunk.add_metadata(MetadataChunkData('shape', frame_shape))
        for metadata_variable, metadata_value in self.config.metadata.items():
            data_chunk.add_metadata(MetadataChunkData(metadata_variable, metadata_value))

        return [data_chunk]
