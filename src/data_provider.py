from abc import ABC, abstractmethod


class DataProvider (ABC):

    @abstractmethod
    def provide_data(self):
        pass

    @abstractmethod
    def get_data_source_details(self):
        pass