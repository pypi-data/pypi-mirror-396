"""
IPv4 Address Data Type Class
"""

# pylint: disable=too-few-public-methods

import ipaddress

import nadap.mixin.ip
import nadap.mixin.ranges
import nadap.types.base

DOC_DT_NAME = "IPv4 Address"
DOC_DT_DESCRIPTION = """
An **ip4_address** data type tests data for being an instance of
python's built-in class `str` and the string represents an IPv4
address.
"""
DOC_DT_FEATURES = """
- Validate IP specific attributes
- Validate against allowed and not allowed IPv4 address ranges
- Validate against allowed and not allowed IPv4 addresses
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: ip4_address
description: "Example IPv4 address definition"

multicast: False
private: True

not_allowed_values:
  - 10.10.10.1
  - 192.168.0.1

reference:
  key: ref_key
"""


class Ip4Address(
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.mixin.ip.IpMixin,
    nadap.types.base.BaseType,
):
    """
    Add handling of strings representing IPv4 addresses
    """

    _ip_data_type_name = "IPv4 address"

    def _get_ip_obj(self, data):
        return ipaddress.IPv4Address(data)


DOC_DT_CLASS = Ip4Address  # pylint: disable=invalid-name
