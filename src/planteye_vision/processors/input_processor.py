import logging

from planteye_vision.configuration.processor_configuration import InputProcessorConfiguration
from planteye_vision.processors.data_processor import ConfigurableDataProcessor


class InputProcessor(ConfigurableDataProcessor):
    def __init__(self, config: InputProcessorConfiguration):
        self.config = config
        self.name = None
        self.type = None
        self.input_inlets = []

    def apply_configuration(self):
        self.name = self.config.name
        self.type = self.config.type
        self.input_inlets = self.config.parameters['input_inlets']

    def apply_processor(self, chunks: list):
        output_data = []
        if not self.config.is_valid():
            logging.warning(f'Processor {self.name} ({self.type}): no execution, invalid configuration')
            return None

        if self.input_inlets == ['all']:
            [output_data.append(chunk) for chunk in chunks]
        else:
            for inlet in self.input_inlets:
                for chunk in chunks:
                    if chunk.name == inlet:
                        output_data.append(chunk)

        logging.debug(f'Processor {self.name} ({self.type}): execution successful')
        return output_data

    def execute(self, input_data):
        return super().execute(input_data)
