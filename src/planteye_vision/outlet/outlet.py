from abc import ABC, abstractmethod


class Outlet(ABC):
    @abstractmethod
    def import_configuration(self, outlet_configuration_provider):
        pass

    @abstractmethod
    def apply_configuration(self):
        pass

    @abstractmethod
    def provide_data(self, data):
        pass
