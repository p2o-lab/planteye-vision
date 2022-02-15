from flask import Flask, request, jsonify
import logging
import threading

from planteye_vision.shell.shell import Shell
from planteye_vision.configuration.shell_configuration import RestAPIShellConfiguration
from planteye_vision.configuration.planteye_configuration import PlantEyeConfiguration


class RestAPIShell(Shell):
    """
    This class describes an REST API shell
    """

    def __init__(self, config: RestAPIShellConfiguration):
        self.config = config
        self.webserver = None
        self.webserver_thread = None
        self.response_callback = None
        self.planteye_config = None

    def apply_configuration(self):
        host = self.config.parameters['host']
        port = self.config.parameters['port']
        self.webserver = RestAPIWebserver('PlantEye', host, port)

        endpoint = self.config.parameters['endpoint']
        endpoint_name = 'PlantEye REST API Shell'
        self.webserver.add_url_rule(endpoint, endpoint_name, self.response_callback, ['GET'])
        self.webserver.add_url_rule('/upload_config', 'configuration update', self.upload_configuration_callback, ['POST'])
        self.webserver.add_url_rule('/get_config', 'configuration', self.download_configuration_callback, ['GET'])
        self.webserver.add_url_rule('/', 'homepage', self.homepage_callback, ['GET'])
        self.connect()

    def attach_planteye_configuration(self, config: PlantEyeConfiguration):
        self.planteye_config = config

    def attach_callback(self, callback: callable):
        self.response_callback = callback

    def homepage_callback(self):
        welcome_str = 'Welcome to PlantEye API. Available endpoint is %s' % self.config.parameters['endpoint']
        return welcome_str

    def download_configuration_callback(self):
        return jsonify(self.planteye_config.cfg_dict)

    def upload_configuration_callback(self):
        if not hasattr(self, 'pipeline_executor'):
            return

        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            uploaded_cfg = request.json
            print(uploaded_cfg)

            self.pipeline_executor.config.update(uploaded_cfg)
            self.pipeline_executor.update_configuration()

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
