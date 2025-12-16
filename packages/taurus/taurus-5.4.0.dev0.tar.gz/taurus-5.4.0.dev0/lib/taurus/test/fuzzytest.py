#!/usr/bin/env python

# ###########################################################################
#
# This file is part of Taurus
#
# http://taurus-scada.org
#
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
#
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
#
# ###########################################################################

"""Utility functions to deal with non-ideal (fuzzy) tests"""


def loopTest(testname, maxtries=100, maxfails=10):
    """Run a test `maxtries` times or until it fails `maxfails` times and
    report the number of tries and failures.

    :param testname: test name. see:
        :meth:`unittest.TestLoader.loadTestsFromName`
    :type testname: str
    :param maxtries: maximum number of runs
    :type maxtries: int
    :param maxfails: maximum number of failed runs
    :type maxfails: int
    :return: a tuple of ints: tries, failures
    :rtype: tuple
    """
    import unittest

    suite = unittest.defaultTestLoader.loadTestsFromName(testname)
    runner = unittest.TextTestRunner(verbosity=0)
    i, f = 0, 0
    while f < maxfails and i < maxtries:
        i += 1
        result = runner.run(suite)
        if not result.wasSuccessful():
            f += 1
    return i, f


def loopSubprocess(
    target, maxtries=100, maxfails=10, okvalues=(0,), args=(), kwargs=None
):
    """Run a callable as a subprocess `maxtries` times or until it fails
    `maxfails` times and report the number of tries and failures.
    The callable is run as a subprocess and it is considered to run fine if
    the subprocess exit code is in the okValues list.

    :param target: a callable test
    :type target: callable
    :param maxtries: maximum number of runs
    :type maxtries: int
    :param maxfails: maximum number of failed runs
    :type maxfails: int
    :param okvalues: a sequence containing exit values of cmd which are
        considered to be successful runs.
    :type okvalues: seq
    :param args: arguments for running the target function
    :type args: seq
    :param kwargs: keyword arguments for running the target function
    :type kwargs: dict
    :return: a tuple of ints: tries, failures
    :rtype: tuple
    """
    if kwargs is None:
        kwargs = {}
    from multiprocessing import Process

    i, f = 0, 0
    while f < maxfails and i < maxtries:
        i += 1
        p = Process(target=target, args=args, kwargs=kwargs)
        p.start()
        p.join()
        if p.exitcode not in okvalues:
            f += 1
    return i, f


def calculateTestFuzziness(test, maxtries=100, maxfails=10, **kwargs):
    """Estimate the fuzziness of a test by running it many times and counting
    the failures. In this context, we assume that there is an underlying
    problem and but that the test is not perfect and only fails (triggers the
    problem) with a certain failure rate.

    :param testname: test name. see:
        :meth:`unittest.TestLoader.loadTestsFromName`
    :type testname: str
    :param maxtries: maximum number of runs
    :type maxtries: int
    :param maxfails: maximum number of failed runs
    :type maxfails: int
    :return: a tuple (f,df,n) where f is the failure rate, df is its standard
        deviation, and n is the number of consecutive times that the test
        should be passed to have a confidence>99%% that the bug is fixed'
    :rtype: tuple
    """
    print(
        (
            "Running the test %i times (or until it fails %i times)"
            + "to estimate the failure rate"
        )
        % (maxtries, maxfails)
    )
    import numpy

    if isinstance(test, str):
        tries, fails = loopTest(test, maxtries=maxtries, maxfails=maxfails)
    else:
        tries, fails = loopSubprocess(
            test, maxtries=maxtries, maxfails=maxfails, **kwargs
        )
    r = float(fails) / tries
    dr = numpy.sqrt(fails) / tries
    print("Failure rate = %g +/- %g  (%i/%i)" % (r, dr, fails, tries))
    # calculating n using p-value=1% and failure rate with -1 sigma
    n = numpy.ceil(numpy.log(0.01) / numpy.log(1 - (r - dr)))
    print(
        (
            "Number of consecutive times that the test should be passed "
            + "to have a confidence>99%% that the bug is fixed: %g"
        )
        % n
    )
    return r, dr, n


if __name__ == "__main__":

    def kk():
        # exits with fail 1/3 of the times
        from numpy.random import randint, seed

        seed()
        k = randint(3)
        if not k:
            exit(1)
        return

    print(calculateTestFuzziness(kk))
