import logging
from time import sleep
from opcua import Client, ua
import threading

from planteye_vision.inlet.inlet import Inlet
from planteye_vision.configuration.inlet_configuration import OPCUAValueConfiguration
from planteye_vision.data_chunks.data_chunk import GeneralDataChunk
from planteye_vision.data_chunks.data_chunk_data import DataChunkValue
from planteye_vision.data_chunks.metadata_chunk import MetadataChunkData
from planteye_vision.data_chunks.data_chunk_status import OPCUAReadStatus


class OPCUADataInlet(Inlet):
    """
    This class describes an OPC UA data inlet
    """
    def __init__(self, config: OPCUAValueConfiguration):
        self.config = config
        self.name = None
        self.type = None
        self.opcua_client = None

    def __del__(self):
        if self.opcua_client is not None:
            self.opcua_client.disconnect()

    def apply_configuration(self):
        opcua_server_url = self.config.parameters['server']
        opcua_server_username = self.config.parameters['username']
        opcua_server_pwd = self.config.parameters['password']
        self.name = self.config.name
        self.type = self.config.type
        self.opcua_client = OPCUAClient(opcua_server_url, opcua_server_username, opcua_server_pwd)
        self.opcua_client.connect()

    def retrieve_data(self):
        data_chunk = GeneralDataChunk(self.name, self.type, self.config.parameters, hidden=self.config.hidden)

        if self.config.is_valid():
            value = self.poll_node()
            data_type = 'diverse'
            if value is None:
                status = OPCUAReadStatus(99)
                data_chunk.add_status(status)
            else:
                status = OPCUAReadStatus(0)
                data_chunk.add_status(status)
                data_chunk.add_data(DataChunkValue('opcua_value', value, data_type))
        else:
            status = OPCUAReadStatus(100)
            data_chunk.add_status(status)
            print('Step %s : No execution due to invalid configuration' % self.name)

        for metadata_variable, metadata_value in self.config.metadata.items():
            data_chunk.add_metadata(MetadataChunkData(metadata_variable, metadata_value))
        return [data_chunk]

    def poll_node(self):
        if not self.opcua_client.get_connection_status():
            logging.warning(
                'Cannot poll %s from OPCA UA server %s (no connection)' % (self.name, self.opcua_client.get_url()))
            return None
        try:
            node_obj = ua.NodeId(self.config.parameters['node_id'], self.config.parameters['node_ns'])
            node = self.opcua_client.get_server_obj().get_node(node_obj)
            data_variant = node.get_data_value()
            timestamp = data_variant.SourceTimestamp
            value = data_variant.Value.Value
            logging.info('Server %s, Node %s: Value polled (Timestamp %s, Value %s)' % (
                self.opcua_client.get_url(), str(self.config.parameters['node_id']), str(timestamp), str(value)))
            return value
        except Exception as exc:
            logging.info('Server %s, Node %s: Value polling failed' % (self.opcua_client.get_url(), str(self.config.parameters['node_id'])),
                         exc_info=exc)
            return None

    def execute(self):
        return super().execute()


class OPCUAClient:
    def __init__(self, server: str, username='', password='', reconnect_interval=1000):
        self.server = server
        self.username = username
        self.password = password

        self.client = Client(self.server)
        self.client.set_user(username)
        self.client.set_password(password)

        self.connection_status = False
        self.connectivity_thread = None
        self.reconnect_interval = reconnect_interval
        self.connected_once = False

        self.stop_flag = False
        self.stopped = True

    def connect(self):
        self.connectivity_thread = threading.Thread(target=self.__connectivity_routine)
        self.stopped = False
        self.connectivity_thread.start()
        sleep(1)

    def disconnect(self):
        logging.info('Disconnecting to OPC UA server %s ...' % self.server)
        self.stop_flag = True
        self.client.disconnect()
        while not self.stopped:
            sleep(0.1)
            logging.info('Disconnected from OPC UA server %s' % self.server)

    def __single_connect(self):
        logging.info('Connecting to OPC UA server %s ...' % self.server)
        try:
            self.client.connect()
            logging.info('Connection to OPC UA server %s established' % self.server)
            sleep(1)
            self.connected_once = True
        except Exception as exc:
            logging.warning('Connection to OPC UA server %s failed' % self.server, exc_info=exc)

    def __connectivity_routine(self):
        while True:
            if self.stop_flag:
                self.stopped = True
                return
            self.check_connection()
            if not self.connection_status:
                self.__single_connect()
            sleep(self.reconnect_interval / 1000)

    def check_connection(self):
        logging.debug('Checking connection status to OPCA UA server %s ...' % self.server)
        try:
            self.client.get_node(ua.NodeId(2259, 0)).get_data_value()
            logging.debug('Connection to OPCA UA server %s persists' % self.server)
            self.connection_status = True
        except Exception as exc:
            logging.warning('Connection to OPCA UA server %s does NOT persist' % self.server)
            self.connection_status = False
            sleep(1)

    def get_connection_status(self):
        return self.connection_status

    def get_url(self):
        return self.server

    def get_server_obj(self):
        return self.client
