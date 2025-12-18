"""
Integer data type classes
"""

# pylint: disable=too-few-public-methods

import nadap.types.base
import nadap.mixin.not_allowed_value
import nadap.mixin.min_max
import nadap.mixin.ranges
import nadap.mixin.allowed_value

DOC_DT_NAME = "Integer"
DOC_DT_DESCRIPTION = """
An **int** data type tests data for being an instance of
python's built-in class `int`.

> If using *int* data type with allowed values and no conversion defined,
> check *enum* data type as a better option.
"""
DOC_DT_FEATURES = f"""
- Validate minimal and maximal integer value{nadap.mixin.ranges.DOC_FEATURES}
- Validate against allowed and not allowed integer values
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: int
description: "Example int definition"

minimum: 1
maximum: 4096

not_allowed_values:
  - 1001
  - 1002

reference:
  key: ref_key
  mode: consumer
"""


class Int(
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.mixin.min_max.MinMaxValueMixin,
    nadap.types.base.BaseType,
):
    """
    Integer datatype class
    """

    data_type_name = "int"
    _cls_python_classes = [int]
    _convert_to_classes = {"str": str, "float": float}
    _doc_data_type = "int"


DOC_DT_CLASS = Int  # pylint: disable=invalid-name
