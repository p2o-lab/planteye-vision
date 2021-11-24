class ReceivedImageData:
    def __init__(self, timestamp, data, status):
        self.timestamp = timestamp
        self.data = data
        self.status = status

    def as_dict(self):
        return {'frame':
                    {'timestamp': self.timestamp, 'data': self.data, 'status': self.status}}
