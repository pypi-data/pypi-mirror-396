"""
Integer data type classes
"""

# pylint: disable=too-few-public-methods

import nadap.types.base
import nadap.mixin.not_allowed_value
import nadap.mixin.min_max
import nadap.mixin.ranges
import nadap.mixin.allowed_value
from nadap.base import ValEnv
from nadap.errors import SchemaDefinitionError

DOC_DT_NAME = "Integer/String"
DOC_DT_DESCRIPTION = """
An **str_int** data type tests data for being an instance of
python's built-in class `int` or class `str` and string must
represent an integer value.

> Data is converted to `int` by default.
> Use `convert_to` option to enforce conversion to other data types.
"""
DOC_DT_FEATURES = f"""
- Validate minimal and maximal integer value{nadap.mixin.ranges.DOC_FEATURES}
- Validate against allowed and not allowed integer values
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: str_int
description: "Example str_int definition"

minimum: 1
maximum: 4096

not_allowed_values:
  - 1001
  - "1002"

reference:
  key: ref_key
  mode: consumer
"""


class StrInt(
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.mixin.min_max.MinMaxValueMixin,
    nadap.types.base.BaseType,
):
    """
    Integer/String datatype class
    """

    data_type_name = "str_int"
    _cls_python_classes = [int, str]
    _convert_to_classes = {"float": float, "str": str}
    _doc_data_type = "int|str[int]"

    def _test_data_type(self, data: any, path: str, env: "ValEnv" = None):
        super()._test_data_type(data=data, path=path, env=env)
        msg = ""
        try:
            data = int(data)
        except ValueError:
            msg = "String does not represent an integer value"
        if msg:
            if env is None:
                raise SchemaDefinitionError(
                    msg,
                    path,
                )
            self._create_finding_with_error(msg, path, env)
        return data


DOC_DT_CLASS = StrInt  # pylint: disable=invalid-name
