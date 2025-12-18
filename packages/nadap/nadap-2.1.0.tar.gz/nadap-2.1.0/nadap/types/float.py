"""
Float data type classes
"""

# pylint: disable=too-few-public-methods

import nadap.types.base
import nadap.mixin.accuracy
import nadap.mixin.not_allowed_value
import nadap.mixin.min_max
import nadap.mixin.ranges
import nadap.mixin.allowed_value

DOC_DT_NAME = "Float"
DOC_DT_DESCRIPTION = """
A **float** data type tests data for being an instance of
python's built-in class `float`.

> If using *float* data type with allowed values and no conversion defined,
> check *enum* data type as a better option.
"""
DOC_DT_FEATURES = f"""
- Validate minimal and maximal float value{nadap.mixin.ranges.DOC_FEATURES}
- Validate against allowed and not allowed values
- Validate if float value meets allowed accuracy
- Conversion supports rounding the float value
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: float
description: "Example float definition"

minimum: 0.9
maximum: 3.0

not_allowed_values:
  - 3.0
  - 1.1
  - 0.9

reference: ref_key
"""


class Float(
    nadap.mixin.accuracy.AccuracyMixin,
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.mixin.min_max.MinMaxValueMixin,
    nadap.types.base.BaseType,
):
    """
    Float datatype class
    """

    data_type_name = "float"
    _cls_python_classes = [float]
    _convert_to_classes = {"str": str, "int": int}
    _doc_data_type = "float"


DOC_DT_CLASS = Float  # pylint: disable=invalid-name
