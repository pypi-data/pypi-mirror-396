"""
Bool type classes
"""

# pylint: disable=too-few-public-methods

from nadap.base import UNDEFINED
import nadap.types.bool

DOC_DT_NAME = "Bool-True"
DOC_DT_DESCRIPTION = """
A **bool_true** data type tests data for being an instance of
python's built-in class `bool`.
It has a pre-defined default value set to `True`.
"""
DOC_DT_FEATURES = """
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: bool_true
description: "Example for a bool_true definition"

reference:
  key: ref_key
  mode: producer
  producer_scope: global
"""


class BoolTrue(nadap.types.bool.Bool):
    """
    Bool datatype class with true as default value
    """

    data_type_name = "bool_true"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # pylint: disable=access-member-before-definition
        # false-positiv in pylint in combination with pre-commit
        if self.default_value is UNDEFINED:
            self.default_value = True


DOC_DT_CLASS = BoolTrue  # pylint: disable=invalid-name
