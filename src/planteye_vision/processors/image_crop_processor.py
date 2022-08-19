import logging

from planteye_vision.configuration.processor_configuration import ImageCropProcessorConfiguration
from planteye_vision.data_chunks.data_chunk import GeneralDataChunk
from planteye_vision.data_chunks.data_chunk_data import DataChunkImage
from planteye_vision.data_chunks.data_chunk_status import ProcessorStatus
from planteye_vision.processors.data_processor import ConfigurableDataProcessor


class ImageCrop(ConfigurableDataProcessor):
    def __init__(self, config: ImageCropProcessorConfiguration):
        self.config = config
        self.name = None
        self.type = None
        self.x_init = None
        self.x_diff = None
        self.y_init = None
        self.y_diff = None

    def apply_configuration(self):
        self.name = self.config.name
        self.type = self.config.type
        self.x_init = self.config.parameters['x_init']
        self.x_diff = self.config.parameters['x_diff']
        self.y_init = self.config.parameters['y_init']
        self.y_diff = self.config.parameters['y_diff']

    def apply_processor(self, chunks):
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
                x_end = int(self.x_init + self.x_diff)
                y_end = int(self.y_init + self.y_diff)

                try:
                    image_np = chunk.data[0].value
                    image_dims = len(image_np.shape)
                    if image_dims == 3:
                        value = image_np[self.x_init:x_end, self.y_init:y_end, :]
                    elif image_dims == 2:
                        value = image_np[self.x_init:x_end, self.y_init:y_end]
                    else:
                        raise BaseException
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
