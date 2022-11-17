from abc import ABC, abstractmethod


class Shell(ABC):

    @abstractmethod
    def apply_configuration(self):
        pass

    @abstractmethod
    def attach_callback(self, callback):
        pass

    @abstractmethod
    def attach_silent_execution_callback(self, callback):
        pass
