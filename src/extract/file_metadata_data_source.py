from src.extract.metadata_data_source import MetadataDataSource
from src.common.cfg_provider import CfgProvider
from time import time, sleep
import logging
from src.extract.StaticMetadataObject import StaticMetadataObject
from src.extract.OPCUAMetadataObject import OPCUAMetadataObject
from src.common.file_cfg_provider import FileCfgProvider


class FileMetadataDataSource(MetadataDataSource):
    """
    This class describes metadata provider where metadata originates directly from config file
    """
    def __init__(self):
        super().__init__()
        self.tags = {}
        self.output_dict = None

    def configure(self):
        self.output_dict = self.cfg.copy()
        if self.cfg is not None:
            for tag_name, tag_dict in self.cfg['tags'].items():
                if tag_dict['source'] == 'static':
                    self.tags[tag_name] = StaticMetadataObject(tag_name, tag_dict)
                if tag_dict['source'] == 'opcua':
                    self.tags[tag_name] = OPCUAMetadataObject(tag_name, tag_dict)
                    self.tags[tag_name].initialise_opcua_listener()

    def receive_data(self) -> (bool, dict, int):
        if self.output_dict:
            for tag_name, tag_dict in self.output_dict['tags'].items():
                tag_dict['value'] = self.tags[tag_name].receive_data()

        timestamp = int(round(time() * 1000))
        return {'code': 200, 'message': 'Metadata extraction/polling successful'}, self.output_dict, timestamp

    def get_details(self):
        pass

    def import_config(self, cfg_provider: CfgProvider):
        super().import_config(cfg_provider)


logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

if __name__ == '__main__':
    cfg_provider = FileCfgProvider('../config.yaml')
    metadata_provider = FileMetadataDataSource()
    metadata_provider.import_config(cfg_provider)
    metadata_provider.configure()
    while True:
        metadata_provider.receive_data()
        sleep(1)
