"""
Bool type classes
"""

# pylint: disable=too-few-public-methods

import nadap.types.base

DOC_DT_NAME = "Bool"
DOC_DT_DESCRIPTION = """
A **bool** data type tests data for being an instance of
python's built-in class `bool`.
"""
DOC_DT_FEATURES = """
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: bool
description: "Example for a bool definition"
default_value: true

template_merge_options:
  recursive: < bool >
  list_merge: < str >
reference:
  key: ref_key
  mode: producer
  producer_scope: global
"""


class Bool(nadap.types.base.BaseType):
    """
    Bool datatype class
    """

    data_type_name = "bool"
    _cls_python_classes = [bool]


DOC_DT_CLASS = Bool  # pylint: disable=invalid-name
