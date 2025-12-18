"""
IP Interface Data Type Class
"""

# pylint: disable=too-few-public-methods

import ipaddress

import nadap.mixin.ip
import nadap.types.base

DOC_DT_NAME = "IP Interface"
DOC_DT_DESCRIPTION = """
An **ip_interface** data type tests data for being an instance of
python's built-in class `str` and the string represents an IPv4
or IPv6 interface.
"""
DOC_DT_FEATURES = """
- Validate IP specific attributes
- Validate against allowed and not allowed IP interfaces
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: ip_interface
description: "Example IP interface definition"

multicast: False
private: True

not_allowed_values:
  - 10.10.0.1/16
  - 192.168.0.1/24
  - 2001:cafe::1/64

reference:
  key: ref_key
"""


class IpInterface(nadap.mixin.ip.IpMixin, nadap.types.base.BaseType):
    """
    Add handling of strings representing IPv4 or IPv6 interfaces
    """

    _ip_data_type_name = "IP interface"

    def _get_ip_obj(self, data):
        try:
            ipaddress.ip_address(data)
        except ValueError:
            try:
                ipaddress.ip_network(data)
            except ValueError:
                return ipaddress.ip_interface(data)
        raise ValueError()


DOC_DT_CLASS = IpInterface  # pylint: disable=invalid-name
