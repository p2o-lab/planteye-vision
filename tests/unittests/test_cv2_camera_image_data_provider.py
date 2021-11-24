import time
import pytest

from src.receive.opencv_generic_image_data_receiver import OpenCVGenericImageDataReceiver


@pytest.fixture()
def create_dummy_cfg_dict():
    dummy_cfg_dict = {'capturing_device': {
        'type': 'local_camera_cv2',
        'connection': {
            'device_id': 1
        }
    }
    }

    return dummy_cfg_dict


@pytest.fixture()
def webcam_constructor(create_dummy_cfg_dict):
    camera_instance = OpenCVGenericImageDataReceiver()
    camera_instance.configured = True
    camera_instance.cfg = create_dummy_cfg_dict['capturing_device']
    return camera_instance


def test_configure(webcam_constructor):
    assert not webcam_constructor.set_parameter('invalid_parameter_name', 1280)
    assert not webcam_constructor.set_parameter('CV_CAP_PROP_FRAME_WIDTH', 1280)
    assert not webcam_constructor.set_parameter('CV_CAP_PROP_FRAME_HEIGHT', 720)


def test_initialise_camera(webcam_constructor):
    webcam_constructor.initialise()
    assert webcam_constructor.initialised


def test_provide_data(webcam_constructor):
    webcam_constructor.initialise()
    status, frame, timestamp = webcam_constructor.receive_data()
    now_timestamp = int(round(time.time() * 1000))
    assert status is not None
    assert frame is not None
    assert abs(timestamp-now_timestamp)<1000

