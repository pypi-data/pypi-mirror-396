"""
IP Address Data Type Class
"""

# pylint: disable=too-few-public-methods

import ipaddress

import nadap.mixin.ip
import nadap.mixin.ranges
import nadap.types.base

DOC_DT_NAME = "IP Address"
DOC_DT_DESCRIPTION = """
An **ip_address** data type tests data for being an instance of
python's built-in class `str` and the string represents an IPv4
or IPv6 address.
"""
DOC_DT_FEATURES = """
- Validate IP specific attributes
- Validate against allowed and not allowed IP address ranges
- Validate against allowed and not allowed IP addresses
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: ip_address
description: "Example IP address definition"

multicast: False
private: True

not_allowed_values:
  - 10.10.0.1
  - 192.168.0.1
  - 2001:cafe::1

reference:
  key: ref_key
"""


class IpAddress(
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.mixin.ip.IpMixin,
    nadap.types.base.BaseType,
):
    """
    Add handling of strings representing IPv4 or IPv6 addresses
    """

    _ip_data_type_name = "IP address"

    def _get_ip_obj(self, data):
        return ipaddress.ip_address(data)


DOC_DT_CLASS = IpAddress  # pylint: disable=invalid-name
