from abc import ABC, abstractmethod
import numpy as np
import cv2
import base64


class DataChunkData(ABC):
    @abstractmethod
    def as_dict(self):
        pass


class DataChunkValue(DataChunkData):
    def __init__(self, name: str, value, data_type: str):
        self.name = name
        self.value = value
        self.data_type = data_type

    def as_dict(self):
        return {'name': self.name, 'value': self.value, 'type': self.data_type}


class DataChunkImage(DataChunkData):
    def __init__(self, name: str, value, data_type: str):
        self.name = name
        if isinstance(value, np.ndarray):
            self.value = value
        elif isinstance(value, str):
            self.value = self.base64_decoder(value)
        self.data_type = data_type

    def as_dict(self):
        return {'name': self.name, 'value': self.value, 'type': self.data_type}

    def encode_as_base64(self):
        if isinstance(self.value, np.ndarray):
            _, frame_arr = cv2.imencode('.png', self.value)
            self.value = base64.b64encode(frame_arr).decode("utf-8")

    @staticmethod
    def base64_decoder(frame: str):
        image_data = base64.b64decode(frame)
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        np_array = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)
        return np_array
