"""
IPv6 Network Data Type Class
"""

# pylint: disable=too-few-public-methods

import ipaddress

import nadap.mixin.ip
import nadap.types.base

DOC_DT_NAME = "IPv6 Network"
DOC_DT_DESCRIPTION = """
An **ip6_network** data type tests data for being an instance of
python's built-in class `str` and the string represents an IPv6
network.
"""
DOC_DT_FEATURES = """
- Validate IP specific attributes
- Validate against allowed and not allowed IPv6 networks
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: ip6_network
description: "Example IPv6 network definition"

multicast: False
private: True

not_allowed_values:
  - 2001:cafe::/64
  - 2001:abba::/64

reference:
  key: ref_key
"""


class Ip6Network(
    nadap.mixin.ip.Ip6NetworkMixin, nadap.mixin.ip.IpMixin, nadap.types.base.BaseType
):
    """
    Add handling of strings representing IPv6 networks
    """

    _ip_data_type_name = "IPv6 network"

    def _get_ip_obj(self, data):
        try:
            ipaddress.IPv6Address(data)
        except ValueError:
            return ipaddress.IPv6Network(data)
        raise ValueError()


DOC_DT_CLASS = Ip6Network  # pylint: disable=invalid-name
