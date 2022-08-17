import logging
import os

from planteye_vision.configuration.processor_configuration import TFModelInferenceProcessorConfiguration
from planteye_vision.data_chunks.data_chunk import GeneralDataChunk
from planteye_vision.data_chunks.data_chunk_data import DataChunkValue
from planteye_vision.data_chunks.data_chunk_status import ProcessorStatus
from planteye_vision.processors.data_processor import ConfigurableDataProcessor


class TFModelInference(ConfigurableDataProcessor):
    import tensorflow as tf

    def __init__(self, config: TFModelInferenceProcessorConfiguration):
        self.config = config
        self.name = None
        self.type = None
        self.path_to_model = None
        self.tf_model = None

    def apply_configuration(self):
        if not self.config.is_valid():
            return
        self.name = self.config.name
        self.type = self.config.type
        path_to_models = self.config.parameters['path_to_models']
        model_name = self.config.parameters['model_name']
        model_version = self.config.parameters['model_version']
        self.path_to_model = os.path.join(path_to_models, model_name, model_version)
        try:
            self.tf_model = self.tf.keras.models.load_model(self.path_to_model)
            logging.info(f'Processor {self.name} ({self.type}): tf model loaded')
            self.tf_model.summary()
        except Exception as exc:
            logging.error(f'Processor {self.name} ({self.type}): no tf model can be loaded: {exc}')

    def apply_processor(self, data_chunks):
        image_np = data_chunks[0].data[0].value
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.parameters, hidden=self.config.hidden)
        if not self.config.is_valid():
            status = ProcessorStatus(100)
            data_chunk.add_status(status)
            logging.warning(f'Processor {self.name} ({self.type}): no execution, invalid configuration')
            return data_chunk
        batched_image_np = self.tf.expand_dims(image_np, axis=0)
        try:
            value = self.tf_model.predict(batched_image_np).flatten().tolist()
            status = ProcessorStatus(0)
            data_type = 'diverse'
            data_chunk.add_status(status)
            data_chunk.add_data(DataChunkValue('inference_result', value, data_type))
            logging.debug(f'Processor {self.name} ({self.type}): execution successful')
        except Exception as exc:
            status = ProcessorStatus(99)
            data_chunk.add_status(status)
            logging.warning(f'Processor {self.name} ({self.type}): error during execution: {exc}')
        return [data_chunk]

    def execute(self, input_data):
        return super().execute(input_data)
