from src.capturing_device import CapturingDevice
from src.schema import validate_cfg
from yaml import safe_load
import logging
from flask import Flask, json

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

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

    metadata = {'tags': cfg['metadata'], 'capturing_device': cfg['capturing_device']}

    @api.route('/get_frame', methods=['GET'])
    def get_frame():
        ret, frame, timestamp = cap_dev.capture_frame()
        data = {'frame': frame, 'timestamp': timestamp, 'metadata': metadata, 'status': ret}
        return json.dumps(data)


    @api.route('/get_camera_status', methods=['GET'])
    def get_camera_status():
        return json.dumps(cap_dev.get_camera_status())


    try:
        api.run(host=cfg['api']['url'], port=cfg['api']['port'])
    except PermissionError:
        logging.error('Could not start flask server with given configuration')


