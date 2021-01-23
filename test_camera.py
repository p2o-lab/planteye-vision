from src.capturing_device import CapturingDevice
from influxdb_writer import InfluxDBWriter
from Buffer import Buffer
import schema
import yaml
import os

if __name__ == '__main__':

    # Import config
    cfg_file = 'config.yaml'
    with open(cfg_file) as config_file:
        cfg = yaml.safe_load(config_file)

    # Validate config
    validation_res, validation_msg = schema.validate_cfg(cfg)
    if not validation_res:
        print(validation_msg)
        exit(1)

    # Start capturing
    cap_dev = CapturingDevice(cfg=cfg, buffer=None)
    cap_dev.test_camera()
