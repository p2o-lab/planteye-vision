from src.capturing_device import CapturingDevice
import schema
import yaml

if __name__ == '__main__':

    # Import config
    cfg_file = 'config.yaml'
    with open(cfg_file) as config_file:
        cfg = yaml.safe_load(config_file)

    # Validate config
    json_schema = 'src/config_schema.json'
    validation_res, validation_msg = schema.validate_cfg(cfg, json_schema)
    if not validation_res:
        print(validation_msg)
        exit(1)

    # Start capturing
    cap_dev = CapturingDevice(cfg=cfg)
    cap_dev.connect()

