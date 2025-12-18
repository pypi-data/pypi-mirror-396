"""
Integer data type classes
"""

# pylint: disable=too-few-public-methods

import nadap.types.base
import nadap.mixin.accuracy
import nadap.mixin.not_allowed_value
import nadap.mixin.min_max
import nadap.mixin.ranges
import nadap.mixin.allowed_value
from nadap.base import ValEnv
from nadap.errors import SchemaDefinitionError

DOC_DT_NAME = "Float/String"
DOC_DT_DESCRIPTION = """
An **str_float** data type tests data for being an instance of
python's built-in class `float` or class `str` and string must
represent a float value.

> Data is converted to `float` by default.
> Use `convert_to` option to enforce conversion to other data types.
"""
DOC_DT_FEATURES = f"""
- Validate minimal and maximal value{nadap.mixin.ranges.DOC_FEATURES}
- Validate against allowed and not allowed values
- Validate if float value meets allowed accuracy
- Conversion supports rounding the float value
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: str_float
description: "Example str_float definition"

minimum: 0.9
maximum: 3.0

not_allowed_values:
  - 3.0
  - "1.1"
  - 0.9

reference: ref_key
"""


class StrFloat(
    nadap.mixin.accuracy.AccuracyMixin,
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.mixin.min_max.MinMaxValueMixin,
    nadap.types.base.BaseType,
):
    """
    Float/String datatype class
    """

    data_type_name = "str_float"
    _cls_python_classes = [float, str]
    _convert_to_classes = {"int": int, "str": str}
    _doc_data_type = "int|str[float]"

    def _test_data_type(self, data: any, path: str, env: "ValEnv" = None):
        super()._test_data_type(data=data, path=path, env=env)
        if isinstance(data, float):
            return data
        msg = ""
        try:
            r_data = float(data)
            try:
                int(data)
            except ValueError:
                pass
            else:
                msg = "String represents an integer value"
        except ValueError:
            msg = "String does not represent a float value"
        if msg:
            if env is None:
                raise SchemaDefinitionError(msg, path)
            self._create_finding_with_error(msg, path, env)
        return r_data


DOC_DT_CLASS = StrFloat  # pylint: disable=invalid-name
