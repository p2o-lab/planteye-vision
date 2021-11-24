from abc import ABC, abstractmethod


class DataReceiver(ABC):

    @abstractmethod
    def receive_data(self):
        pass

    @abstractmethod
    def get_details(self):
        pass

    @abstractmethod
    def configure(self):
        pass
