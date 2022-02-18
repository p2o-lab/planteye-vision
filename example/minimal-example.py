from planteye_vision.pipeline_execution.pipeline_executor import PipeLineExecutor
from planteye_vision.configuration.planteye_configuration import PlantEyeConfiguration
from yaml import safe_load
import logging

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

path_to_config_file = 'config_minimal_restapi.yaml'
with open(path_to_config_file) as config_file:
    config_dict = safe_load(config_file)

config = PlantEyeConfiguration()
config.read(config_dict)
PipeLineExecutor(config).run()
