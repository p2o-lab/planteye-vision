import logging
import cv2
from base64 import b64encode
from yaml import safe_load
import json
import time

from src.schema import validate_cfg
from src.cv2_camera_image_data_provider import CapturingDeviceLocalCamera
from src.capturing_device_baumer_vax import CapturingDeviceBaumerVAX
from src.restapi_endpoint import RestAPIEndpoint
from src.opcua_listener import OPCUAServer, OPCUANodePoller


class Vision:
    def __init__(self, data_provider):
        self.cfg = None
        self.cap_dev = None
        self.restapi_endpoint = None
        self.opcua_listeners = {}
        self.initialised = False
        self.data_provider = data_provider

    def import_config(self, cfg_file):
        with open(cfg_file) as config_file:
            cfg = safe_load(config_file)
        validation_res, validation_msg = validate_cfg(cfg, '../res/config_schema.json')
        if not validation_res:
            logging.warning(validation_msg)
        else:
            logging.info(validation_msg)
        self.cfg = cfg

    def initialise(self):
        if self.cfg is not None:
            self.initialise_opcua_listeners()
            self.initialise_capturing_device()
            self.initialise_restapi()
            self.initialised = True

    def initialise_capturing_device(self):
        if self.cfg['capturing_device']['type'] == 'local_camera_cv2':
            self.cap_dev = CapturingDeviceLocalCamera(cfg=self.cfg['capturing_device'])
        elif self.cfg['capturing_device']['type'] == 'baumer_camera_neoapi':
            self.cap_dev = CapturingDeviceBaumerVAX(cfg=self.cfg['capturing_device'])

    def initialise_restapi(self):
        self.restapi_endpoint = RestAPIEndpoint(self.cfg['api'])
        self.restapi_endpoint.add_url_rule('/get_frame', 'Get frame', self.api_rule_get_frame)

    def run(self):
        if self.initialised:
            vis.run_restapi()

    def run_restapi(self):
        if self.restapi_endpoint is not None:
            self.restapi_endpoint.run()

    def get_frame_from_camera(self):
        logging.debug('Get frame as str')
        begin_time_total = time.time()
        get_frame_status, frame_np, timestamp = self.cap_dev.capture_frame()
        capturing_time = int((time.time() - begin_time_total) * 1000)
        logging.debug('Capturing frame duration %i ms' % capturing_time)
        if not get_frame_status['code'] == 200:
            return None, get_frame_status

        frame_shape = frame_np.shape
        frame_colormap = 'BGR'
        frame = {'frame': frame_np, 'frame_shape': frame_shape, 'frame_colormap': frame_colormap}
        return frame, get_frame_status

    @staticmethod
    def convert_frame_to_str(frame):
        frame_np = frame['frame']
        begin_time = time.time()
        if frame_np.size == 0:
            return {'code': 500, 'message': 'Frame is empty'}, None
        try:
            _, frame_arr = cv2.imencode('.png', frame_np)
            frame_bytes = frame_arr.tobytes()
            frame_b64 = b64encode(frame_bytes)
            frame_str = frame_b64.decode('utf-8')
            conv_frame_status = {'code': 200, 'message': 'Conversion frame to str successful'}
        except Exception:
            frame_str = None
            conv_frame_status = {'code': 500, 'message': 'Error converting frame to str'}
        frame['frame'] = frame_str
        conversion_time = int((time.time() - begin_time) * 1000)
        logging.debug('Conversion duration %i ms' % conversion_time)
        return frame, conv_frame_status

    @staticmethod
    def get_timestamp():
        return int(round(time.time() * 1000))

    def get_metadata(self):
        metadata = self.cfg['metadata'].copy()
        for tag_name, tag_dict in self.cfg['metadata']['tags'].items():
            if tag_dict['source'] == 'opcua':
                tag_value_over_opcua = self.opcua_listeners[tag_name].get_value()
                metadata['tags'][tag_name]['value'] = tag_value_over_opcua
        get_metadata_status = {'code': 200, 'message': 'Metadata extraction/polling successful'}

        return metadata, get_metadata_status

    def get_labels(self):
        labels = self.cfg['labels'].copy()
        for label_name, label_dict in self.cfg['labels'].items():
            if label_dict['source'] == 'opcua':
                label_value_over_opcua = self.opcua_listeners[label_name].get_value()
                labels[label_name]['value'] = label_value_over_opcua
        get_labels_status = {'code': 200, 'message': 'Labels extraction/polling successful'}

        return labels, get_labels_status

    def initialise_opcua_listeners(self):
        for tag_name, tag_dict in self.cfg['metadata']['tags'].items():
            self.initialise_opcua_listener(tag_name, tag_dict)

        for label_name, label_dict in self.cfg['labels'].items():
            self.initialise_opcua_listener(label_name, label_dict)

    def initialise_opcua_listener(self, item_name, item_dict):
        if item_dict['source'] == 'opcua':
            opcua_server_url = item_dict['access_data']['server']
            opcua_server_username = item_dict['access_data']['username']
            opcua_server_pwd = item_dict['access_data']['password']
            node_name = item_name
            node_ns = item_dict['access_data']['node_ns']
            node_id = item_dict['access_data']['node_id']
            opcua_listener_obj = OPCUAServer(opcua_server_url, opcua_server_username, opcua_server_pwd)
            opcua_listener_obj.connect()
            self.opcua_listeners[item_name] = OPCUANodePoller(opcua_listener_obj, node_name, node_ns, node_id)

    def api_rule_get_frame(self):
        response = {'status': {}, 'camera': {}}

        response['camera']['information'] = self.cap_dev.get_camera_details()
        response['camera']['parameters'] = self.cap_dev.get_camera_configuration()

        timestamp = self.get_timestamp()
        response['timestamp'] = timestamp

        frame, get_frame_status = self.get_frame_from_camera()
        response['status']['get_frame_status'] = get_frame_status
        if get_frame_status['code'] == 200:
            frame, conv_frame_status = self.convert_frame_to_str(frame)
            response['frame'] = frame
            response['status']['conv_frame_status'] = conv_frame_status

        metadata, get_metadata_status = self.get_metadata()
        response['status']['get_metadata_status'] = get_metadata_status

        labels, get_labels_status = self.get_labels()
        response['status']['get_labels_status'] = get_labels_status

        json_dump = self.serialise_response(response)

        return json_dump

    @staticmethod
    def serialise_response(resp_dict):
        begin_time = time.time()
        json_dump = json.dumps(resp_dict, indent=4)
        serialisation_time = int((time.time() - begin_time) * 1000)
        logging.debug('Serialisation time %i ms' % serialisation_time)
        return json_dump


if __name__ == '__main__':
    vis = Vision()
    vis.import_config('../config.yaml')
    vis.initialise()
    vis.run()
