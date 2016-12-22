import time
import logging


class Stopwatch():

    def __init__(self, logger=None):
        if not logger:
            logger = logging.getLogger('score.perf.stopwatch')
        self.logger = logger
        self.start = time.time()
        self.last = self.start

    def __call__(self, msg=None, *args):
        now = time.time()
        timing = '%f %f' % (now - self.start, now - self.last)
        self.last = now
        if msg:
            msg = '%s: %s' % (timing, msg)
        else:
            msg = timing
        self.logger.info(msg, *args)
