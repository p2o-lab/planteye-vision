from src.pipeline_execution.pipeline_executor import PipeLineExecutor
from src.configuration.config_provider import FileConfigProvider


from abc import abstractmethod, ABC


class Vision(ABC):

    @abstractmethod
    def run(self):
        pass


class LocalVision(Vision):
    def __init__(self, path_to_config_file):
        self.path_to_config_file = path_to_config_file
        self.cfg_provider = FileConfigProvider('config', self.path_to_config_file)
        self.pipeline_exec = PipeLineExecutor(self.cfg_provider)

    def run(self):
        self.pipeline_exec.run()
