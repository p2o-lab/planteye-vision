from src.vision import LocalVision
import logging

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


vision1 = LocalVision('../res/config_camera_restapi.yaml')
vision1.run()

#vision2 = LocalVision('../res/config_restapi_to_restapi.yaml')
#vision2.run()