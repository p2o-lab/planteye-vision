from abc import ABC, abstractmethod


class DataTransformer (ABC):

    @abstractmethod
    def transform_data(self, input_data):
        pass
