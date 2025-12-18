"""
IP Network Data Type Class
"""

# pylint: disable=too-few-public-methods

import ipaddress

import nadap.mixin.ip
import nadap.types.base

DOC_DT_NAME = "IP Network"
DOC_DT_DESCRIPTION = """
An **ip_network** data type tests data for being an instance of
python's built-in class `str` and the string represents an IPv4
or IPv6 network.
"""
DOC_DT_FEATURES = """
- Validate IP specific attributes
- Validate against allowed and not allowed IP networks
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: ip_network
description: "Example IP network definition"

multicast: False
private: True

not_allowed_values:
  - 10.10.0.0/16
  - 192.168.0.0/24
  - 2001:cafe::/64

reference:
  key: ref_key
"""


class IpNetwork(nadap.mixin.ip.IpMixin, nadap.types.base.BaseType):
    """
    Add handling of strings representing IPv4 or IPv6 networks
    """

    _ip_data_type_name = "IP network"

    def _get_ip_obj(self, data):
        try:
            ipaddress.ip_address(data)
        except ValueError:
            return ipaddress.ip_network(data)
        raise ValueError()


DOC_DT_CLASS = IpNetwork  # pylint: disable=invalid-name
