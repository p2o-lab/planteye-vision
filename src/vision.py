from src.pipeline_execution.pipeline_executor import PipeLineExecutor
from src.configuration.config_provider import FileConfigProvider
from src.configuration.planteye_configuration import PlantEyeConfiguration
from yaml import safe_load

from abc import abstractmethod, ABC


class Vision(ABC):

    @abstractmethod
    def run(self):
        pass


class LocalVision(Vision):
    def __init__(self, path_to_config_file):
        self.path_to_config_file = path_to_config_file
        with open(path_to_config_file) as config_file:
            config_dict = safe_load(config_file)
        self.config = PlantEyeConfiguration()
        self.config.read(config_dict)
        self.pipeline_exec = PipeLineExecutor(self.config)

    def run(self):
        self.pipeline_exec.run()
