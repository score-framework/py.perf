# Copyright © 2016 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
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
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

import collections
from datetime import datetime
import os
import time
import sys
import subprocess
import threading
from score.init import ConfiguredModule, ConfigurationError, parse_time_interval
from score.serve import SimpleWorker


defaults = {
    'sample_interval': '100ms',
    'output_interval': '5s',
    'output.folder': '.',
    'output.file': None,
}


def init(confdict):
    """
    Initializes this module according to :ref:`our module initialization
    guidelines <module_initialization>` with the following configuration keys:

    :confkey:`sample_interval` :confdefault:`100ms`
        Time duration to wait between measurements.

    :confkey:`output_interval` :confdefault:`5s`
        Interval in which to update resulting graph.

    :confkey:`output.folder` :confdefault:`.`
        Folder to write results to. Will create a file with this process's start
        time and PID as file name.

    :confkey:`output.file`
        This may be provided instead of ``output.folder``, in which case the
        output will be written to this specific file.
    """
    conf = dict(defaults.items())
    conf.update(confdict)
    sample_interval = parse_time_interval(conf['sample_interval'])
    output_interval = parse_time_interval(conf['output_interval'])
    if conf['output.file']:
        file = conf['output.file']
        if not os.path.isdir(os.path.dirname(file)):
            import score.perf
            raise ConfigurationError(
                score.perf, 'Folder of configured `output.file` does not exist')
    else:
        if not os.path.isdir(conf['output.folder']):
            import score.perf
            raise ConfigurationError(
                score.perf, 'Configured `output.folder` does not exist')
        now = datetime.now()
        file = os.path.join(
            conf['output.folder'], '%s-%d.svg' % (
                now.strftime('%Y-%m-%d %H:%M:%S'), os.getpid()))

    return ConfiguredPerfModule(sample_interval, output_interval, file)


class ConfiguredPerfModule(ConfiguredModule):
    """
    This module's :class:`configuration object <score.init.ConfiguredModule>`.
    """

    def __init__(self, sample_interval, output_interval, file):
        import score.perf
        super().__init__(score.perf)
        self.sample_interval = sample_interval
        self.output_interval = output_interval
        self._stack_counts = collections.defaultdict(int)
        self.file = file

    def score_serve_workers(self):
        return Worker(self)

    def _sample(self, frame=None):
        if frame is None:
            for thread_id, frame in sys._current_frames().items():
                if thread_id == threading.current_thread().ident:
                    continue
                top_frame = frame
                while top_frame.f_back:
                    top_frame = top_frame.f_back
                if top_frame.f_globals.get('__name__') == '__main__':
                    continue
                self._sample(frame)
            return

        stack = []
        while frame is not None:
            formatted_frame = '{}({})'.format(frame.f_code.co_name,
                                              frame.f_globals.get('__name__'))
            stack.append(formatted_frame)
            frame = frame.f_back

        formatted_stack = ';'.join(reversed(stack))
        self._stack_counts[formatted_stack] += 1

    def update_graph(self):
        proc = subprocess.Popen(
            ['flamegraph.pl', '--hash', '--minwidth', '1'],
            universal_newlines=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            outs, errs = proc.communicate(self.flamegraph_string(), timeout=15)
            open(self.file, 'w').write(outs)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            raise

    def flamegraph_string(self):
        ordered_stacks = sorted(self._stack_counts.items(),
                                key=lambda kv: kv[1], reverse=True)
        lines = ['{} {}\n'.format(frame, count)
                 for frame, count in ordered_stacks]
        return ''.join(lines)


class Worker(SimpleWorker):

    def __init__(self, conf):
        super().__init__()
        self.conf = conf

    def loop(self):
        last_output = time.time()
        while self.running:
            time.sleep(self.conf.sample_interval)
            self.conf._sample()
            if time.time() - last_output >= self.conf.output_interval:
                self.conf.update_graph()
                last_output = time.time()
        self.conf.update_graph()
