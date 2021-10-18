from src.transform.data_transformer import DataTransformer
import cv2
import time
from base64 import b64encode
import logging


class ImageDataSerialiser(DataTransformer):

    def transform_data(self, frame_np):
        logging.debug('Converting single frame to str...')
        begin_time = time.time()
        if frame_np.size == 0:
            return {'code': 500, 'message': 'Frame is empty'}, None
        try:
            _, frame_arr = cv2.imencode('.png', frame_np)
            frame_bytes = frame_arr.tobytes()
            frame_b64 = b64encode(frame_bytes)
            frame_str = frame_b64.decode('utf-8')
            conv_frame_status = {'code': 200, 'message': 'Conversion frame to str successful'}
            logging.debug('Conversion successful')
        except Exception:
            frame_str = None
            conv_frame_status = {'code': 500, 'message': 'Error converting frame to str'}
            logging.debug('Conversion NOT successful')
        conversion_time = int((time.time() - begin_time) * 1000)
        logging.debug('Conversion duration %i ms' % conversion_time)
        return frame_str, conv_frame_status
