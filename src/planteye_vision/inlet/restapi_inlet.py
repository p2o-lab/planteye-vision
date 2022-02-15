import logging

from planteye_vision.inlet.inlet import Inlet
from planteye_vision.configuration.inlet_configuration import RestAPIInletConfiguration
from planteye_vision.data_chunks.data_chunk import GeneralDataChunk
from planteye_vision.data_chunks.data_chunk_data import *
from planteye_vision.data_chunks.metadata_chunk import MetadataChunkData
from planteye_vision.data_chunks.data_chunk_status import *
import requests


class RestAPIDataInlet(Inlet):
    """
    This class describes a data inlet that retrieves data over Rest API
    """
    def __init__(self, config: RestAPIInletConfiguration):
        self.config = config
        self.name = None
        self.type = None

    def apply_configuration(self):
        self.name = self.config.name
        self.type = self.config.type

    def retrieve_data(self):
        response = self.request_json()

        if response is None:
            logging.error('Data NOT read')
            return []

        if response.status_code == 200:
            return self.parse_data_chunks(response.json())
        else:
            logging.error('Data NOT read')
            return []

    def request_json(self):
        try:
            return requests.get(self.config.parameters['endpoint'])
        except Exception:
            return None

    def parse_data_chunks(self, json):
        data_chunks = []

        for data_chunk_name, data_chunk_content in json.items():
            name = data_chunk_content['name']
            chunk_type = data_chunk_content['type']
            parameters = data_chunk_content['parameters']
            data_chunk = GeneralDataChunk(name, chunk_type, parameters, hidden=self.config.hidden)
            [data_chunk.add_data(data_chunk_data) for data_chunk_data in self.parse_data(data_chunk_content)]

            data_chunks.append(data_chunk)

        return data_chunks

    def parse_data(self, data_chunk_dict):
        if 'data' not in data_chunk_dict.keys():
            return []

        if len(data_chunk_dict['data']) == 0:
            return []

        data_chunks = []

        for data_chunk_data_name, data_chunk_data_content in data_chunk_dict['data'].items():
            data_name = data_chunk_data_content['name']
            data_type = data_chunk_data_content['type']
            data_value = data_chunk_data_content['value']
            if data_type == 'base64_png':
                data_chunks.append(DataChunkImage(data_name, data_value, data_type))
            else:
                data_chunks.append(DataChunkValue(data_name, data_value, data_type))

        return data_chunks

    def parse_metadata(self, data_chunk_dict):
        if 'metadata' not in data_chunk_dict.keys():
            return []

        if len(data_chunk_dict['metadata']) == 0:
            return []

        metadata_chunks = []

        for metadata_chunk_name, metadata_chunk_content in data_chunk_dict['metadata'].items():
            data_name = metadata_chunk_content['name']
            data_value = metadata_chunk_content['value']
            metadata_chunks.append(MetadataChunkData(data_name, data_value))

        return metadata_chunks

    def parse_status(self, data_chunk_dict):
        if 'status' not in data_chunk_dict.keys():
            return []

        if len(data_chunk_dict['status']) == 0:
            return []

        status_chunks = []

        for status_chunk_name, status_chunk_content in data_chunk_dict['status'].items():
            status_code = status_chunk_content['code']
            operation_type = status_chunk_content['operation_type']
            if operation_type == 'image_capturing':
                status_chunks.append(CapturingStatus(status_code))
            elif operation_type == 'processor':
                status_chunks.append(ProcessorStatus(status_code))
            elif operation_type == 'opcua_poll':
                status_chunks.append(OPCUAReadStatus(status_code))
            elif operation_type == 'restapi_read':
                status_chunks.append(RestAPIReadStatus(status_code))

        return status_chunks





    def execute(self):
        return super().execute()
