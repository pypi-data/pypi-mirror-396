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

"""This module contains the base taurus name validator classes"""

__all__ = [
    "TangoAuthorityNameValidator",
    "TangoDeviceNameValidator",
    "TangoAttributeNameValidator",
]

__docformat__ = "restructuredtext"

from taurus.core.taurusvalidator import (
    TaurusAttributeNameValidator,
    TaurusAuthorityNameValidator,
    TaurusDeviceNameValidator,
)
from taurus.core.util.fqdn import fqdn_no_alias

# todo: I do not understand the behaviour of getNames for Auth, Dev and Attr in
#      the case when the fullname does not match the regexp. For Auth it
#      returns a 3-tuple, for devs a 2-tuple and for attrs and conf a single
#      None. This is not coherent to what the method returns when it matches
#      the regexp (always a 3-tuple)


class TangoAuthorityNameValidator(TaurusAuthorityNameValidator):
    """Validator for Tango authority names. Apart from the standard named
    groups (scheme, authority, path, query and fragment), the following named
    groups are created:

     - host: tango host name, without port.
     - port: port number
    """

    scheme = "(tango|tango-nodb)"
    authority = (
        r"//((?P<host>([\w\-_]+\.)*[\w\-_]+):(?P<port>\d{1,5})"
        + r"|([\w\-_]+\.)*[\w\-_]+:\d{1,5}"
        + r"(,([\w\-_]+\.)*[\w\-_]+:\d{1,5})+)"
    )
    path = "(?!)"
    query = "(?!)"
    fragment = "(?!)"
    default_scheme = "tango"

    def getUriGroups(self, name, strict=None):
        """Reimplementation of getUriGroups to fix the host and authority
        name using fully qualified domain name for the host.
        """
        ret = TaurusAuthorityNameValidator.getUriGroups(self, name, strict)
        if ret is not None and ret.get("host", None) is not None:
            ret["host"] = fqdn_no_alias(ret["host"])
            ret["authority"] = "//{host}:{port}".format(**ret)
        return ret


class TangoDeviceNameValidator(TaurusDeviceNameValidator):
    """Validator for Tango device names. Apart from the standard named
    groups (scheme, authority, path, query and fragment), the following named
    groups are created:

     - devname: device name (either alias or slashed name)
     - [_devalias]: device alias
     - [_devslashname]: device name in slashed (a/b/c) form
     - [host] as in :class:`TangoAuthorityNameValidator`
     - [port] as in :class:`TangoAuthorityNameValidator`

    Note: brackets on the group name indicate that this group will only contain
    a string if the URI contains it.
    """

    scheme = "(tango|tango-nodb)"
    authority = TangoAuthorityNameValidator.authority
    path = (
        r"/?(?P<devname>((?P<_devalias>[^/?#:]+)|"
        + r"(?P<_devslashname>[^/?#:]+/[^/?#:]+/[^/?#:]+)))"
    )
    query = "(?!)"
    fragment = "(?P<_fragmentdb>dbase=(yes|no)$)"
    default_scheme = "tango"

    names_cache = {}

    def getUriGroups(self, name, strict=None):
        """Reimplementation of getUriGroups to fix the host and authority
        name using fully qualified domain name for the host.
        """
        ret = TaurusDeviceNameValidator.getUriGroups(self, name, strict)
        if ret is not None and ret.get("host", None) is not None:
            ret["host"] = fqdn_no_alias(ret["host"])
            ret["authority"] = "//{host}:{port}".format(**ret)
        # use special scheme "tango-nodb" if the name contains #dbase=no
        if ret is not None and ret.get("_fragmentdb", None) == "dbase=no":
            ret["scheme"] = "tango-nodb"
        return ret

    def getNames(self, fullname, factory=None, queryAuth=True):
        """reimplemented from :class:`TaurusDeviceNameValidator`. It accepts an
        extra keyword arg `queryAuth` which, if set to False, will prevent the
        validator from trying to query a TaurusAuthority to obtain missing info
        such as the devslashname <--> devalias correspondence.
        """
        if fullname in self.names_cache:
            return self.names_cache[fullname]

        groups = self.getUriGroups(fullname)
        if groups is None:
            return None

        default_authority = None
        if factory is None:
            from taurus import Factory

            factory = Factory(scheme="tango")
        default_authority = factory.get_default_tango_host()

        if default_authority is None:
            try:
                import tango

                tango_host = tango.ApiUtil.get_env_var("TANGO_HOST")
                v = TangoAuthorityNameValidator()
                g = v.getUriGroups("tango://{}".format(tango_host))
                default_authority = g.get("authority")
            except Exception:
                default_authority = None

        authority = groups.get("authority")
        if authority is None:
            groups["authority"] = authority = default_authority

        db = None
        if queryAuth and groups["scheme"] != "tango-nodb":
            try:
                db = factory.getAuthority("tango:{}".format(authority))
            except Exception:
                pass

        # note, since we validated, we either have alias or slashname (not
        # both)
        _devalias = groups.get("_devalias")
        _devslashname = groups.get("_devslashname")

        if _devslashname is None and db is not None:
            # get _devslashname from the alias using the DB
            _devslashname = db.getElementFullName(_devalias)
            groups["_devslashname"] = _devslashname

        if _devslashname is None:
            # if we still do not have a slashname, we can only give the short
            return None, None, _devalias

        # we can now construct everything. First the complete:
        complete = "{scheme}:{authority}/{_devslashname}".format(**groups)

        # then the normal
        normal = "{authority}/{_devslashname}".format(**groups)
        if default_authority and authority.lower() == default_authority.lower():
            normal = "{_devslashname}".format(**groups)

        # and finally the short
        if _devalias is not None:
            short = _devalias
        else:
            if db is not None:
                # get the alias from the DB (if it is defined)
                short = db.getElementAlias(_devslashname) or _devslashname
            else:
                short = _devslashname

        self.names_cache[fullname] = complete, normal, short

        return complete, normal, short

    @property
    def nonStrictNamePattern(self):
        """In non-strict mode, allow double-slash even if there is no
        Authority. (e.g., "tango://a/b/c" passes this non-strict form)
        """
        pattern = (
            r"^((?P<scheme>%(scheme)s)://)?"
            + r"((?P<authority>%(authority)s)(?=/))?"
            + r"(?P<path>%(path)s)"
            + r"(\?(?P<query>%(query)s))?"
            + r"(#%(fragment)s)?$"
        )
        authority = r"(?P<host>([\w\-_]+\.)*[\w\-_]+):(?P<port>\d{1,5})"
        path = (
            "/?(?P<devname>((?P<_devalias>([^/?#:]+))|"
            + "(?P<_devslashname>[^/?#:]+/[^/?#:]+/[^/?#:]+)))"
        )

        return pattern % dict(
            scheme=self.scheme,
            authority=authority,
            path=path,
            query="(?!)",
            fragment="(?!)",
        )


class TangoAttributeNameValidator(TaurusAttributeNameValidator):
    """Validator for Tango attribute names. Apart from the standard named
    groups (scheme, authority, path, query and fragment), the following named
    groups are created:

     - attrname: attribute name including device name
     - _shortattrname: attribute name excluding device name
     - devname: as in :class:`TangoDeviceNameValidator`
     - [_devalias]: as in :class:`TangoDeviceNameValidator`
     - [_devslashname]: as in :class:`TangoDeviceNameValidator`
     - [host] as in :class:`TangoAuthorityNameValidator`
     - [port] as in :class:`TangoAuthorityNameValidator`
     - [cfgkey] same as fragment (for bck-compat use only)

    Note: brackets on the group name indicate that this group will only contain
    a string if the URI contains it.
    """

    scheme = "(tango|tango-nodb)"
    authority = TangoAuthorityNameValidator.authority
    path = "(?P<attrname>{0}/(?P<_shortattrname>[^/?:#]+))".format(
        TangoDeviceNameValidator.path
    )
    query = "(?!)"
    fragment = "((?P<_fragmentdb>dbase=(yes|no)$)|(?P<cfgkey>[^# ]*))"

    default_scheme = "tango"

    def getUriGroups(self, name, strict=None):
        """Reimplementation of getUriGroups to fix the host and authority
        name using fully qualified domain name for the host.
        """
        ret = TaurusAttributeNameValidator.getUriGroups(self, name, strict)
        if ret is not None:
            if ret.get("host", None) is not None:
                ret["host"] = fqdn_no_alias(ret["host"])
                auth = "//{host}:{port}".format(**ret)
                ret["authority"] = auth

        # use special scheme "tango-nodb" if the name contains #dbase=no
        if ret is not None and ret.get("_fragmentdb", None) == "dbase=no":
            ret["scheme"] = "tango-nodb"
        return ret

    def getNames(self, fullname, factory=None, queryAuth=True, fragment=False):
        """Returns the complete and short names"""

        groups = self.getUriGroups(fullname)
        if groups is None:
            return None

        complete, normal, short = None, None, groups.get("_shortattrname")

        # reuse the getNames from the Device validator...
        devname = fullname.rsplit("#", 1)[0].rsplit("/", 1)[0]
        v = TangoDeviceNameValidator()
        devcomplete, devnormal, _ = v.getNames(
            devname, factory=factory, queryAuth=queryAuth
        )
        if devcomplete is not None:
            complete = "{}/{}".format(devcomplete, short)
        if devnormal is not None:
            normal = "{}/{}".format(devnormal, short)

        # return fragment if requested (ignores the special #dbase=yes|no case)
        if fragment:
            key = groups.get("cfgkey", None)
            return complete, normal, short, key

        return complete, normal, short

    @property
    def nonStrictNamePattern(self):
        """In non-strict mode, allow double-slash even if there is no
        Authority. Also allow old-style "?configuration[=cfgkey]" instead of
        fragment. If cfgkey is present, it is also stored in the "fragment"
        named group. For example, "tango://a/b/c/d?configuration=label" passes
        this non-strict form, and the named group "fragment" will contain
        "label" """

        pattern = (
            r"^((?P<scheme>%(scheme)s)://)?"
            + r"((?P<authority>%(authority)s)(?=/))?"
            + r"(?P<path>%(path)s)"
            + r"(\?(?P<query>%(query)s))?"
            + r"(#%(fragment)s)?$"
        )
        authority = r"(?P<host>([\w\-_]+\.)*[\w\-_]+):(?P<port>\d{1,5})"
        query = "configuration(=(?P<fragment>(?P<cfgkey>[^# ]+)))?"

        return pattern % dict(
            scheme=self.scheme,
            authority=authority,
            path=self.path,
            query=query,
            fragment="(?!)",
        )
