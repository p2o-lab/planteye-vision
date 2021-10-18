import yaml
import pytest
import logging

from src.cv2_camera_image_data_provider import CV2CameraImageDataProvider

logging.basicConfig(filename='test.log',
                    filemode='w',
                    format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)


@pytest.fixture()
def create_dummy_cfg_dict():
    dummy_cfg_dict = {'capturing_device': {
        'type': 'local_camera_cv2',
        'connection': {
            'device_id': 0
        }
    }
    }

    return dummy_cfg_dict


@pytest.fixture()
def webcam_constructor(create_dummy_cfg_dict):
    camera_instance = CV2CameraImageDataProvider()
    camera_instance.__configured = True
    camera_instance.__cfg = create_dummy_cfg_dict
    camera_instance.initialise()
    return camera_instance


def test_configure(webcam_constructor):
    webcam_constructor


def test_set_proper_parameter(webcam_constructor):
    assert webcam_constructor.set_parameter('CV_CAP_PROP_FRAME_WIDTH', 1280)
    assert webcam_constructor.set_parameter('CV_CAP_PROP_FRAME_HEIGHT', 720)
