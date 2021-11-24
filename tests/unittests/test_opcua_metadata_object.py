import time

from src.receive.OPCUAMetadataObject import OPCUAMetadataObject


def simulation_server_configuration_dict():
    return ('stirrer_rotational_speed',
            {'source': 'opcua',
             'access_data': {
                 'server': 'opc.tcp://opcuademo.sterfive.com:26543',
                 'username': '',
                 'password': '',
                 'node_ns': 8,
                 'node_id': 'Scalar_Simulation_Float'},
             'unit': 'rpm'
             })


def test_configure_and_release():
    cfg = simulation_server_configuration_dict()
    opcua_metadata_obj = OPCUAMetadataObject(*cfg)
    step = 0
    while step <= 10:
        step += step
        time.sleep(1)
        value = opcua_metadata_obj.receive_data()
        if value is not None:
            opcua_metadata_obj.release()
            return True
    opcua_metadata_obj.release()
    assert False
