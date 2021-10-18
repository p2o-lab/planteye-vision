from flask import Flask
import logging
import json


class RestAPIEndpoint:
    def __init__(self, name):
        self.endpoint_flask_app = Flask(name)

    def add_url_rule(self, endpoint, name, rule):
        self.endpoint_flask_app.add_url_rule(endpoint, name, rule)

    def run(self, host, port):
        try:
            self.endpoint_flask_app.run(host=host, port=port)
        except PermissionError:
            logging.error('Cannot not start flask server with given configuration')


if __name__ == '__main__':
    endpoint_app = RestAPIEndpoint('Test API')
    endpoint_app.add_url_rule('/get_frame', 'Get frame', lambda: json.dumps('test_output'))
    endpoint_app.run('0.0.0.0', 9000)
