from abc import ABC, abstractmethod


class DataSource (ABC):

    @abstractmethod
    def receive_data(self):
        pass

    @abstractmethod
    def get_details(self):
        pass
