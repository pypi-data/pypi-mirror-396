"""
Enum type class
"""

# pylint: disable=too-few-public-methods

import nadap.types.base
import nadap.mixin.allowed_value

DOC_DT_NAME = "Enum"
DOC_DT_DESCRIPTION = """
A **enum** data type represents a selection of allowed discrete data values.
"""
DOC_DT_FEATURES = """
- Supports **Referencing Feature**. Adds an option to lookup values in other namespaces.
- Data type conversion is not supported
"""
DOC_DT_YAML_EXAMPLE = """
type: enum
description: "Example enum definition"
default_value: 1

allowed_values:
  - key1: 1
    key2: string2
  - 1
  - 2
  -
    - nadap
    - rulez!

reference:
  key: ref_key
  mode: producer
"""


class Enum(nadap.mixin.allowed_value.AllowedValueMixin, nadap.types.base.BaseType):
    """
    Enum datatype class
    Only discrete values are allowed.
    """

    data_type_name = "enum"
    _convert_to_classes = {}


DOC_DT_CLASS = Enum  # pylint: disable=invalid-name
