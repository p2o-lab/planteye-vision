from flask import Flask, request, Response
import logging
import threading

from src.shell.shell import Shell
from src.configuration.shell_configuration import RestAPIShellConfiguration
from src.configuration.config_provider import ConfigProvider, DictConfigProvider


class RestAPIShell(Shell):
    """
    This class describes an REST API shell
    """

    def __init__(self):
        self.config = RestAPIShellConfiguration()
        self.webserver_name = 'unnamed'
        self.webserver = None
        self.webserver_thread = None
        self.response_callback = None

    def import_configuration(self, config_provider: ConfigProvider):
        self.config.read(config_provider)
        self.webserver_name = config_provider.provide_name()

    def apply_configuration(self):
        name = self.webserver_name
        host = self.config.access_data['host']
        port = self.config.access_data['port']
        self.webserver = RestAPIWebserver(name, host, port)

        endpoint = self.config.access_data['endpoint']
        endpoint_name = self.config.access_data['endpoint_name']
        self.webserver.add_url_rule(endpoint, endpoint_name, self.response_callback, ['GET'])
        self.webserver.add_url_rule('/upload_config', 'configuration update', self.upload_configuration_callback, ['POST'])
        self.webserver.add_url_rule('/', 'homepage', self.homepage_callback, ['GET'])
        self.connect()

    def attach_callback(self, callback: callable):
        self.response_callback = callback

    def homepage_callback(self):
        welcome_str = 'Welcome to PlantEye API. Available endpoint is %s' % self.config.access_data['endpoint']
        return welcome_str

    def upload_configuration_callback(self):
        if not hasattr(self, 'pipeline_executor'):
            return

        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            uploaded_cfg = request.json
            print(uploaded_cfg)

            if 'inlets' in uploaded_cfg.keys():
                self.pipeline_executor.config_dict['inlets'] = uploaded_cfg['inlets']
            if 'processors' in uploaded_cfg.keys():
                self.pipeline_executor.config_dict['processors'] = uploaded_cfg['processors']

            self.pipeline_executor.reapply_configuration()

            return 'Configuration applied'
        else:
            return 'Content-Type not supported! Only json application/json is supported!'

    def enable_configuration_update_via_restapi(self, pipeline_executor):
        self.pipeline_executor = pipeline_executor

    def connect(self):
        self.webserver_thread = threading.Thread(target=self.webserver.run)
        self.webserver_thread.start()

    def disconnect(self):
        pass


class RestAPIWebserver:
    def __init__(self, name: str, host: str, port: int):
        self.name = name
        self.host = host
        self.port = port
        self.endpoint_flask_app = Flask(name)

    def add_url_rule(self, endpoint: str, name: str, rule: callable, methods):
        self.endpoint_flask_app.add_url_rule(endpoint, name, rule, methods=methods)

    def run(self):
        try:
            self.endpoint_flask_app.run(host=self.host, port=self.port)
        except PermissionError:
            logging.error('Cannot not start flask server with given configuration')
