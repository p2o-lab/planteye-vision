import logging
import os
import numpy as np
from planteye_vision.configuration.processor_configuration import TFModelInferenceProcessorConfiguration
from planteye_vision.data_chunks.data_chunk import GeneralDataChunk
from planteye_vision.data_chunks.data_chunk_data import DataChunkValue
from planteye_vision.data_chunks.data_chunk_status import ProcessorStatus
from planteye_vision.processors.data_processor import ConfigurableDataProcessor
import torch


class PTModelInference(ConfigurableDataProcessor):
    def __init__(self, config: TFModelInferenceProcessorConfiguration):
        self.config = config
        self.name = None
        self.type = None
        self.path_to_model = None
        self.model = None

    def apply_configuration(self):
        if not self.config.is_valid():
            return
        self.name = self.config.name
        self.type = self.config.type
        path_to_models = self.config.parameters['path_to_models']
        model_name = self.config.parameters['model_name']
        model_version = self.config.parameters['model_version']
        self.path_to_model = os.path.join(path_to_models, model_name, model_version, 'model.pt')
        try:
            self.model = torch.jit.load(self.path_to_model)
            logging.info(f'Processor {self.name} ({self.type}): pt model loaded')
            self.model.eval()
        except Exception as exc:
            logging.error(f'Processor {self.name} ({self.type}): no pt model could be loaded: {exc}')

    def apply_processor(self, data_chunks):
        image_np = data_chunks[0].data[0].value
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.parameters, hidden=self.config.hidden)
        if not self.config.is_valid():
            status = ProcessorStatus(100)
            data_chunk.add_status(status)
            logging.warning(f'Processor {self.name} ({self.type}): no execution, invalid configuration')
            return data_chunk
        if len(image_np.shape) == 2:
            image_np = np.expand_dims(image_np, axis=-1)

        image_np = np.transpose(image_np, (2, 0, 1))
        image_np = np.expand_dims(image_np, axis=1)
        img_tensor = torch.from_numpy(image_np).float()
        try:
            with torch.no_grad():
                predicted = self.model(img_tensor)

            if len(predicted.shape) == 1:
                value = predicted.item()
            else:
                value = predicted.tolist()[0]

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
