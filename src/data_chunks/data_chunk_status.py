from abc import ABC, abstractmethod


class DataChunkStatus(ABC):
    @abstractmethod
    def as_dict(self):
        pass


class CapturingStatus(DataChunkStatus):
    def __init__(self, code: int):
        self.operation = 'Frame capturing'
        self.operation_type = 'image_capturing'
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
        return {self.operation: {'type': self.operation_type, 'code': self.code, 'message': self.message}}

    def get_message(self):
        return self.message


class ProcessorStatus(DataChunkStatus):
    def __init__(self, code: int):
        self.operation = 'Processor'
        self.operation_type = 'processor'
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
        return {self.operation: {'type': self.operation_type, 'code': self.code, 'message': self.message}}
    

class OPCUAReadStatus(DataChunkStatus):
    def __init__(self, code: int):
        self.operation = 'Reading process value over OPC UA'
        self.operation_type = 'opcua_poll'
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
        return {self.operation: {'type': self.operation_type, 'code': self.code, 'message': self.message}}


class RestAPIReadStatus(DataChunkStatus):
    def __init__(self, code: int):
        self.operation = 'Reading data over Rest API'
        self.operation_type = 'restapi_read'
        self.code = code
        self.message = 'Unknown state'
        self.infer_message()

    def infer_message(self):
        if self.code == 200:
            self.message = 'Data read'
        elif self.code == 500:
            self.message = 'Data NOT read: endpoint returned internal error'
        elif self.code == 99:
            self.message = 'Data NOT read: unknown error'
        elif self.code == 100:
            self.message = 'Invalid configuration'

    def as_dict(self):
        return {self.operation: {'type': self.operation_type, 'code': self.code, 'message': self.message}}
