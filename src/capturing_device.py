import cv2
import logging
from time import sleep, time
import threading
from base64 import b64encode
from numpy import ndarray


class CapturingDevice:
    """
    This class describes capturing device
    """

    def __init__(self, cfg):

        self._cfg = cfg
        self._camera = None
        self._initialised = False
        self._capturing = False
        self._exit = False
        self._frames_taken = 0

    def _configure(self):
        """
        This function configures capturing device according to parameters from the config
        :return:  Status of configuration process: True - Successful, False - Unsuccessful
        """
        if self._cfg['capturing_device']['type'] == 'local_camera_cv2':
            return self._configure_cv2()
        elif self._cfg['capturing_device']['type'] == 'local_camera_jetson':
            return self._configure_jetson()
        elif self._cfg['capturing_device']['type'] == 'rtmp':
            return self._configure_rtmp()

    def _configure_cv2(self):
        """
        This function configures local capturing device by means of methods of OpenCV package
        :return:  Status of configuration process: True - Successful, False - Unsuccessful
        """
        res = True
        for parameter, value in self._cfg['capturing_device']['parameters'].items():
            res *= self._set_parameter_cv2(parameter, value)
        return res

    def _configure_jetson(self):
        """
        This function configures local capturing device by means of methods of NVidia Jetson package
        :return:  Status of configuration process: True - Successful, False - Unsuccessful
        """
        # TODO: add support
        return False

    def _configure_rtmp(self):
        """
        This function configures remotes capturing device via rtmp
        :return:  Status of configuration process: True - Successful, False - Unsuccessful
        """
        # TODO: add support
        return False

    def _set_parameter_cv2(self, parameter, requested_value):
        """
        This function sets parameter of capturing device and checks if it was set
        :return: Status of configuration process: True - Successful, False - Unsuccessful
        """
        # Get parameter from opencv2 based on its name
        par = None
        try:
            exec("par = cv2.%s" % parameter)
        except:
            logging.warning('Parameter (' + parameter + ') is not found by name')
            return False

        initial_value = self._camera.get(par)
        if not initial_value:
            logging.warning('Parameter (' + parameter + ') is not supported by VideoCapture instance')
            return False

        backend_support = self._camera.set(par, requested_value)
        if not backend_support:
            logging.warning('Parameter (' + parameter + ') cannot be changed (' + str(requested_value) + ')')
            return False

        new_value = self._camera.get(par)
        if new_value == requested_value:
            logging.info('Parameter (' + parameter + ') set to ' + str(new_value))
            return True
        else:
            logging.warning('Setting parameter (' + parameter + ') unsuccessful. Actual value ' + str(new_value))
            return False

    def _initialise(self):
        """
        This function initialise the capturing device
        :return: Status of initialisation process: True - Successful, False - Unsuccessful
        """

        if self._cfg['capturing_device']['type'] == 'local_camera_cv2':
            self._initialise_local_camera_cv2()
        elif self._cfg['capturing_device']['type'] == 'local_camera_jetson':
            self._initialise_local_camera_jetson()
        elif self._cfg['capturing_device']['type'] == 'rtmp':
            self._initialise_rtmp()

        return self._initialised

    def _initialise_local_camera_cv2(self):
        """
        This function initialise local capturing device connected via OpenCV package
        :return: Status of initialisation process: True - Successful, False - Unsuccessful
        """
        self._camera = cv2.VideoCapture(self._cfg['capturing_device']['connection']['device_id'])
        if self._camera.isOpened():
            logging.info('Capturing device initialised successfully')
            self._initialised = True
        else:
            logging.error('Capturing device initialisation failed')
            self._initialised = False

    def _initialise_local_camera_jetson(self):
        """
        This function initialise local capturing device connected via NVidia Jetson package
        :return: Status of initialisation process: True - Successful, False - Unsuccessful
        """
        # TODO: add support
        self._camera = None
        self._initialised = False

    def _initialise_rtmp(self):
        """
        This function initialise remote capturing device connected via RTMP
        :return: Status of initialisation process: True - Successful, False - Unsuccessful
        """
        # TODO: add support
        self._camera = None
        self._initialised = False

    def start(self):
        """
        This function starts connectivity thread
        :return:
        """
        ret = self._initialise()

        if not self._initialised:
            return

        self._configure()

    def stop(self):
        self._exit = True
        self._release()

    def _release(self):
        """
        This function releases the capturing device
        :return: Status of release process: True - Successful, False - Unsuccessful
        """
        if self._initialised:

            if self._cfg['capturing_device']['type'] == 'local_camera_cv2':
                res = self._release_cv2()
            elif self._cfg['capturing_device']['type'] == 'local_camera_jetson':
                res = self._release_jetson()
            elif self._cfg['capturing_device']['type'] == 'rtmp':
                res = self._release_cv2()
            else:
                logging.error('Capturing device type specified in config is unknown')
                res = False

            if not res:
                logging.warning('Capturing device could not be released')
                self._initialised = True
            else:
                logging.info('Captured device released successfully')
                self._initialised = False

    def _release_cv2(self):
        """
        This function releases the capturing device initialised via OpenCV package
        :return: Status of release process: True - Successful, False - Unsuccessful
        """
        return self._camera.release()

    def _release_jetson(self):
        """
        This function releases the capturing device initialised via Jetson Nano package
        :return: Status of release process: True - Successful, False - Unsuccessful
        """
        # TODO: add support
        return False

    def exit(self):
        """
        This function stops capturing and releases the capturing device
        :return:
        """
        logging.info('Disconnecting from capturing device ...')
        self._exit = True
        self._release()
        logging.info('Disconnection successful')

    def _start_capturing(self):
        """
        This function begins the thread with frame capturing
        :return:
        """
        self._capturing = True
        threading.Thread(target=self.capture_frame, args=[]).start()

    def capture_frame(self):
        """
        This function captures a frame from the capturing device
        :return:
        """
        if self._capturing:
            status = {'code': 500, 'message': 'capturing device busy'}
            return status, None, int(round(time() * 1000))

        # Try to reconnect first
        if not self._initialised:
            self.start()

        if not self._initialised:
            status = {'code': 500, 'message': 'capturing device not initialised'}
            return status, None, int(round(time() * 1000))

        if self._cfg['capturing_device']['type'] == 'local_camera_cv2':
            ret, frame, timestamp = self._capture_frame_cv2()
        elif self._cfg['capturing_device']['type'] == 'local_camera_jetson':
            ret, frame, timestamp = self._capture_frame_local_jetson()
        elif self._cfg['capturing_device']['type'] == 'rtmp':
            ret, frame, timestamp = self._capture_frame_cv2()
        else:
            ret, frame, timestamp = False, None, int(round(time() * 1000))

        if ret:
            status = {'code': 200, 'message': 'frame captured'}
            return status, frame, timestamp
        else:
            status = {'code': 500, 'message': 'error capturing frame'}
            return status, frame, timestamp

    def _capture_frame_cv2(self):
        """
        This function gets frame from capturing device and returns frame variable with
        :return: Return frame
        """
        ret, frame_raw = self._camera.read()
        timestamp = int(round(time() * 1000))
        if ret:
            logging.info('Frame captured')
        else:
            frame_raw = None
            logging.error('Capturing frame failed')

        self._capturing = False
        return ret, frame_raw, timestamp

    def _capture_frame_local_jetson(self):
        """
        This function captures a frame from a capturing device by means of NVidia Jetson package
        :return:
        """
        # TODO: add support
        return False, None, None

    def get_camera_status(self):
        if self._initialised:
            msg = 'camera initialised'
        else:
            msg = 'camera not initialised'
        initialisation_status = {'status': self._initialised, 'message': msg}

        if self._capturing:
            msg = 'camera capturing'
        else:
            msg = 'camera idle'
        capturing_status = {'status': self._capturing, 'message': msg}

        return {'status': {'initialisation': initialisation_status, 'capturing': capturing_status}, 'timestamp': int(round(time() * 1000))}


def convert_frame_to_string(raw_frame):
    # https://jdhao.github.io/2020/03/17/base64_opencv_pil_image_conversion/

    _, frame_arr = cv2.imencode('.png', raw_frame)
    frame_bytes = frame_arr.tobytes()
    frame_b64 = b64encode(frame_bytes)
    frame_str = frame_b64.decode('utf-8')
    return frame_str
