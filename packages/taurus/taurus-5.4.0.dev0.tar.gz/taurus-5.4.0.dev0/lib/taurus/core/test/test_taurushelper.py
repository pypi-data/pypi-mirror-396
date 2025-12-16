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

"""Test for taurus.core.taurushelper"""

__docformat__ = "restructuredtext"

import pytest

import taurus
from taurus.core import TaurusAttribute, TaurusAuthority, TaurusDevice
from taurus.core import TaurusElementType as etype


def _skip_if_scheme_not_supported(name):
    manager = taurus.Manager()
    scheme = manager.getScheme(name)
    supportedSchemes = list(manager.getPlugins().keys())
    if scheme not in supportedSchemes:
        pytest.skip("'{}' scheme not supported".format(scheme))


@pytest.mark.parametrize(
    "name, etypes, strict, expected",
    [
        ("eval:foo", None, True, True),
        ("eval:@foo", None, True, True),
        ("eval://localhost", None, True, True),
        (
            "eval:foo",
            [etype.Attribute, etype.Device],
            True,
            True,
        ),
        (
            "eval:foo",
            [etype.Authority, etype.Device],
            True,
            False,
        ),
        ("eval:foo", [etype.Attribute], True, True),
        ("eval:foo", [etype.Device], True, False),
        ("eval:foo", [etype.Authority], True, False),
        ("eval://", None, True, False),
        ("eval://2+3?configuration=label", None, True, False),
        ("eval://2+3?configuration=label", None, False, True),
        ("tango:a/b/c/d", None, True, True),
        ("tango-nodb:a/b/c/d", None, True, True),
        ("tango-nodb://a/b/c/d", None, True, False),
        ("tango-nodb://a/b/c/d", None, False, True),
        ("tango-nodb:a/b/c/d", [etype.Attribute], True, True),
        ("tango-nodb:a/b/c/d", [etype.Device], True, False),
        ("tango-nodb:a/b/c/d", [etype.Device], True, False),
        ("ca:foo", None, True, True),
    ],
)
def test_taurus_isValid(name, etypes, strict, expected):
    """check taurus.isValidName helper"""
    _skip_if_scheme_not_supported(name)
    returned = taurus.isValidName(name, etypes=etypes, strict=strict)
    assert returned == expected


@pytest.mark.parametrize(
    "name, etypes, implicit, expected",
    [
        ("foo", [etype.Attribute], "eval", True),
        ("foo", [etype.Attribute], "tango", False),
        ("//foo:10000", [etype.Authority], "tango", True),
        ("//foo:10000", [etype.Authority], "eval", False),
        ("eval:foo", [etype.Attribute], "tango", True),
        ("tango://foo:10000", [etype.Authority], "eval", True),
    ],
)
def test_implicit_scheme(monkeypatch, name, etypes, implicit, expected):
    """check taurus.isValidName with implicit scheme"""
    _skip_if_scheme_not_supported(name)
    from taurus import tauruscustomsettings

    monkeypatch.setattr(tauruscustomsettings, "DEFAULT_SCHEME", implicit)
    assert taurus.isValidName(name, etypes=etypes) == expected


def test_taurus_isValidName_():
    """Testing that an unsupported scheme validates as False"""
    ret = taurus.isValidName("_unsupported_://foo")
    msg = "Validating unsupported schemes must return False (got %s)" % ret
    assert not ret, msg


@pytest.mark.parametrize(
    "helper,name,klass",
    [
        (taurus.Authority, "eval://localhost", TaurusAuthority),
        (taurus.Authority, "ca://", TaurusAuthority),
        (taurus.Device, "eval://localhost/@Foo", TaurusDevice),
        (taurus.Device, "eval://localhost/@Foo", TaurusDevice),
        (taurus.Device, "eval:@Foo", TaurusDevice),
        (taurus.Device, "eval://dev=Foo", TaurusDevice),
        (taurus.Device, "eval:@datetime.*", TaurusDevice),
        (taurus.Device, "eval:@datetime.date(2017,3,29)", TaurusDevice),
        # (taurus.Device, 'tango:a/b/c', TaurusDevice),
        (taurus.Device, "tango-nodb:a/b/c", TaurusDevice),
        # (taurus.Device, "ca:/", TaurusDevice),
        (taurus.Attribute, "eval:1", TaurusAttribute),
        (taurus.Attribute, "tango:a/b/c/d", TaurusAttribute),
        (taurus.Attribute, "tango-nodb:a/b/c/d", TaurusAttribute),
        # (taurus.Attribute, "ca:foo", TaurusAttribute),
    ],
)
def test_model_helper(helper, name, klass):
    _skip_if_scheme_not_supported(name)
    a = helper(name)
    assert isinstance(a, klass)


def test_getValidatorFromName():
    """check that getValidatorFromName returns the expected values"""

    assert isinstance(
        taurus.getValidatorFromName("eval:@foo"),
        taurus.core.evaluation.evalvalidator.EvaluationDeviceNameValidator,
    )
    assert taurus.getValidatorFromName("eval:@/") is None
    assert taurus.getValidatorFromName("unsupported:scheme") is None
