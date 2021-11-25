from abc import ABC, abstractmethod


class Inlet(ABC):
    @abstractmethod
    def import_configuration(self, inlet_configuration_provider):
        pass

    @abstractmethod
    def apply_configuration(self):
        pass

    @abstractmethod
    def retrieve_data(self):
        pass