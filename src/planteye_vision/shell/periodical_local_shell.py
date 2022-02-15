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
            print('Loop step %f' % time())
            logging.info('Shell execution step')
            step_begin = time()
            expected_step_end = expected_step_end + self.time_interval / 1000.0
            print('Step begin %f' % step_begin)
            print('Expected step end %f' % expected_step_end)
            if step_begin > expected_step_end:
                logging.error('Shell execution step skipped (consider increasing interval)')
                print('Skip step')
                continue
            print('Execute step')
            logging.info('Shell execution step began')
            self.executed_function()
            step_duration = time() - step_begin
            debug_str = 'Shell execution step duration %i ms' % int(step_duration * 1000)
            logging.debug(debug_str)
            print('End step %f' % time())
            print('Step execution duration %f' % step_duration)
            if time() > expected_step_end:
                print('Step execution longer than interval')
                logging.warning('Shell execution step took longer (' + str(step_duration) + ') than given time interval ' + '(' + str(self.time_interval) + ')')
            else:
                print('Sleep for %f' % max(expected_step_end-time(), 0))
                sleep(max(expected_step_end-time(), 0))
