from src.extract.metadata_object import MetadataObject
from src.extract.opcua_listener import OPCUAServer, OPCUANodePoller


class OPCUAMetadataObject(MetadataObject):

    def __init__(self, item_name, item_dict):
        super().__init__(item_name, item_dict)
        self.opcua_listener = None
        self.opcua_node_obj = None

    def receive_data(self):
        if self.opcua_node_obj is None:
            self.initialise_opcua_listener()
        return self.opcua_node_obj.get_value()

    def get_source_type(self):
        return super().get_source_type()

    def initialise_opcua_listener(self):
        opcua_server_url = self.item_dict['access_data']['server']
        opcua_server_username = self.item_dict['access_data']['username']
        opcua_server_pwd = self.item_dict['access_data']['password']
        node_name = self.item_name
        node_ns = self.item_dict['access_data']['node_ns']
        node_id = self.item_dict['access_data']['node_id']
        self.opcua_listener = OPCUAServer(opcua_server_url, opcua_server_username, opcua_server_pwd)
        self.opcua_listener.connect()
        self.opcua_node_obj = OPCUANodePoller(self.opcua_listener, node_name, node_ns, node_id)

    def get_opcua_node_obj(self):
        return self.opcua_node_obj

    def release(self):
        if self.opcua_node_obj:
            self.opcua_listener.disconnect()
