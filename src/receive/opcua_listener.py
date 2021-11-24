from opcua import Client, ua
import logging
import time
import threading

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


class OPCUANodePoller:
    def __init__(self, opcua_server, node_name, node_ns, node_id):
        self.opcua_server = opcua_server
        self.node_name = node_name
        self.node_ns = node_ns
        self.node_id = node_id
        self.node_obj = None

    def get_value(self):
        return self.poll_node()

    def poll_node(self):
        if not self.opcua_server.get_connection_status():
            logging.warning(
                'Cannot pull %s from OPCA UA server %s (no connection)' % (self.node_name, self.opcua_server.get_url()))
            return None
        try:
            node_obj = ua.NodeId(self.node_id, self.node_ns)
            node = self.opcua_server.get_server_obj().get_node(node_obj)
            data_variant = node.get_data_value()
            timestamp = data_variant.SourceTimestamp
            value = data_variant.Value.Value
            logging.info('Server %s, Node %s: Value polled (Timestamp %s, Value %s)' % (
                self.opcua_server.get_url(), str(self.node_id), str(timestamp), str(value)))
            return value
        except Exception as exc:
            logging.info('Server %s, Node %s: Value polling failed' % (self.opcua_server.get_url(), str(self.node_id)),
                         exc_info=exc)
            return None


class OPCUAServer:
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
        """
        Creates separate thread to take care of connectivity
        :return:
        """
        self.connectivity_thread = threading.Thread(target=self.__connectivity_routine)
        self.stopped = False
        self.connectivity_thread.start()
        time.sleep(1)

    def disconnect(self):
        logging.info('Disconnecting to OPC UA server %s ...' % self.opcua_url)
        self.stop_flag = True
        self.client.disconnect()
        while not self.stopped:
            time.sleep(0.1)
            logging.info('Disconnected from OPC UA server %s' % self.opcua_url)

    def __single_connect(self):
        logging.info('Connecting to OPC UA server %s ...' % self.opcua_url)
        try:
            self.client.connect()
            logging.info('Connection to OPC UA server %s established' % self.opcua_url)
            time.sleep(1)
            self.connected_once = True
        except Exception as exc:
            logging.warning('Connection to OPC UA server %s failed' % self.opcua_url, exc_info=exc)

    def __connectivity_routine(self):
        """
        This function checks connection and reconnect to the OPC UA server as required.
        :return:
        """
        while True:
            if self.stop_flag:
                self.stopped = True
                return
            self.check_connection()
            if not self.connection_status:
                self.__single_connect()
            time.sleep(self.reconnect_interval / 1000)

    def check_connection(self):
        logging.debug('Checking connection status to OPCA UA server %s ...' % self.opcua_url)
        try:
            self.client.get_node(ua.NodeId(2259, 0)).get_data_value()
            logging.debug('Connection to OPCA UA server %s persists' % self.opcua_url)
            self.connection_status = True
        except Exception as exc:
            logging.warning('Connection to OPCA UA server %s does NOT persist' % self.opcua_url)
            self.connection_status = False
            time.sleep(1)

    def get_connection_status(self):
        return self.connection_status

    def get_url(self):
        return self.opcua_url

    def get_server_obj(self):
        return self.client


if __name__ == '__main__':
    opcua_server_obj = OPCUAServer('opc.tcp://opcuademo.sterfive.com:26543')
    opcua_server_obj.connect()
    time.sleep(1)
    node_poller = OPCUANodePoller(opcua_server_obj, 'float_dynamic', 8, 'Scalar_Simulation_Float')
    while True:
        print(node_poller.get_value())
        time.sleep(1)
