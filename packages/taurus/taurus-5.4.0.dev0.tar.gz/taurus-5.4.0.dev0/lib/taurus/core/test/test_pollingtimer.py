from __future__ import print_function

import signal
import sys
import time

import pytest

import taurus
from taurus.core import TaurusPollingTimer


class _Timeout:
    """Timeout context. Inspired by https://stackoverflow.com/a/59997890"""

    def __init__(self, seconds=1, msg="Timeout"):
        self.seconds = seconds
        self.msg = msg

    def handle_timeout(self, signum, frame):
        pytest.fail(self.msg)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


def test_polling():
    period = 50
    a = taurus.Attribute("eval:'test_polling'")

    class _Listener:
        def __init__(self):
            self.count = 0

        def cb(self, *_):
            self.count += 1

    listener = _Listener()
    a.addListener(listener.cb)
    pt = TaurusPollingTimer(period=period)
    pt.addAttribute(a)
    time.sleep(period * 4 / 1000.0)
    assert listener.count > 0
    assert listener.count < 7


def test_bug_1178():
    """Test if we are affected by
    https://gitlab.com/taurus-org/taurus/-/issues/1178
    """
    a = taurus.Attribute("eval:1")
    pt = TaurusPollingTimer(period=500)  # poll every 500ms
    with _Timeout(seconds=3, msg="Deadlock in TaurusPollingTimer (see #1178)"):
        for i in range(100):  # this should finish in << 1s
            pt.addAttribute(a)
            print(i, end=" ")
            sys.stdout.flush()
            pt.removeAttribute(a)
    assert i == 99
