class ImageFrame:
    def __init__(self, frame=None, colormap=None):
        self.frame = frame
        self.shape = frame.shape
        self.colormap = colormap

    def as_dict(self):
        return {'frame': {'frame_np': self.frame, 'shape': self.shape, 'colormap': self.colormap}}
