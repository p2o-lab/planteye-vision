import logging
from time import sleep
import cv2
from opcua import Client, ua
import threading

from src.common.timestamp import get_timestamp

from src.inlet.inlet import Inlet
from src.common.configuration import OPCUAValueConfiguration
from src.common.data_chunk import GeneralDataChunk
from src.common.data_chunk_data import DataChunkValue
from src.common.metadata_chunk import MetadataChunkData
from src.common.data_chunk_status import OPCUAReadStatus


class OPCUADataInlet(Inlet):
    """
    This class describes an OPC UA data inlet
    """
    def __init__(self):
        self.config = OPCUAValueConfiguration()
        self.variable_name = 'unnamed'
        self.opcua_client = None
        self.node_obj = None

    def import_configuration(self, config_provider):
        self.config.read(config_provider)
        self.variable_name = config_provider.provide_name()

    def apply_configuration(self):
        opcua_server_url = self.config.server_url
        opcua_server_username = self.config.server_user
        opcua_server_pwd = self.config.server_password
        self.opcua_client = OPCUAClient(opcua_server_url, opcua_server_username, opcua_server_pwd)
        self.opcua_client.connect()

    def retrieve_data(self):
        value = self.poll_node()
        data_chunk = GeneralDataChunk()
        if value is None:
            status = OPCUAReadStatus(99)
            data_chunk.add_status(status)
        else:
            status = OPCUAReadStatus(0)
            data_chunk.add_status(status)
            data_chunk.add_data(DataChunkValue(self.variable_name, value))

        for metadata_variable, metadata_value in self.config.metadata.items():
            data_chunk.add_metadata(MetadataChunkData(metadata_variable, metadata_value))
        return data_chunk

    def connect(self):
        pass

    def disconnect(self):
        pass

    def poll_node(self):
        if not self.opcua_client.get_connection_status():
            logging.warning(
                'Cannot poll %s from OPCA UA server %s (no connection)' % (self.variable_name, self.opcua_client.get_url()))
            return None
        try:
            node_obj = ua.NodeId(self.config.node_id, self.config.namespace)
            node = self.opcua_client.get_server_obj().get_node(node_obj)
            data_variant = node.get_data_value()
            timestamp = data_variant.SourceTimestamp
            value = data_variant.Value.Value
            logging.info('Server %s, Node %s: Value polled (Timestamp %s, Value %s)' % (
                self.opcua_client.get_url(), str(self.config.node_id), str(timestamp), str(value)))
            return value
        except Exception as exc:
            logging.info('Server %s, Node %s: Value polling failed' % (self.opcua_client.get_url(), str(self.config.node_id)),
                         exc_info=exc)
            return None

    def get_opcua_server_info(self):
        return 'Server info'


class OPCUAClient:
    def __init__(self, opcua_url, user_id='', user_pwd='', reconnect_interval=1000):
        self.opcua_url = opcua_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        self.client = Client(self.opcua_url)
        self.client.set_user(user_id)
        self.client.set_password(user_pwd)

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
        logging.info('Disconnecting to OPC UA server %s ...' % self.opcua_url)
        self.stop_flag = True
        self.client.disconnect()
        while not self.stopped:
            sleep(0.1)
            logging.info('Disconnected from OPC UA server %s' % self.opcua_url)

    def __single_connect(self):
        logging.info('Connecting to OPC UA server %s ...' % self.opcua_url)
        try:
            self.client.connect()
            logging.info('Connection to OPC UA server %s established' % self.opcua_url)
            sleep(1)
            self.connected_once = True
        except Exception as exc:
            logging.warning('Connection to OPC UA server %s failed' % self.opcua_url, exc_info=exc)

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
        logging.debug('Checking connection status to OPCA UA server %s ...' % self.opcua_url)
        try:
            self.client.get_node(ua.NodeId(2259, 0)).get_data_value()
            logging.debug('Connection to OPCA UA server %s persists' % self.opcua_url)
            self.connection_status = True
        except Exception as exc:
            logging.warning('Connection to OPCA UA server %s does NOT persist' % self.opcua_url)
            self.connection_status = False
            sleep(1)

    def get_connection_status(self):
        return self.connection_status

    def get_url(self):
        return self.opcua_url

    def get_server_obj(self):
        return self.client
