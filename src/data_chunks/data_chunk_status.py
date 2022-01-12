from abc import ABC, abstractmethod


class DataChunkStatus(ABC):
    @abstractmethod
    def as_dict(self):
        pass


class CapturingStatus(DataChunkStatus):
    def __init__(self, code: int):
        self.operation = 'Frame capturing'
        self.code = code
        self.message = 'Unknown state'
        self.infer_message()

    def infer_message(self):
        if self.code == 0:
            self.message = 'Frame captured'
        elif self.code == 1:
            self.message = 'Frame NOT captured: capturing device is NOT initialised yet'
        elif self.code == 2:
            self.message = 'Frame NOT captured: capturing device is busy'
        elif self.code == 99:
            self.message = 'Frame NOT captured: unknown error'
        elif self.code == 100:
            self.message = 'Invalid configuration'

    def as_dict(self):
        return {self.operation: {'code': self.code, 'message': self.message}}

    def get_message(self):
        return self.message


class OPCUAReadStatus(DataChunkStatus):
    def __init__(self, code: int):
        self.operation = 'Reading process value over OPC UA'
        self.code = code
        self.message = 'Unknown state'
        self.infer_message()

    def infer_message(self):
        if self.code == 0:
            self.message = 'Process value read'
        elif self.code == 1:
            self.message = 'Process value NOT read: error 1'
        elif self.code == 2:
            self.message = 'Process value NOT read: error 2'
        elif self.code == 99:
            self.message = 'Process value NOT read: unknown error'
        elif self.code == 100:
            self.message = 'Invalid configuration'

    def as_dict(self):
        return {self.operation: {'code': self.code, 'message': self.message}}


class ProcessorStatus(DataChunkStatus):
    def __init__(self, code: int):
        self.operation = 'Processor'
        self.code = code
        self.message = 'Unknown state'
        self.infer_message()

    def infer_message(self):
        if self.code == 0:
            self.message = 'Processing value successful'
        elif self.code == 99:
            self.message = 'Value NOT processes: unknown error'
        elif self.code == 100:
            self.message = 'Invalid configuration'

    def as_dict(self):
        return {self.operation: {'code': self.code, 'message': self.message}}