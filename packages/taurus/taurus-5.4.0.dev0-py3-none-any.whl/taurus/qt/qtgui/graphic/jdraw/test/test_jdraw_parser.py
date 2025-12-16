import os

import pytest

from taurus.external.qt.QtCore import PYSIDE2
from taurus.qt.qtgui.graphic import (
    TaurusGraphicsScene,
    TaurusJDrawGraphicsFactory,
)

from ..jdraw_parser import parse


@pytest.mark.skipif(PYSIDE2, reason="Avoid segfault when using PySide2")
def test_jdraw_parser(qtbot):
    """Check that jdraw_parser does not break with JDBar elements"""
    fname = os.path.join(os.path.dirname(__file__), "res", "bug1077.jdw")
    factory = TaurusJDrawGraphicsFactory(None)
    p = parse(fname, factory)
    assert isinstance(p, TaurusGraphicsScene)


if __name__ == "__main__":
    test_jdraw_parser()
