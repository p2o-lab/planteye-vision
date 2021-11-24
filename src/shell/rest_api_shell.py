from flask import Flask
import logging
import threading

from src.shell.shell import Shell
from src.configuration.configuration import RestAPIConfiguration


class RestAPIShell(Shell):
    """
    This class describes an REST API outlet
    """
    def __init__(self):
        self.config = RestAPIConfiguration()
        self.webserver_name = 'unnamed'
        self.webserver = None
        self.data_to_provide = None
        self.webserver_thread = None
        self.response_callback = None

    def import_configuration(self, config_provider):
        self.config.read(config_provider)
        self.webserver_name = config_provider.provide_name()

    def apply_configuration(self):
        name = self.webserver_name
        host = self.config.host
        port = self.config.port
        self.webserver = RestAPIWebserver(name, host, port)

        endpoint = self.config.endpoint
        endpoint_name = self.config.endpoint_name
        self.webserver.add_url_rule(endpoint, endpoint_name, self.response_callback)
        self.webserver.add_url_rule('/', 'homepage', self.homepage_callback)
        self.connect()

    def attach_callback(self, callback):
        self.response_callback = callback

    def homepage_callback(self):
        welcome_str = 'Welcome to PlantEye API. Available endpoint is %s' % self.config.endpoint
        return welcome_str

    def connect(self):
        self.webserver_thread = threading.Thread(target=self.webserver.run)
        self.webserver_thread.start()

    def disconnect(self):
        pass


class RestAPIWebserver:
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port
        self.endpoint_flask_app = Flask(name)

    def add_url_rule(self, endpoint, name, rule):
        self.endpoint_flask_app.add_url_rule(endpoint, name, rule)

    def run(self):
        try:
            self.endpoint_flask_app.run(host=self.host, port=self.port)
        except PermissionError:
            logging.error('Cannot not start flask server with given configuration')
