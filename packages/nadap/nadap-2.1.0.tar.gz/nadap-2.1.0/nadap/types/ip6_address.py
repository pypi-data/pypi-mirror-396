"""
IPv6 Address Data Type Class
"""

# pylint: disable=too-few-public-methods

import ipaddress

import nadap.mixin.ip
import nadap.mixin.ranges
import nadap.types.base

DOC_DT_NAME = "IPv6 Address"
DOC_DT_DESCRIPTION = """
An **ip6_address** data type tests data for being an instance of
python's built-in class `str` and the string represents an IPv6
address.
"""
DOC_DT_FEATURES = """
- Validate IP specific attributes
- Validate against allowed and not allowed IPv6 address ranges
- Validate against allowed and not allowed IPv6 addresses
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: ip6_address
description: "Example IPv6 address definition"

multicast: False
private: True

not_allowed_values:
  - 2001:cafe::1
  - 2001:abba::1

reference:
  key: ref_key
"""


class Ip6Address(
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.mixin.ip.IpMixin,
    nadap.types.base.BaseType,
):
    """
    Add handling of strings representing IPv6 addresses
    """

    _ip_data_type_name = "IPv6 address"

    def _get_ip_obj(self, data):
        return ipaddress.IPv6Address(data)


DOC_DT_CLASS = Ip6Address  # pylint: disable=invalid-name
