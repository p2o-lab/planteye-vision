from abc import ABC, abstractmethod

from src.data_chunks.data_chunk_data import DataChunkImage
import logging


class DataTransformer (ABC):
    @abstractmethod
    def apply_transformation(self, input_data):
        pass


class EncodeImageChunksToBase64(DataTransformer):
    def apply_transformation(self, chunks):
        logging.debug('Images to base64 string...')
        for chunk in chunks:
            for chunk_pieces in chunk.data:
                if isinstance(chunk_pieces, DataChunkImage):
                    chunk_pieces.encode_as_base64()


class ChunksToDict(DataTransformer):
    def apply_transformation(self, chunks):
        logging.debug('Chunks to json body...')
        response_body = {}
        for chunk in chunks:
            response_body[chunk.name] = chunk.as_dict()

        return response_body
