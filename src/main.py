from src.vision import LocalVision
import logging

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


vision = LocalVision('../res/config_baumer_restapi_opcua.yaml')
vision.run()
