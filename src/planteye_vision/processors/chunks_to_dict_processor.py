import logging

from planteye_vision.processors.data_processor import NonConfigurableDataProcessor


class ChunksToDict(NonConfigurableDataProcessor):
    def __init__(self):
        self.name = 'chunks_to_dict'
        self.type = 'chunks_to_dict'

    def apply_processor(self, chunks: list):
        response_body = {}
        for chunk in chunks:
            if not chunk.hidden:
                response_body[chunk.name] = chunk.as_dict()
        logging.debug(f'Processor {self.name} ({self.type}): execution successful')
        return response_body

    def execute(self, input_data):
        return super().execute(input_data)
