import logging
import time

from src.forward.restapi_endpoint import RestAPIEndpoint
from transform.image_data_serialiser import ImageDataSerialiser
from transform.dict_serialiser import DictSerialiser
from common.file_cfg_provider import FileCfgProvider
from receive.file_metadata_data_receiver import FileMetadataDataReceiver
from receive.opencv_generic_image_data_receiver import OpenCVGenericImageDataReceiver

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)


class Vision:
    def __init__(self, data_receiver):
        self.cfg_provider = cfg_provider
        self.cfg = self.cfg_provider.provide_cfg()

        self.data_receiver = data_receiver
        #self.metadata_datasource = metadata_datasource
        self.restapi_endpoint = None

        self.initialised = False

    def initialise(self):
        if self.cfg is not None:
            self.initialise_data_receiver()
            #self.initialise_metadata_source()
            self.initialise_restapi()
            self.initialised = True

    def initialise_data_receiver(self):
        self.data_receiver.import_config(cfg_provider, 'data_receiver')
        self.data_receiver.configure()

    def initialise_metadata_source(self):
        #self.metadata_datasource.import_config(self.cfg_provider)
        #self.metadata_datasource.configure()
        pass

    def initialise_restapi(self):
        api_name = self.cfg['data_sink']['name']
        api_endpoint = self.cfg['data_sink']['endpoint']

        self.restapi_endpoint = RestAPIEndpoint(api_name)
        self.restapi_endpoint.add_url_rule(api_endpoint, api_name, self.api_response)

    def api_response(self):
        if not self.initialised:
            resp_dict = {'code': 500, 'message': 'PlantEye/Vision is not yet initialised'}
            return DictSerialiser().transform_data(resp_dict)

        frame_status, frame_dict, frame_timestamp = self.data_receiver.receive_data()
        data_provider_conf_dict = self.data_receiver.get_configuration()
        data_source_details_dict = self.data_receiver.get_details()
        img_str, img_str_status = ImageDataSerialiser().transform_data(frame_dict['frame'])
        frame_dict['frame'] = img_str
        data_source_dict = {'configuration': self.cfg['data_source'],
                            'parameters': data_provider_conf_dict,
                            'details': data_source_details_dict, }

        #metadata_status, metadata, metadata_timestamp = self.metadata_datasource.receive_data()

        status_dict = {'frame_capturing': frame_status,
                       'frame_conversion_to_str': img_str_status,
                       'metadata_collection': None,
                       }

        resp_dict = {'frame': frame_dict,
                     'data_source': data_source_dict,
                     'metadata': None,
                     'status': status_dict}

        return DictSerialiser().transform_data(resp_dict)

    def run_restapi(self):
        if self.restapi_endpoint is not None:
            api_host = self.cfg['data_sink']['url']
            api_port = self.cfg['data_sink']['port']
            self.restapi_endpoint.run(api_host, api_port)


if __name__ == '__main__':
    cfg_provider = FileCfgProvider('config.yaml')
    #metadata_source = FileMetadataDataReceiver()
    image_data_receiver = OpenCVGenericImageDataReceiver()
    vis = Vision(image_data_receiver)
    vis.initialise()
    vis.run_restapi()
