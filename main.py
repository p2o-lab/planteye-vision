from src.capturing_device import CapturingDevice, convert_frame_to_string
from src.schema import validate_cfg
from yaml import safe_load
import logging
from flask import Flask, json
from time import time

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    # Import and validate config
    with open('config.yaml') as config_file:
        cfg = safe_load(config_file)
    validation_res, validation_msg = validate_cfg(cfg, 'src/config_schema.json')
    if not validation_res:
        print(validation_msg)
    #   exit(1)

    cap_dev = CapturingDevice(cfg=cfg)
    cap_dev.start()

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
        capturing_time = int((time() - begin_time_total) * 1000)

        begin_time = time()
        frame_str = convert_frame_to_string(frame_raw)
        conversion_time = int((time() - begin_time) * 1000)

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
        resp = json.dumps(cap_dev.get_camera_status())
        logging.debug('Total execution time of request get_camera_status %i ms' % int((time() - begin_time) * 1000))
        return resp


    try:
        api.run(host=cfg['api']['url'], port=cfg['api']['port'])
    except PermissionError:
        logging.error('Could not start flask server with given configuration')
