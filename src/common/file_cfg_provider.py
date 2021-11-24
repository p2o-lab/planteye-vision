from src.common.cfg_provider import CfgProvider
from yaml import safe_load
from src.common.schema import validate_cfg
import logging


class FileCfgProvider(CfgProvider):
    def __init__(self, cfg_file):
        self.cfg_file = cfg_file

    def provide_cfg(self):
        with open(self.cfg_file) as config_file:
            cfg = safe_load(config_file)
        return cfg
