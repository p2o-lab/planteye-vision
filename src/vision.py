from src.pipeline_execution.pipeline_executor import PipeLineExecutor
from src.configuration.config_provider import FileConfigProvider

if __name__ == '__main__':
    cfg_provider = FileConfigProvider('config', '../src/config.yaml')
    pipeline_exec = PipeLineExecutor(cfg_provider)
    pipeline_exec.run()