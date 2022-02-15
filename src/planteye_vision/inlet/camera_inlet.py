from abc import abstractmethod
from planteye_vision.inlet.inlet import Inlet
from planteye_vision.common.camera_status import CameraStatus
from planteye_vision.configuration.inlet_configuration import CameraConfiguration


class CameraInlet(Inlet):
    """
    This class describes a generic capturing device connected via OpenCV
    """
    def __init__(self, config: CameraConfiguration):
        self.config = config
        self.name = None
        self.type = None
        self.camera_object = None
        self.camera_status = CameraStatus()

    def apply_configuration(self):
        configured_all_parameters = True
        for parameter, value in self.config.parameters.items():
            configured_all_parameters *= self.set_parameter(parameter, value)
        self.camera_status.fully_configured = configured_all_parameters
        self.name = self.config.name
        self.type = self.config.type
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

    def execute(self):
        return super().execute()
