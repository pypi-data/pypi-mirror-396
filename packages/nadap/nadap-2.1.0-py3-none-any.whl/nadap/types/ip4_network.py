"""
IPv4 Network Data Type Class
"""

# pylint: disable=too-few-public-methods

import ipaddress

import nadap.mixin.ip
import nadap.types.base

DOC_DT_NAME = "IPv4 Network"
DOC_DT_DESCRIPTION = """
An **ip4_network** data type tests data for being an instance of
python's built-in class `str` and the string represents an IPv4
network.
"""
DOC_DT_FEATURES = """
- Validate IP specific attributes
- Validate against allowed and not allowed IP networks
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: ip4_network
description: "Example IPv4 network definition"

multicast: False
private: True

not_allowed_values:
  - 10.20.0.0/16
  - 192.168.0.0/24

reference:
  key: ref_key
"""


class Ip4Network(
    nadap.mixin.ip.Ip4NetworkMixin, nadap.mixin.ip.IpMixin, nadap.types.base.BaseType
):
    """
    Add handling of strings representing IPv4 networks
    """

    _ip_data_type_name = "IPv4 network"

    def _get_ip_obj(self, data):
        try:
            ipaddress.IPv4Address(data)
        except ValueError:
            return ipaddress.IPv4Network(data)
        raise ValueError()


DOC_DT_CLASS = Ip4Network  # pylint: disable=invalid-name
