import logging
import threading
import os
import json
from time import time, sleep
import cv2
from src.common.timestamp import get_timestamp

from src.shell.shell import Shell
from src.configuration.configuration import LocalShellConfiguration
from src.data_chunks.data_chunk_data import DataChunkImage
from src.configuration.config_provider import ConfigProvider


class LocalShell(Shell):
    """
    This class describes a periodic shell
    """
    def __init__(self):
        self.config = LocalShellConfiguration()
        self.name = None
        self.time_scheduler = None
        self.callback = None

    def import_configuration(self, config_provider: ConfigProvider):
        self.config.read(config_provider)
        self.name = config_provider.provide_name()

    def apply_configuration(self):
        os.makedirs(self.config.storage_path, exist_ok=True)
        self.time_scheduler = TimeScheduler(self.config.time_interval, self.execution_step)
        self.time_scheduler.start()

    def attach_callback(self, callback):
        self.callback = callback

    def execution_step(self):
        timestamp = get_timestamp()
        data_chunks = self.callback()
        for chunk in data_chunks:
            for chunk_piece_data in chunk.data:
                if isinstance(chunk_piece_data, DataChunkImage):

                    for chunk_piece_metadata in chunk.metadata:
                        if chunk_piece_metadata.name == 'timestamp':
                            timestamp = chunk_piece_metadata.value
                            break

                    image_file_name = str(timestamp)+'.png'
                    image_file_fullpath = os.path.join(self.config.storage_path, image_file_name)
                    cv2.imwrite(image_file_fullpath, chunk_piece_data.value)
                    break

        metadata_file_dict = {}
        for chunk in data_chunks:
            metadata_file_dict[chunk.name] = chunk.as_dict()
            for chunk_piece in chunk.data:
                if isinstance(chunk_piece, DataChunkImage):
                    metadata_file_dict[chunk.name].pop('data')

        metadata_file_name = str(timestamp) + '.json'
        metadata_file_fullpath = os.path.join(self.config.storage_path, metadata_file_name)

        with open(metadata_file_fullpath, 'w') as json_file:
            json.dump(metadata_file_dict, json_file, indent=4)


class TimeScheduler:
    def __init__(self, time_interval: float, executed_function):
        self.time_interval = time_interval
        self.executed_function = executed_function
        self.thread = None
        self.stop_flag = False

    def start(self):
        self.stop_flag = False
        self.thread = threading.Thread(target=self.single_step, args=[])
        self.thread.start()

    def stop(self):
        self.stop_flag = True

    def single_step(self):
        cycle_begin = time() - self.time_interval / 1000.0
        while not self.stop_flag:
            print('Loop step')
            logging.info('Loop step')
            cycle_begin = cycle_begin + self.time_interval / 1000.0
            if cycle_begin + 0.010 < time():
                logging.error('Capturing skipped (consider increasing interval)')
                continue
            self.executed_function()
            debug_str = 'Execution duration %i ms' % int((time() - cycle_begin) * 1000)
            logging.debug(debug_str)
            cycle_duration = time() - cycle_begin
            if cycle_duration > self.time_interval / 1000.0:
                logging.warning('Capturing takes longer ' + str(cycle_duration) + ' than given time intervals')
            else:
                sleep(max(self.time_interval / 1000.0 - (time() - cycle_begin), 0))
