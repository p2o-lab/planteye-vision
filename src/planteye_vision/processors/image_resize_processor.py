import logging

import cv2
from planteye_vision.configuration.processor_configuration import ImageResizeProcessorConfiguration
from planteye_vision.data_chunks.data_chunk import GeneralDataChunk
from planteye_vision.data_chunks.data_chunk_data import DataChunkImage
from planteye_vision.data_chunks.data_chunk_status import ProcessorStatus
from planteye_vision.processors.data_processor import ConfigurableDataProcessor


class ImageResize(ConfigurableDataProcessor):
    def __init__(self, config: ImageResizeProcessorConfiguration):
        self.config = config
        self.name = None
        self.type = None
        self.width = None
        self.height = None
        self.interpolation = None

    def apply_configuration(self):
        self.name = self.config.name
        self.type = self.config.type
        self.width = self.config.parameters['width']
        self.height = self.config.parameters['height']
        self.interpolation = self.config.parameters['interpolation']

    def apply_processor(self, chunks: list):
        result_chunks = []
        for chunk in chunks:
            if chunk.chunk_type in ['local_camera_cv2', 'baumer_camera_neoapi', 'image_resize', 'image_crop']:
                new_name = chunk.name + '_' + self.name
                data_chunk = GeneralDataChunk(new_name, self.type, self.config.parameters, hidden=self.config.hidden)
                if not self.config.is_valid():
                    status = ProcessorStatus(100)
                    data_chunk.add_status(status)
                    logging.warning(f'Processor {self.name} ({self.type}): no execution, invalid configuration')
                    continue
                width = int(self.width)
                height = int(self.height)
                dim = (width, height)
                cv2_interpolation = eval(f'cv2.{self.interpolation}')
                try:
                    image_np = chunk.data[0].value
                    value = cv2.resize(image_np, dim, interpolation=cv2_interpolation)
                    status = ProcessorStatus(0)
                    data_type = 'image'
                    data_chunk.add_status(status)
                    data_chunk.add_data(DataChunkImage('frame', value, data_type))
                    logging.debug(f'Processor {self.name} ({self.type}): execution successful')
                except Exception:
                    status = ProcessorStatus(99)
                    data_chunk.add_status(status)
                    logging.warning(f'Processor {self.name} ({self.type}): error during execution')
                result_chunks.append(data_chunk)
            else:
                result_chunks.append(chunk)
        return result_chunks

    def execute(self, input_data):
        return super().execute(input_data)
