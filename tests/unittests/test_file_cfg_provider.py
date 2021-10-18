import yaml

from src.file_cfg_provider import FileCfgProvider


def create_dummy_cfg_dict():
    dummy_cfg_dict = {'capturing_device': {
        'type': 'local_camera_cv2',
        'connection': {
            'device_id': 0
        }
    }
    }

    return dummy_cfg_dict


def write_dummy_cfg_as_yaml(dummy_cfg_dict):
    with open('./res/dummy_cfg.yaml', 'w') as fp:
        yaml.dump(dummy_cfg_dict, fp)


def test_provide_cfg():
    dummy_cfg_dict = create_dummy_cfg_dict()
    write_dummy_cfg_as_yaml(dummy_cfg_dict)
    file_cfg_provider = FileCfgProvider('../res/dummy_cfg.yaml')
    loaded_cfg = file_cfg_provider.provide_cfg()

    assert loaded_cfg == dummy_cfg_dict
