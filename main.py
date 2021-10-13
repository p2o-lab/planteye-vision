from src.capturing_device_local_camera import CapturingDeviceLocalCamera
from src.capturing_device_baumer_vax import CapturingDeviceBaumerVAX
from src.schema import validate_cfg
from yaml import safe_load
import logging
from flask import Flask, json
from time import time
import cv2
from base64 import b64encode
import numpy as np


def convert_frame_to_string(raw_frame: np.array) -> (bool, str):
    """
    Converts np.array into string variable.
    Based on code from https://jdhao.github.io/2020/03/17/base64_opencv_pil_image_conversion/
    :param raw_frame: np.array: Frame
    :return: Tuple of two variables:
    status: bool: True - frame converted successfully, False - otherwise
    frame: str: Frame converted into string
    """
    if raw_frame is None:
        return False, None
    try:
        _, frame_arr = cv2.imencode('.png', raw_frame)
        frame_bytes = frame_arr.tobytes()
        frame_b64 = b64encode(frame_bytes)
        frame_str = frame_b64.decode('utf-8')
        return True, frame_str
    except Exception:
        return False, None


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    with open('config.yaml') as config_file:
        cfg = safe_load(config_file)
    validation_res, validation_msg = validate_cfg(cfg, 'src/config_schema.json')
    if not validation_res:
        print(validation_msg)
    #   exit(1)

    if cfg['capturing_device']['type'] == 'local_camera_cv2':
        cap_dev = CapturingDeviceLocalCamera(cfg=cfg)
    elif cfg['capturing_device']['type'] == 'baumer_camera_neoapi':
        cap_dev = CapturingDeviceBaumerVAX(cfg=cfg)

    api = Flask(__name__)
    if 'metadata' in cfg:
        metadata = cfg['metadata']
    else:
        metadata = {}

    if 'labels' in cfg:
        labels = cfg['labels']
    else:
        labels = {}

    vision_settings = {'capturing_settings': cfg['capturing_device']}

    @api.route('/get_frame', methods=['GET'])
    def get_frame():
        logging.debug('get_frame request received')
        begin_time_total = time()
        ret, frame_raw, timestamp = cap_dev.capture_frame()
        if not ret['code'] == 200:
            return ret['message'], 500
        capturing_time = int((time() - begin_time_total) * 1000)

        begin_time = time()
        conv_status, frame_str = convert_frame_to_string(frame_raw)
        conversion_time = int((time() - begin_time) * 1000)
        if not conv_status:
            return 'Cannot convert frame to string', 500

        begin_time = time()
        frame = {'frame': frame_str,
                 'colorspace': 'BGR',
                 'frame_shape': frame_raw.shape}
        data = {'frame': frame, 'timestamp': timestamp, 'metadata': metadata, 'labels': labels, 'status': ret}
        resp = json.dumps(data)
        serialisation_time = int((time() - begin_time) * 1000)
        logging.debug('Total execution time of request get_frame %i ms (capturing %i, conversion %i, serialisation %i)'
                      % (int((time() - begin_time_total) * 1000), capturing_time, conversion_time, serialisation_time))

        return resp


    @api.route('/get_camera_status', methods=['GET'])
    def get_camera_status():
        logging.debug('get_camera_status request received')
        begin_time = time()
        resp = json.dumps(cap_dev.get_status())
        logging.debug('Total execution time of request get_camera_status %i ms' % int((time() - begin_time) * 1000))
        return resp


    try:
        api.run(host=cfg['api']['url'], port=cfg['api']['port'])
    except PermissionError:
        logging.error('Cannot not start flask server with given configuration')
