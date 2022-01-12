from src.data_chunks.data_chunk_data import DataChunkImage
from src.configuration.config_provider import ConfigProvider
from src.processors.data_processor import NonConfigurableDataProcessor, ConfigurableDataProcessor
from src.configuration.processor_configuration import TFModelInferenceProcessorConfiguration, ImageResizeProcessorConfiguration, ImageCropProcessorConfiguration, ColorConversionProcessorConfiguration, InputProcessorConfiguration
import logging
import os
import tensorflow as tf
import cv2

from src.data_chunks.data_chunk import GeneralDataChunk
from src.data_chunks.data_chunk_data import DataChunkValue, DataChunkImage
from src.data_chunks.metadata_chunk import MetadataChunkData
from src.data_chunks.data_chunk_status import ProcessorStatus


class EncodeImageChunksToBase64(NonConfigurableDataProcessor):
    def apply_processor(self, chunks: list):
        logging.debug('Images to base64 string...')
        for chunk in chunks:
            for chunk_pieces in chunk.data:
                if isinstance(chunk_pieces, DataChunkImage):
                    chunk_pieces.encode_as_base64()


class ChunksToDict(NonConfigurableDataProcessor):
    def apply_processor(self, chunks: list):
        logging.debug('Chunks to json body...')
        response_body = {}
        for chunk in chunks:
            response_body[chunk.name] = chunk.as_dict()
        return response_body


class TFModelInference(ConfigurableDataProcessor):
    def __init__(self):
        self.config = TFModelInferenceProcessorConfiguration()
        self.name = None
        self.type = None
        self.path_to_model = None
        self.tf_model = None

    def import_configuration(self, config_provider: ConfigProvider):
        self.name = config_provider.provide_name()
        self.config.read(config_provider)
        self.type = self.config.type

    def apply_configuration(self):
        path_to_models = self.config.access_data['path_to_models']
        model_name = self.config.access_data['model_name']
        model_version = self.config.access_data['model_version']
        self.path_to_model = os.path.join(path_to_models, model_name, model_version)
        self.tf_model = tf.keras.models.load_model(self.path_to_model)
        self.tf_model.summary()

    def apply_processor(self, image_np):
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.access_data)
        if not self.config.is_valid():
            status = ProcessorStatus(100)
            data_chunk.add_status(status)
            print('Step %s : No execution due to invalid configuration' % self.name)
            return data_chunk
        logging.debug('Running inference...')
        print('Inference Run')
        batched_image_np = tf.expand_dims(image_np, axis=0)
        try:
            value = self.tf_model.predict(batched_image_np).flatten().tolist()
            status = ProcessorStatus(0)
            data_chunk.add_status(status)
            data_chunk.add_data(DataChunkValue('inference_result', value))
        except Exception:
            status = ProcessorStatus(99)
            data_chunk.add_status(status)
        return data_chunk


class ImageResize(ConfigurableDataProcessor):
    def __init__(self):
        self.config = ImageResizeProcessorConfiguration()
        self.name = None
        self.type = None
        self.width = None
        self.height = None
        self.interpolation = None

    def import_configuration(self, config_provider: ConfigProvider):
        self.name = config_provider.provide_name()
        self.config.read(config_provider)
        self.type = self.config.type

    def apply_configuration(self):
        self.width = self.config.access_data['width']
        self.height = self.config.access_data['height']
        self.interpolation = self.config.access_data['interpolation']

    def apply_processor(self, image_np):
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.access_data)
        if not self.config.is_valid():
            status = ProcessorStatus(100)
            data_chunk.add_status(status)
            print('Step %s : No execution due to invalid configuration' % self.name)
            return data_chunk
        logging.debug('Resizing...')
        print('Resize Run')
        width = int(self.width)
        height = int(self.height)
        dim = (width, height)
        cv2_interpolation = eval(f'cv2.{self.interpolation}')
        try:
            value = cv2.resize(image_np, dim, interpolation=cv2_interpolation)
            status = ProcessorStatus(0)
            data_chunk.add_status(status)
            data_chunk.add_data(DataChunkImage('image', value))
        except Exception:
            status = ProcessorStatus(99)
            data_chunk.add_status(status)
        return data_chunk


class ImageCrop(ConfigurableDataProcessor):
    def __init__(self):
        self.config = ImageCropProcessorConfiguration()
        self.name = None
        self.type = None
        self.x_init = None
        self.x_diff = None
        self.y_init = None
        self.y_diff= None

    def import_configuration(self, config_provider: ConfigProvider):
        self.name = config_provider.provide_name()
        self.config.read(config_provider)
        self.type = self.config.type

    def apply_configuration(self):
        self.x_init = self.config.access_data['x_init']
        self.x_diff = self.config.access_data['x_diff']
        self.y_init = self.config.access_data['y_init']
        self.y_diff = self.config.access_data['y_diff']

    def apply_processor(self, image_np):
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.access_data)
        if not self.config.is_valid():
            status = ProcessorStatus(100)
            data_chunk.add_status(status)
            print('Step %s : No execution due to invalid configuration' % self.name)
            return data_chunk
        logging.debug('Cropping...')
        print('Crop Run')
        x_end = int(self.x_init+self.x_diff)
        y_end = int(self.y_init + self.y_diff)

        try:
            value = image_np[self.x_init:x_end, self.y_init:y_end, :]
            status = ProcessorStatus(0)
            data_chunk.add_status(status)
            data_chunk.add_data(DataChunkImage('image', value))
        except Exception:
            status = ProcessorStatus(99)
            data_chunk.add_status(status)
        return data_chunk


class ImageColorConversion(ConfigurableDataProcessor):
    def __init__(self):
        self.config = ColorConversionProcessorConfiguration()
        self.name = None
        self.type = None
        self.conversion = None

    def import_configuration(self, config_provider: ConfigProvider):
        self.name = config_provider.provide_name()
        self.config.read(config_provider)
        self.type = self.config.type

    def apply_configuration(self):
        self.conversion = self.config.parameters['conversion']

    def apply_processor(self, image_np):
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.access_data)
        if not self.config.is_valid():
            status = ProcessorStatus(100)
            data_chunk.add_status(status)
            print('Step %s : No execution due to invalid configuration' % self.name)
            return data_chunk
        logging.debug('Color conversion...')
        print('Color Conversion Run')
        color_conversion = eval(f'cv2.COLOR_{self.conversion}')

        try:
            value = cv2.cvtColor(image_np, color_conversion)
            status = ProcessorStatus(0)
            data_chunk.add_status(status)
            data_chunk.add_data(DataChunkImage('image', value))
        except Exception:
            status = ProcessorStatus(99)
            data_chunk.add_status(status)
        return data_chunk


class InputProcessor(ConfigurableDataProcessor):
    def __init__(self):
        self.config = InputProcessorConfiguration()
        self.name = None
        self.type = None
        self.input_inlets = []

    def import_configuration(self, config_provider: ConfigProvider):
        self.name = config_provider.provide_name()
        self.config.read(config_provider)
        self.type = self.config.type

    def apply_configuration(self):
        self.input_inlets = self.config.access_data['input_inlets']

    def apply_processor(self, chunks: list):
        logging.debug('Input processor...')
        print('Input Processor Run')
        output_data = []
        if not self.config.is_valid():
            print('Step %s : No execution due to invalid configuration' % self.name)
            return None

        for inlet in self.input_inlets:
            for chunk in chunks:
                if chunk.name == inlet:
                    output_data.append(chunk.data[0].value)
        if len(output_data) == 1:
            return output_data[0]
        return output_data
