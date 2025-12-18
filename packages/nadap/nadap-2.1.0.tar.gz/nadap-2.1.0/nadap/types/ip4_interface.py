"""
IPv4 Interface Data Type Class
"""

# pylint: disable=too-few-public-methods

import ipaddress

import nadap.mixin.ip
import nadap.types.base

DOC_DT_NAME = "IPv4 Interface"
DOC_DT_DESCRIPTION = """
An **ip4_interface** data type tests data for being an instance of
python's built-in class `str` and the string represents an IPv4
interface.
"""
DOC_DT_FEATURES = """
- Validate IP specific attributes
- Validate against allowed and not allowed IPv4 interfaces
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: ip4_interface
description: "Example IPv4 interface definition"

multicast: False
private: True

not_allowed_values:
  - 10.10.99.1/16
  - 192.168.0.1/24

reference:
  key: ref_key
"""


class Ip4Interface(nadap.mixin.ip.IpMixin, nadap.types.base.BaseType):
    """
    Add handling of strings representing IPv4 interfaces
    """

    _ip_data_type_name = "IPv4 interface"

    def _get_ip_obj(self, data):
        try:
            ipaddress.IPv4Address(data)
        except ValueError:
            try:
                ipaddress.IPv4Network(data)
            except ValueError:
                return ipaddress.IPv4Interface(data)
        raise ValueError()


DOC_DT_CLASS = Ip4Interface  # pylint: disable=invalid-name
