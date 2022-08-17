import logging

from planteye_vision.data_chunks.data_chunk_data import DataChunkImage
from planteye_vision.processors.data_processor import NonConfigurableDataProcessor


class EncodeImageChunksToBase64(NonConfigurableDataProcessor):
    def __init__(self):
        self.name = 'base64_encode'
        self.type = 'base64_encode'

    def apply_processor(self, chunks: list):
        for chunk in chunks:
            for chunk_pieces in chunk.data:
                if isinstance(chunk_pieces, DataChunkImage):
                    chunk_pieces.encode_as_base64()

    def execute(self, input_data):
        return super().execute(input_data)
