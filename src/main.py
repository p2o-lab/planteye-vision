from src.inlet.generic_camera_inlet import GenericCameraInlet
from src.inlet.static_data_inlet import StaticDataInlet
from src.inlet.opcua_data_inlet import OPCUADataInlet

from src.common.config_provider import FileConfigProvider, DictConfigProvider
import time

config_provider = FileConfigProvider('config', 'config.yaml')
cfg_dict = config_provider.provide_config()
inlets = cfg_dict['inlet']

inlets_obj = []
for inlet_name, inlet_config_dict in inlets.items():
    if inlet_config_dict['type'] == 'local_camera_cv2':
        inlet = GenericCameraInlet()
    elif inlet_config_dict['type'] == 'static_variable':
        inlet = StaticDataInlet()
    elif inlet_config_dict['type'] == 'opcua_variable':
        inlet = OPCUADataInlet()
    config_provider = DictConfigProvider(inlet_name, inlet_config_dict)
    inlet.import_configuration(config_provider)
    inlet.apply_configuration()
    inlets_obj.append(inlet)
    chunk = inlet.receive_data()

for inlet in inlets_obj:
    chunk = inlet.receive_data()
    print(chunk.as_dict())

chunk_object = chunk

outlets = cfg_dict['outlet']
for outlet_name, outlet_config_dict in outlets.items():
    if outlet_config_dict['type'] == 'rest_api':
        outlet = RestAPIOutlet()
    config_provider = DictConfigProvider(outlet_name, outlet_config_dict)
    outlet.import_configuration(config_provider)
    outlet.update_data_to_provide(chunk_object)
    outlet.apply_configuration()

i = 0
while True:
    print(i)
    for inlet in inlets_obj:
        chunk = inlet.receive_data()
        print(chunk.as_dict())
    i += 1
    time.sleep(1)







