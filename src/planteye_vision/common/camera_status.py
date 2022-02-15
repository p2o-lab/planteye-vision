from planteye_vision.common.timestamp import get_timestamp


class CameraStatus:
    def __init__(self):
        self.initialised = False
        self.configured = False
        self.fully_configured = False
        self.connected = False
        self.capturing = False

    def as_dict(self):
        return {
            'camera_status': {
                'initalised': self.initialised,
                'configured': self.configured,
                'fully_configured': self.fully_configured,
                'connected': self.connected,
                'capturing': self.capturing,
            },
            'timestamp': get_timestamp,
            }
