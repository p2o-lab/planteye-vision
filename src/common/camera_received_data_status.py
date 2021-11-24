class CameraReceivedDataStatus:
    def __init__(self, code):
        self.code = code
        self.msg = 'unknown'
        self.infer_msg()

    def infer_msg(self):
        if self.code == 0:
            self.msg = 'Data captured'
        elif self.code == 99:
            self.msg = 'Data NOT captured. Error unspecified'
        elif self.code == 1:
            self.msg = 'Data NOT captured. Camera busy'
        elif self.code == 2:
            self.msg = 'Data NOT captured. Camera NOT initialised'
        else:
            self.msg = 'Unknown status'

    def as_dict(self):
        return {'capturing_status':
                    {'code': self.code,
                     'message': self.msg}}
