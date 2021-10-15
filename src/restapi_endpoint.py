from flask import Flask
import logging
import json


class RestAPIEndpoint:
    def __init__(self, cfg):
        self.cfg = cfg
        self.endpoint_flask_app = Flask(self.cfg['name'])

    def add_url_rule(self, url, name, rule):
        self.endpoint_flask_app.add_url_rule(url, name, rule)

    def run(self):
        try:
            self.endpoint_flask_app.run(host=self.cfg['url'], port=self.cfg['port'])
        except PermissionError:
            logging.error('Cannot not start flask server with given configuration')


if __name__ == '__main__':
    endpoint_app = RestAPIEndpoint('0.0.0.0', 9000)
    endpoint_app.add_url_rule('/get_frame', 'Get frame', lambda: json.dumps('test_output'))
    endpoint_app.run()
