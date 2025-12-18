"""
8bit Integer data type classes
"""

# pylint: disable=too-few-public-methods

import nadap.types.base
import nadap.mixin.not_allowed_value
import nadap.mixin.min_max
import nadap.mixin.ranges
import nadap.mixin.allowed_value
from nadap.base import ValEnv
from nadap.errors import SchemaDefinitionError

DOC_DT_NAME = "8bit Integer"
DOC_DT_DESCRIPTION = f"""
An **int8** data type tests data for being an instance of
python's built-in class `int` and has a value within -{2**7} and {2**7 - 1}.

> If using *int8* data type with allowed values and no conversion defined,
> check *enum* data type as a better option.
"""
DOC_DT_FEATURES = f"""
- Validate minimal and maximal data value{nadap.mixin.ranges.DOC_FEATURES}
- Validate against allowed and not allowed integer values
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: int8
description: "Example int8 definition"

minimum: 1
maximum: 100

not_allowed_values:
  - 11
  - 12

reference:
  key: ref_key
  mode: consumer
"""


class Int8(
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.mixin.min_max.MinMaxValueMixin,
    nadap.types.base.BaseType,
):
    """
    8-bit Integer datatype class
    """

    data_type_name = "int8"
    _cls_python_classes = [int]
    _convert_to_classes = {"str": str, "float": float}
    _doc_data_type = "int"
    _minimum_default = -128
    _maximum_default = 127

    def _test_data_type(self, data: any, path: str, env: "ValEnv" = None) -> "any":
        data = super()._test_data_type(data=data, path=path, env=env)
        if not -(2**7) <= data < 2**7:
            msg = "Data is out of range of 'int8'"
            if env is None:
                raise SchemaDefinitionError(msg, path)
            self._create_finding_with_error(msg, path, env)
        return data


DOC_DT_CLASS = Int8  # pylint: disable=invalid-name
