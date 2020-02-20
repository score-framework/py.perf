# Copyright © 2016-2018 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in
# the file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district
# the Licensee has his registered seat, an establishment or assets.

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

    def __enter__(self):
        self('__enter__')
        return self

    def __exit__(self, type, value, traceback):
        self('__exit__')
