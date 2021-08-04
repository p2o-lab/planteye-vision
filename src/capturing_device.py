from abc import ABC, abstractmethod


class CapturingDevice(ABC):
    """
    This class describes generic capturing device
    """

    @abstractmethod
    def capture_frame(self):
        pass

    @abstractmethod
    def get_status(self):
        pass
