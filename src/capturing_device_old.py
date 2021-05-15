import cv2
import logging
import time
import threading
import copy
from os import path
from json import dump


class CapturingDevice:
    """
    This class describes capturing device
    """

    def __init__(self, cfg):
        # Module name
        self.module_name = 'CapDev'

        # Configuration
        self.cfg = cfg
        self.capture_type = cfg['capturing_device']['type']
        self.storage_type = cfg['data_storage']['type']
        self.capturing_interval = self.cfg['capturing_device']['capturing_interval']

        self._initialised = False
        self._capturing_thread = None

        # Capturing device object
        self.camera = None

        # Stop and exit flags
        self._exit = False
        self._stop = False

        # Frame counter
        self._current_frame_id = 0

    def _configure(self):
        """
        This function configures capturing device according to parameters from the config
        :return:  Status of configuration process: True - Successful, False - Unsuccessful
        """
        if self.capture_type == 'local_camera_cv2':
            return self._configure_cv2()
        elif self.capture_type == 'local_camera_jetson':
            return self._configure_jetson()
        elif self.capture_type == 'rtmp':
            return self._configure_rtmp()

    def _configure_cv2(self):
        """
        This function configures local capturing device by means of methods of OpenCV package
        :return:  Status of configuration process: True - Successful, False - Unsuccessful
        """
        status = True
        for parameter, value in self.cfg['capturing_device']['parameters'].items():
            res = self._set_parameter_cv2(parameter, value)
            status = status * res
        return status

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

    def _set_parameter_cv2(self, parameter, value):
        """
        This function sets parameter of capturing device and checks if it was set
        :return: Status of configuration process: True - Successful, False - Unsuccessful
        """
        # Get parameter from opencv2 based on its name
        par = None
        exec("par = cv2.%s" % parameter)
        initial_value = self.camera.get(par)
        if not initial_value:
            logging.warning('Parameter (' + parameter + ') is not supported by VideoCapture instance')
            return False
        backend_support = self.camera.set(par, value)
        if not backend_support:
            logging.warning(
                self.module_name + 'Parameter (' + parameter + ') cannot be changed (' + str(value) + ')')
            return False
        new_value = self.camera.get(par)
        if new_value == initial_value:
            logging.warning('Parameter (' + parameter + ') has not changed (' + str(value) + ')')
            return False
        else:
            logging.info( 'Parameter (' + parameter + ') changed to ' + str(value))
            return True

    def _initialise(self):
        """
        This function initialise the capturing device
        :return: Status of initialisation process: True - Successful, False - Unsuccessful
        """

        # Setup capturing device
        if self.capture_type == 'local_camera_cv2':
            self._initialise_local_camera_cv2()
        elif self.capture_type == 'local_camera_jetson':
            self._initialise_local_camera_jetson()
        elif self.capture_type == 'rtmp':
            self._initialise_rtmp()

        self.metadata = {'tags': self.cfg['metadata']}
        self.metadata['tags']['storage_type'] = self.cfg['data_storage']['type']
        self.metadata['tags'].update(self.cfg['data_storage']['connection'])

        return self._initialised

    def _initialise_local_camera_cv2(self):
        """
        This function initialise local capturing device connected via OpenCV package
        :return: Status of initialisation process: True - Successful, False - Unsuccessful
        """
        self.camera = cv2.VideoCapture(self.cfg['capturing_device']['connection']['device_id'])
        if self.camera.isOpened():
            logging.info('Capturing device initialisation successful')
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
        self.camera = None
        self._initialised = False

    def _initialise_rtmp(self):
        """
        This function initialise remote capturing device connected via RTMP
        :return: Status of initialisation process: True - Successful, False - Unsuccessful
        """
        # TODO: add support
        self.camera = None
        self._initialised = False

    def connect(self):
        """
        This function starts connectivity thread
        :return:
        """
        self._initialise()

        # TODO: add following lines after debugging
        if not self._initialised:
            return

        self._configure()
        time.sleep(1)
        self._start_capturing()

    def _release(self):
        """
        This function releases the capturing device
        :return: Status of release process: True - Successful, False - Unsuccessful
        """
        if self._initialised:

            if self.capture_type == 'local_camera_cv2':
                res = self._release_cv2()
            elif self.capture_type == 'local_camera_jetson':
                res = self._release_jetson()
            elif self.capture_type == 'rtmp':
                res = self._release_cv2()

            if not res:
                logging.warning('Capturing device could not be released')
                self._initialised = True
            else:
                logging.info('Captured device released successfully')
                self._initialised = False

    def _release_cv2(self):
        """
        This function releases the capturing device initilised via OpenCV package
        :return: Status of release process: True - Successful, False - Unsuccessful
        """
        return self.camera.release()

    def _release_jetson(self):
        """
        This function releases the capturing device initilised via Jetson Nano package
        :return: Status of release process: True - Successful, False - Unsuccessful
        """
        # TODO: add support
        return None

    def exit(self):
        """
        This function stops capturing and releases the capturing device
        :return:
        """
        logging.info('Disconnecting from capturing device ...')
        self._exit = True
        self._stop_capturing()
        self._release()
        logging.info('Disconnection successful')

    def _start_capturing(self):
        """
        This function begins the thread with frame capturing
        :return:
        """
        self._stop = False
        self._capturing_thread = threading.Thread(target=self._capturing, args=[])
        self._capturing_thread.start()

    def _stop_capturing(self):
        """
        This function sends a signal to capturing thread to stop capturing process
        :return:
        """
        self._stop = True
        time.sleep(self.capturing_interval / 1000.0)

    def _capturing(self):
        """
        This function periodically captures a frame and copies it together with metadata into structure
        :return:
        """
        # Set initial time point
        cycle_begin = time.time() - self.capturing_interval / 1000.0

        while not self._stop:

            # Calculate one cycle length
            cycle_begin = cycle_begin + self.capturing_interval / 1000.0

            # If last cycle lasted much longer, we need to skip the current polling cycle to catch up in the future
            if cycle_begin + 0.010 < time.time():
                logging.error('Capturing skipped (increase time interval)')
                continue

            ret_value, frame, timestamp = self._capture_frame()
            frame_saved, filename = self._save_frame(frame)

            if ret_value and frame_saved and not self._stop:
                self.metadata['timestamp'] = timestamp
                frame_metadata = copy.deepcopy(self.metadata)
                self._save_metadata(frame_metadata)
                self._current_frame_id += 1

            if self._stop:
                break

            # Calculate real cycle duration
            cycle_dur = time.time() - cycle_begin

            # If the cycle duration longer than given and no connection issues, jump directly to the next cycle
            if cycle_dur > self.capturing_interval / 1000.0:
                logging.warning('Capturing takes longer ' + str(cycle_dur) + ' than given time intervals')
            else:
                # Calculate how long we need to wait till the begin of the next cycle
                time.sleep(max(self.capturing_interval / 1000.0 - (time.time() - cycle_begin), 0))

    def _save_metadata(self, frame_metadata):
        if self.storage_type == 'local':
            self._save_metadata_local(frame_metadata)

    def _save_metadata_local(self, frame_metadata):
        try:
            filepath = path.join(self.cfg['data_storage']['connection']['filepath'], 'metadata')
            filename = self.cfg['data_storage']['connection']['filename_mask']
            filename += '%0*d' % (6, self._current_frame_id)
            filename += '.json'
            fullname = path.join(filepath, filename)
        except:
            logging.error(
                self.module_name + 'Impossible saving path:' + filepath + ' ' + filename)

        try:
            with open(fullname, 'w') as outfile:
                dump(frame_metadata, outfile, skipkeys=True, indent=4)
                logging.info('Metadata saved as ' + fullname)
        except:
            logging.error(
                self.module_name + 'Saving metadata as ' + fullname + ' failed')

    def _capture_frame(self):
        """
        This function captures a frame from the capturing device
        :return:
        """
        if self.capture_type == 'local_camera_cv2':
            return self._capture_frame_cv2()
        elif self.capture_type == 'local_camera_jetson':
            return self._capture_frame_local_jetson()
        elif self.capture_type == 'rtmp':
            return self._capture_frame_cv2()

    def _capture_frame_cv2(self):
        """
        This function gets frame from capturing device and returns frame variable with
        :return: Return frame
        """
        return_value, frame = self.camera.read()
        timestamp = int(round(time.time() * 1000))

        # TODO: uncomment while debugging
        # return_value = True
        # frame = cv2.imread('test_image.jpg', 0)

        if return_value:
            logging.info(
                self.module_name + 'Frame captured')
        else:
            logging.error(
                self.module_name + 'Capturing frame failed')

        return return_value, frame, timestamp

    def _capture_frame_local_jetson(self):
        """
        This function captures a frame from a capturing device by means of NVidia Jetson package
        :return:
        """
        # TODO: add support
        return False, None, None

    def _save_frame(self, frame):
        """
        This function saves frame
        :param frame:
        :return:
        """
        if self.storage_type == 'local':
            return self._save_frame_locally(frame)
        elif self.storage_type == 'ftp':
            return self._save_frame_ftp(frame)
        elif self.storage_type == 'dataverse':
            return self._save_frame_dataverse(frame)

    def _save_frame_locally(self, frame):
        """
        This function saves current frame locally
        :return:  Status of saving process: True - Successful, False - Unsuccessful
        """
        filepath = ''
        filename = ''
        if type(frame) == 'NoneType':
            ret = False
            logging.error(
                self.module_name + 'No frame to save')
            return ret, None

        try:
            filepath = path.join(self.cfg['data_storage']['connection']['filepath'], 'frames')
            filename = self.cfg['data_storage']['connection']['filename_mask']
            filename += '%0*d' % (6, self._current_frame_id)
            filename += '.png'
            fullname = path.join(filepath, filename)
        except:
            logging.error(
                self.module_name + 'Invalid saving path:' + filepath + ' ' + filename)

        try:
            ret = cv2.imwrite(fullname, frame)
            logging.info(
                self.module_name + 'Frame saved as ' + fullname)
        except:
            logging.err(
                self.module_name + 'Saving as ' + fullname + ' failed')
        return ret, filename

    def _save_frame_ftp(self, frame):
        """
        This function saves frame on ftp server
        :param frame:
        :return:
        """
        # TODO: add support
        return False, 'FTP: not programmed'

    def _save_frame_dataverse(self, frame):
        """
        This function saves frame on dataverse server
        :param frame:
        :return:
        """
        # TODO: add support
        return False, 'dataverse: not programmed'


    def test_camera(self):
        """
        This function outputs video stream in window
        :return:
        """
        self._initialise()

        # TODO: comment during debugging
        if not self._initialised:
            return

        self._configure()
        time.sleep(1)

        while True:
            return_value, frame = self.camera.read()
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    def output_web(self):
        """
        This function streams video on a webpage
        :return:
        """
        pass
