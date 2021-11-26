from abc import abstractmethod
from src.inlet.inlet import Inlet
from src.common.camera_status import CameraStatus
from src.configuration.configuration import CameraConfiguration
from src.configuration.config_provider import ConfigProvider


class CameraInlet(Inlet):
    """
    This class describes a generic capturing device connected via OpenCV
    """
    def __init__(self):
        self.config = CameraConfiguration()
        self.name = None
        self.type = None
        self.camera_object = None
        self.camera_status = CameraStatus()

    def import_configuration(self, config_provider: ConfigProvider):
        self.name = config_provider.provide_name()
        self.config.read(config_provider)
        self.type = self.config.type

    def apply_configuration(self):
        configured_all_parameters = True
        for parameter, value in self.config.parameters.items():
            configured_all_parameters *= self.set_parameter(parameter, value)
        self.camera_status.fully_configured = configured_all_parameters
        self.camera_status.configured = True

    @abstractmethod
    def set_parameter(self, parameter: str, value: [int, float, str, bool]):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def retrieve_data(self):
        pass

    @abstractmethod
    def get_camera_info(self):
        pass
