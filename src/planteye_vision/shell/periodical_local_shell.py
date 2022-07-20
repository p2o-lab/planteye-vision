import logging
import threading
from time import time, sleep

from planteye_vision.shell.shell import Shell
from planteye_vision.configuration.shell_configuration import PeriodicalLocalShellConfiguration


class PeriodicalLocalShell(Shell):
    """
    This class describes a local shell that requests data periodically
    """
    def __init__(self, config: PeriodicalLocalShellConfiguration):
        self.config = config
        self.time_scheduler = None
        self.callback = None

    def apply_configuration(self):
        self.time_scheduler = TimeScheduler(self.config.parameters['time_interval'], self.execution_step)
        self.time_scheduler.start()

    def attach_callback(self, callback):
        self.callback = callback

    def execution_step(self):
        self.callback()


class TimeScheduler:
    def __init__(self, time_interval: float, executed_function):
        self.time_interval = time_interval
        self.executed_function = executed_function
        self.thread = None
        self.stop_flag = False

    def start(self):
        self.stop_flag = False
        self.thread = threading.Thread(target=self.executable, args=[])
        self.thread.start()

    def stop(self):
        self.stop_flag = True

    def executable(self):
        expected_step_end = time() - self.time_interval / 1000.0
        while not self.stop_flag:
            logging.debug('Shell execution step began')
            step_begin = time()
            expected_step_end = expected_step_end + self.time_interval / 1000.0
            if step_begin > expected_step_end:
                logging.error('Shell execution step skipped (consider increasing interval)')
                continue
            self.executed_function()
            if time() > expected_step_end:
                warn_msg = f'Shell execution step took longer than given time interval ({self.time_interval/1000.0} s)'
                logging.warning(warn_msg)
            else:
                sleep(max(expected_step_end-time(), 0))
