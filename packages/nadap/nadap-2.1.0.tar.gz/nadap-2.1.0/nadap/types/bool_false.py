"""
Bool type classes
"""

# pylint: disable=too-few-public-methods

from nadap.base import UNDEFINED
import nadap.types.bool

DOC_DT_NAME = "Bool-False"
DOC_DT_DESCRIPTION = """
A **bool_false** data type tests data for being an instance of
python's built-in class `bool`.
It has a pre-defined default value set to `False`.
"""
DOC_DT_FEATURES = """
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: bool_false
description: "Example for a bool_false definition"

reference:
  key: ref_key
  mode: producer
  producer_scope: global
"""


class BoolFalse(nadap.types.bool.Bool):
    """
    Bool datatype class with false as default value
    """

    data_type_name = "bool_false"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # pylint: disable=access-member-before-definition
        # false-positiv in pylint in combination with pre-commit
        if self.default_value is UNDEFINED:
            self.default_value = False


DOC_DT_CLASS = BoolFalse  # pylint: disable=invalid-name
