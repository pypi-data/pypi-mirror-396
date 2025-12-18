"""
32bit unsigned Integer data type classes
"""

# pylint: disable=too-few-public-methods

import nadap.types.base
import nadap.mixin.not_allowed_value
import nadap.mixin.min_max
import nadap.mixin.ranges
import nadap.mixin.allowed_value
from nadap.base import ValEnv
from nadap.errors import SchemaDefinitionError

DOC_DT_NAME = "32bit unsigned Integer"
DOC_DT_DESCRIPTION = f"""
An **uint32** data type tests data for being an instance of
python's built-in class `int` and has a value within 0 and {2**32 - 1}.

> If using *uint32* data type with allowed values and no conversion defined,
> check *enum* data type as a better option.
"""
DOC_DT_FEATURES = f"""
- Validate minimal and maximal data value{nadap.mixin.ranges.DOC_FEATURES}
- Validate against allowed and not allowed integer values
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: uint32
description: "Example uint32 definition"

minimum: 1
maximum: 1000000

not_allowed_values:
  - 101
  - 100002

reference:
  key: ref_key
  mode: consumer
"""


class Uint32(
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.mixin.min_max.MinMaxValueMixin,
    nadap.types.base.BaseType,
):
    """
    8-bit unsigned Integer datatype class
    """

    data_type_name = "uint32"
    _cls_python_classes = [int]
    _convert_to_classes = {"str": str, "float": float}
    _doc_data_type = "int"
    _minimum_default = 0
    _maximum_default = 4294967295

    def _test_data_type(self, data: any, path: str, env: "ValEnv" = None) -> "any":
        data = super()._test_data_type(data=data, path=path, env=env)
        if not 0 <= data < 2**32:
            msg = "Data is out of range of 'uint32'"
            if env is None:
                raise SchemaDefinitionError(msg, path)
            self._create_finding_with_error(msg, path, env)
        return data


DOC_DT_CLASS = Uint32  # pylint: disable=invalid-name
