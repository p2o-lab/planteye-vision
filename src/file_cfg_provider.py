from src.cfg_provider import CfgProvider
from yaml import safe_load
from src.schema import validate_cfg
import logging

PATH_TO_VALIDATION_SCHEME = '../res/config_schema.json'


class FileCfgProvider(CfgProvider):
    def __init__(self, cfg_file):
        self.cfg_file = cfg_file

    def provide_cfg(self):
        with open(self.cfg_file) as config_file:
            cfg = safe_load(config_file)
        validation_res, validation_msg = validate_cfg(cfg, PATH_TO_VALIDATION_SCHEME)
        if not validation_res:
            logging.warning(validation_msg)
        else:
            logging.info(validation_msg)
        return cfg
