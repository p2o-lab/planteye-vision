from src.transform.data_transformer import DataTransformer
import time
import logging
import json


class DictSerialiser(DataTransformer):

    def transform_data(self, resp_dict):
        logging.debug('Serialisation...')
        begin_time = time.time()
        json_dump = json.dumps(resp_dict, indent=4)
        serialisation_time = int((time.time() - begin_time) * 1000)
        logging.debug('Serialisation time %i ms' % serialisation_time)
        json_dump_status = {'code': 200, 'message': 'Serialisation in json successful'}
        return json_dump, json_dump_status
