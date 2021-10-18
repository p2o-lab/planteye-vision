from src.file_cfg_provider import FileCfgProvider
from src.cv2_camera_image_data_provider import CV2CameraImageDataProvider

cfg_provider = FileCfgProvider('../config.yaml')

camera_instance = CV2CameraImageDataProvider()
camera_instance.configure(cfg_provider)
camera_instance.initialise()
