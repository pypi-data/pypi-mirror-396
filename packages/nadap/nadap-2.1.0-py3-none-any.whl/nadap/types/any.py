"""
Any type classes
"""

import nadap.types.base

DOC_DT_NAME = "Any"
DOC_DT_DESCRIPTION = """
An **any** data type represents any data.
"""
DOC_DT_FEATURES = """
- Supports **Referencing Feature**
- Data type conversion is not supported
"""
DOC_DT_YAML_EXAMPLE = """
type: any
description: "Example for an any definition"
default_value: ["nadap", "rulez"]

reference:
  key: ref_key
  mode: producer
  producer_scope: global
"""


class Any(nadap.types.base.BaseType):
    """
    Any datatype class
    """

    # pylint: disable=too-few-public-methods

    data_type_name = "any"
    _convert_to_classes = {}

    def _test_data_type(self, data: any, path: str, env=None):
        # pylint: disable=unused-argument
        return data


DOC_DT_CLASS = Any  # pylint: disable=invalid-name
