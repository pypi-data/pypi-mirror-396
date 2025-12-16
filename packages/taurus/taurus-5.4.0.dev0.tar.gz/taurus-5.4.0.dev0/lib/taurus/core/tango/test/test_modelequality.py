import pytest
import tango

import taurus
from taurus.core.tango.tangovalidator import TangoDeviceNameValidator


class _DummyDev(tango.server.Device):
    @tango.server.attribute
    def attr1(self):
        return 1.0

    @tango.server.attribute
    def attr2(self):
        return 2.0


devices_info = (
    {
        "class": _DummyDev,
        "devices": [
            {"name": "test/device1/1"},
            {"name": "test/device1/2"},
        ],
    },
)


@pytest.mark.forked
def test_device_equality():
    with tango.test_context.MultiDeviceTestContext(
        devices_info, process=True, timeout=15
    ) as context:
        v = TangoDeviceNameValidator()
        name1, _, _ = v.getNames(context.get_device_access("test/device1/1"))
        name2, _, _ = v.getNames(context.get_device_access("test/device1/2"))
        sch, rest = name1.split(":", 1)
        name1b = ":".join((sch, rest.upper()))
        # same DS, different device ==> different
        assert taurus.Device(name1) is not taurus.Device(name2)
        # same DS, same device, same name  ==> equal
        assert taurus.Device(name1) is taurus.Device(name1)
        # same DS, same device, different capitalization in name  ==> equal
        assert taurus.Device(name1) is taurus.Device(name1b)


@pytest.mark.forked
def test_attr_equality():
    with tango.test_context.MultiDeviceTestContext(
        devices_info, process=True, timeout=15
    ) as context:
        v = TangoDeviceNameValidator()
        name1, _, _ = v.getNames(context.get_device_access("test/device1/1"))
        name2, _, _ = v.getNames(context.get_device_access("test/device1/2"))

        # same dev, different attr ==> different
        assert taurus.Attribute(name1 + "/attr1") is not taurus.Attribute(
            name1 + "/attr2"
        )
        # same attr name, same DS, different device ==> different
        assert taurus.Attribute(name1 + "/attr1") is not taurus.Attribute(
            name2 + "/attr1"
        )
        # same attr+fragment name, same DS, different device ==> different
        assert taurus.Attribute(name1 + "/attr1#label") is not taurus.Attribute(
            name2 + "/attr1#label"
        )

        # same DS, same device, same name  ==> equal
        assert taurus.Attribute(name1 + "/attr1") is taurus.Attribute(name1 + "/attr1")
        # same DS, same device, different capitalization in name  ==> equal
        assert taurus.Attribute(name1 + "/attr1") is taurus.Attribute(name1 + "/ATTR1")
        # same DS, same device, same name+fragment  ==> equal
        assert taurus.Attribute(name1 + "/attr1#label") is taurus.Attribute(
            name1 + "/attr1#label"
        )
        # same DS, same device, same name different fragment  ==> equal
        assert taurus.Attribute(name1 + "/attr1#label") is taurus.Attribute(
            name1 + "/attr1#range"
        )
