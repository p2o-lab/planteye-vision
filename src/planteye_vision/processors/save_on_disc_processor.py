import json
import logging
import os

import cv2
from planteye_vision.common.timestamp import get_timestamp
from planteye_vision.configuration.processor_configuration import SaveOnDiskProcessorConfiguration
from planteye_vision.data_chunks.data_chunk_data import DataChunkImage
from planteye_vision.processors.data_processor import ConfigurableDataProcessor


class SaveOnDiskProcessor(ConfigurableDataProcessor):
    def __init__(self, config: SaveOnDiskProcessorConfiguration):
        self.config = config
        self.name = None
        self.type = None

    def apply_configuration(self):
        if not self.config.is_valid():
            return
        self.name = self.config.name
        self.type = self.config.type
        os.makedirs(self.config.parameters['save_path'], exist_ok=True)

    def apply_processor(self, data_chunks):
        if not self.config.is_valid():
            logging.warning(f'Processor {self.name} ({self.type}): no execution, invalid configuration')
            return None

        timestamp = get_timestamp()
        json_dict = {}
        for chunk in data_chunks:
            if chunk.hidden:
                continue
            chunk_dict = chunk.as_dict()

            if chunk.chunk_type in ['local_camera_cv2', 'baumer_camera_neoapi',
                                    'image_resize', 'image_crop', 'color_conversion']:
                chunk_dict.pop('data')
                for image in chunk.data:
                    if isinstance(image, DataChunkImage) and chunk.data[0].value is not None:
                        image_file_name = str(timestamp) + '_' + chunk.name + '_' + image.name + '.png'
                        image_file_full_path = os.path.join(self.config.parameters['save_path'], image_file_name)
                        ret_val = cv2.imwrite(image_file_full_path, chunk.data[0].value)
                        chunk_dict['data'] = {image.name: image_file_name}
                        if ret_val:
                            logging.info(f'Data saved as {image_file_full_path}')
                        else:
                            logging.info(f'Data NOT saved as {image_file_full_path}')

            json_dict[chunk.name] = chunk_dict

        if len(json_dict) != 0:
            json_file_name = str(timestamp) + '.json'
            json_file_full_path = os.path.join(self.config.parameters['save_path'], json_file_name)
            with open(json_file_full_path, 'w') as json_file:
                json.dump(json_dict, json_file, indent=4)

        logging.debug(f'Processor {self.name} ({self.type}): execution successful')
        return data_chunks

    def execute(self, input_data):
        return super().execute(input_data)
