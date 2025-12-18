"""
IPv6 Interface Data Type Class
"""

# pylint: disable=too-few-public-methods

import ipaddress

import nadap.mixin.ip
import nadap.types.base

DOC_DT_NAME = "IPv6 Interface"
DOC_DT_DESCRIPTION = """
An **ip6_interface** data type tests data for being an instance of
python's built-in class `str` and the string represents an IPv6
interface.
"""
DOC_DT_FEATURES = """
- Validate IP specific attributes
- Validate against allowed and not allowed IPv6 interfaces
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: ip6_interface
description: "Example IPv6 interface definition"

multicast: False
private: True

not_allowed_values:
  - 2001:cafe::1/64
  - 2001:abba::1/64

reference:
  key: ref_key
"""


class Ip6Interface(nadap.mixin.ip.IpMixin, nadap.types.base.BaseType):
    """
    Add handling of strings representing IPv6 interfaces
    """

    _ip_data_type_name = "IPv6 interface"

    def _get_ip_obj(self, data):
        try:
            ipaddress.IPv6Address(data)
        except ValueError:
            try:
                ipaddress.IPv6Network(data)
            except ValueError:
                return ipaddress.IPv6Interface(data)
        raise ValueError()


DOC_DT_CLASS = Ip6Interface  # pylint: disable=invalid-name
