"""
None data type classes
"""

# pylint: disable=too-few-public-methods

import nadap.types.base

DOC_DT_NAME = "None"
DOC_DT_DESCRIPTION = """
A **none** data type tests data for being python's built-in `None`.
"""
DOC_DT_FEATURES = """
- Supports **Referencing Feature** (even if mostly senseless)
- Data type conversion is not supported
"""
DOC_DT_YAML_EXAMPLE = """
type: none
description: "Example for a none/null definition"
default_value: null
"""


class Null(nadap.types.base.BaseType):
    """
    None type datatype class
    """

    data_type_name = "none"
    _cls_python_classes = [type(None)]
    _convert_to_classes = {}


DOC_DT_CLASS = Null  # pylint: disable=invalid-name
