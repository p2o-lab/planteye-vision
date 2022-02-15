from planteye_vision.processors.data_processor import NonConfigurableDataProcessor, ConfigurableDataProcessor
from planteye_vision.configuration.processor_configuration import *
import logging
import os
import tensorflow as tf
import cv2
import json

from planteye_vision.data_chunks.data_chunk import GeneralDataChunk
from planteye_vision.data_chunks.data_chunk_data import DataChunkValue, DataChunkImage
from planteye_vision.data_chunks.data_chunk_status import ProcessorStatus
from planteye_vision.common.timestamp import get_timestamp


class EncodeImageChunksToBase64(NonConfigurableDataProcessor):
    def __init__(self):
        self.name = 'base64_encode'
        self.type = 'base64_encode'

    def apply_processor(self, chunks: list):
        for chunk in chunks:
            for chunk_pieces in chunk.data:
                if isinstance(chunk_pieces, DataChunkImage):
                    chunk_pieces.encode_as_base64()
        logging.info('Processor ' + self.name + ' (' + self.type + '): execution successful')

    def execute(self, input_data):
        return super().execute(input_data)


class ChunksToDict(NonConfigurableDataProcessor):
    def __init__(self):
        self.name = 'chunks_to_dict'
        self.type = 'chunks_to_dict'

    def apply_processor(self, chunks: list):
        response_body = {}
        for chunk in chunks:
            if not chunk.hidden:
                response_body[chunk.name] = chunk.as_dict()
        logging.info('Processor ' + self.name + ' (' + self.type + '): execution successful')
        return response_body

    def execute(self, input_data):
        return super().execute(input_data)


class InputProcessor(ConfigurableDataProcessor):
    def __init__(self, config: InputProcessorConfiguration):
        self.config = config
        self.name = None
        self.type = None
        self.input_inlets = []

    def apply_configuration(self):
        self.input_inlets = self.config.parameters['input_inlets']
        self.name = self.config.name
        self.type = self.config.type

    def apply_processor(self, chunks: list):
        output_data = []
        if not self.config.is_valid():
            logging.warning('Processor ' + self.name + ' (' + self.type + '): no execution, invalid configuration')
            return None

        if self.input_inlets == ['all']:
            [output_data.append(chunk) for chunk in chunks]
        else:
            for inlet in self.input_inlets:
                for chunk in chunks:
                    if chunk.name == inlet:
                        output_data.append(chunk)

        logging.info('Processor ' + self.name + ' (' + self.type + '): execution successful')
        return output_data

    def execute(self, input_data):
        return super().execute(input_data)


class ImageResize(ConfigurableDataProcessor):
    def __init__(self, config: ImageResizeProcessorConfiguration):
        self.config = config
        self.name = None
        self.type = None
        self.width = None
        self.height = None
        self.interpolation = None

    def apply_configuration(self):
        self.width = self.config.parameters['width']
        self.height = self.config.parameters['height']
        self.interpolation = self.config.parameters['interpolation']
        self.name = self.config.name
        self.type = self.config.type

    def apply_processor(self, chunks: list):
        result_chunks = []
        for chunk in chunks:
            if chunk.chunk_type in ['local_camera_cv2', 'baumer_camera_neoapi', 'image_resize', 'image_crop']:
                new_name = chunk.name + '_' + self.name
                data_chunk = GeneralDataChunk(new_name, self.type, self.config.parameters, hidden=self.config.hidden)
                if not self.config.is_valid():
                    status = ProcessorStatus(100)
                    data_chunk.add_status(status)
                    logging.warning('Processor ' + self.name + ' (' + self.type + '): no execution, invalid configuration')
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
                    logging.info('Processor ' + self.name + ' (' + self.type + '): execution successful')
                except Exception:
                    status = ProcessorStatus(99)
                    data_chunk.add_status(status)
                    logging.warning('Processor ' + self.name + ' (' + self.type + '): error during execution')
                result_chunks.append(data_chunk)
            else:
                result_chunks.append(chunk)
        return result_chunks

    def execute(self, input_data):
        return super().execute(input_data)


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
        self.x_init = self.config.parameters['x_init']
        self.x_diff = self.config.parameters['x_diff']
        self.y_init = self.config.parameters['y_init']
        self.y_diff = self.config.parameters['y_diff']
        self.name = self.config.name
        self.type = self.config.type

    def apply_processor(self, chunks):
        result_chunks = []
        for chunk in chunks:
            if chunk.chunk_type in ['local_camera_cv2', 'baumer_camera_neoapi', 'image_resize', 'image_crop']:
                new_name = chunk.name + '_' + self.name
                data_chunk = GeneralDataChunk(new_name, self.type, self.config.parameters, hidden=self.config.hidden)
                if not self.config.is_valid():
                    status = ProcessorStatus(100)
                    data_chunk.add_status(status)
                    logging.warning('Processor ' + self.name + ' (' + self.type + '): no execution, invalid configuration')
                    continue
                x_end = int(self.x_init + self.x_diff)
                y_end = int(self.y_init + self.y_diff)

                try:
                    image_np = chunk.data[0].value
                    value = image_np[self.x_init:x_end, self.y_init:y_end, :]
                    status = ProcessorStatus(0)
                    data_type = 'image'
                    data_chunk.add_status(status)
                    data_chunk.add_data(DataChunkImage('frame', value, data_type))
                    logging.info('Processor ' + self.name + ' (' + self.type + '): execution successful')
                except Exception:
                    status = ProcessorStatus(99)
                    data_chunk.add_status(status)
                    logging.warning('Processor ' + self.name + ' (' + self.type + '): error during execution')
                result_chunks.append(data_chunk)
            else:
                result_chunks.append(chunk)
        return result_chunks

    def execute(self, input_data):
        return super().execute(input_data)


class ImageColorConversion(ConfigurableDataProcessor):
    def __init__(self, config: ColorConversionProcessorConfiguration):
        self.config = config
        self.name = None
        self.type = None
        self.conversion = None

    def apply_configuration(self):
        self.conversion = self.config.parameters['conversion']
        self.name = self.config.name
        self.type = self.config.type

    def apply_processor(self, chunks):
        result_chunks = []
        for chunk in chunks:
            if chunk.chunk_type in ['local_camera_cv2', 'baumer_camera_neoapi', 'image_resize', 'image_crop']:
                new_name = chunk.name + '_' + self.name
                data_chunk = GeneralDataChunk(new_name, self.type, self.config.parameters, hidden=self.config.hidden)
                if not self.config.is_valid():
                    status = ProcessorStatus(100)
                    data_chunk.add_status(status)
                    logging.warning('Processor ' + self.name + ' (' + self.type + '): no execution, invalid configuration')
                    continue
                color_conversion = eval(f'cv2.COLOR_{self.conversion}')

                try:
                    image_np = chunk.data[0].value
                    value = cv2.cvtColor(image_np, color_conversion)
                    status = ProcessorStatus(0)
                    data_type = 'image'
                    data_chunk.add_status(status)
                    data_chunk.add_data(DataChunkImage('frame', value, data_type))
                    logging.info('Processor ' + self.name + ' (' + self.type + '): execution successful')
                except Exception:
                    status = ProcessorStatus(99)
                    data_chunk.add_status(status)
                    logging.warning('Processor ' + self.name + ' (' + self.type + '): error during execution')
                result_chunks.append(data_chunk)
            else:
                result_chunks.append(chunk)
        return result_chunks

    def execute(self, input_data):
        return super().execute(input_data)


class TFModelInference(ConfigurableDataProcessor):
    def __init__(self, config: TFModelInferenceProcessorConfiguration):
        self.config = config
        self.name = None
        self.type = None
        self.path_to_model = None
        self.tf_model = None

    def apply_configuration(self):
        if not self.config.is_valid():
            return
        path_to_models = self.config.parameters['path_to_models']
        model_name = self.config.parameters['model_name']
        model_version = self.config.parameters['model_version']
        self.path_to_model = os.path.join(path_to_models, model_name, model_version)
        self.tf_model = tf.keras.models.load_model(self.path_to_model)
        self.name = self.config.name
        self.type = self.config.type
        # self.tf_model.summary()

    def apply_processor(self, data_chunks):
        image_np = data_chunks[0].data[0].value
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.parameters, hidden=self.config.hidden)
        if not self.config.is_valid():
            status = ProcessorStatus(100)
            data_chunk.add_status(status)
            logging.warning('Processor ' + self.name + ' (' + self.type + '): no execution, invalid configuration')
            return data_chunk
        batched_image_np = tf.expand_dims(image_np, axis=0)
        try:
            value = self.tf_model.predict(batched_image_np).flatten().tolist()
            status = ProcessorStatus(0)
            data_type = 'diverse'
            data_chunk.add_status(status)
            data_chunk.add_data(DataChunkValue('inference_result', value, data_type))
            logging.info('Processor ' + self.name + ' (' + self.type + '): execution successful')
        except Exception:
            status = ProcessorStatus(99)
            data_chunk.add_status(status)
            logging.warning('Processor ' + self.name + ' (' + self.type + '): error during execution')
        return [data_chunk]

    def execute(self, input_data):
        return super().execute(input_data)


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
            logging.warning('Processor ' + self.name + ' (' + self.type + '): no execution, invalid configuration')
            return None

        timestamp = get_timestamp()
        json_dict = {}
        for chunk in data_chunks:
            if chunk.hidden:
                continue
            chunk_dict = chunk.as_dict()

            if chunk.chunk_type in ['local_camera_cv2', 'baumer_camera_neoapi', 'image_resize', 'image_crop', 'color_conversion']:
                chunk_dict.pop('data')
                for image in chunk.data:
                    if isinstance(image, DataChunkImage):
                        image_file_name = str(timestamp) + '_' + chunk.name + '_' + image.name + '.png'
                        image_file_full_path = os.path.join(self.config.parameters['save_path'], image_file_name)
                        ret_val = cv2.imwrite(image_file_full_path, chunk.data[0].value)
                        chunk_dict['data'] = {image.name: image_file_name}

            json_dict[chunk.name] = chunk_dict

        if len(json_dict) != 0:
            json_file_name = str(timestamp) + '.json'
            json_file_full_path = os.path.join(self.config.parameters['save_path'], json_file_name)
            with open(json_file_full_path, 'w') as json_file:
                json.dump(json_dict, json_file, indent=4)

        logging.info('Processor ' + self.name + ' (' + self.type + '): execution successful')
        return data_chunks

    def execute(self, input_data):
        return super().execute(input_data)
