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

DOC_DT_NAME = "Number/String"
DOC_DT_DESCRIPTION = """
An **str_number** data type tests data for being an instance of
python's built-in class `int`, `float` or class `str` and string must
represent an integer or a float value.

> String is converted to `float` if representing an float value
> or to `int` if representing a integer value
> Use `convert_to` option to enforce convertion to other data types.
"""
DOC_DT_FEATURES = f"""
- Validate minimal and maximal number value{nadap.mixin.ranges.DOC_FEATURES}
- Validate against allowed and not allowed number values
- Validate if float value meets allowed accuracy
- Conversion supports rounding the float value
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: str_number
description: "Example str_number definition"

minimum: 1
maximum: 3.0

not_allowed_values:
  - 3.0
  - 1
  - "0.9"
  - "4"

reference: ref_key
"""


class StrNumber(
    nadap.mixin.accuracy.AccuracyMixin,
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.mixin.min_max.MinMaxValueMixin,
    nadap.types.base.BaseType,
):
    """
    Number/String datatype class
    """

    data_type_name = "str_number"
    _cls_python_classes = [int, float, str]
    _convert_to_classes = {"float": float, "int": int, "str": str}
    _doc_data_type = "float|int|str[float|int]"

    def _test_data_type(self, data: any, path: str, env: "ValEnv" = None):
        super()._test_data_type(data=data, path=path, env=env)
        if isinstance(data, float):
            return data
        msg = ""
        try:
            r_data = float(data)
            try:
                r_data = int(data)
            except ValueError:
                pass
        except ValueError:
            msg = "String does not represent an integer or a float value"
        if msg:
            if env is None:
                raise SchemaDefinitionError(msg, path)
            self._create_finding_with_error(msg, path, env)
        return r_data


DOC_DT_CLASS = StrNumber  # pylint: disable=invalid-name
