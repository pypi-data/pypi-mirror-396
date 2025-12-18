"""
4-Byte Value data type class
"""

# pylint: disable=too-few-public-methods

from typing import TYPE_CHECKING

import nadap.types.base
import nadap.mixin.min_max
import nadap.mixin.ranges
import nadap.mixin.allowed_value
import nadap.mixin.not_allowed_value
import nadap.schema
from nadap.base import ValEnv, CONVERT_DATA, str_list_out
from nadap.errors import SchemaDefinitionError
from nadap.doc import UnorderedTextList

if TYPE_CHECKING:
    from nadap.doc import TextField


DOC_DT_NAME = "4-Byte Value"
DOC_DT_DESCRIPTION = """
A **4byte_value** data type tests data for being an instance of
python's built-in class `int` or `str` and if it represents a 4-Byte value.
"""
DOC_DT_FEATURES = """
- Validate integer value
- Validate string in colon-separated format
- Validate string in different dot-separated formats
- Validate hexadecimal string
- Supports format conversion
- Validate minimal and maximal value
- Validate against allowed and not allowed value ranges
- Validate against allowed and not allowed values
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = r"""
type: 4byte_value
description: "Example 4byte_value definition"
default_value: "0:123"

formats:
  - colon-separated
  - 3-dot-separated
  - hex
  - int
convert_to_format: hex

not_allowed_values:
  - 111
  - 1:1
  - 0xff
  - 192.168.1.1

reference: ref_key
"""

CANONICAL = "canonical"
BIT_REVERSED = "bit-reversed"

DOT1_FORMAT = "1-dot-separated"
DOT3_FORMAT = "3-dot-separated"
INT_FORMAT = "int"  # 1003458
COLON_FORMAT = "colon-separated"  # 12:65500
HEX_FORMAT = "hex"  # 0x0012abff or 0x12abff


class Byte4Value(
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.mixin.min_max.MinMaxValueMixin,
    nadap.types.base.BaseType,
):
    """
    4-Byte Value datatype class
    """

    data_type_name = "4byte_value"
    _cls_python_classes = [int, str]
    _convert_to_classes = {"int": int, "float": float, "str": str}
    _doc_data_type = "4-Byte Value"

    def __init__(self, **kwargs):
        self._formats = []
        self._detected_format = None
        self._convert_to_format = None
        super().__init__(**kwargs)

    @staticmethod
    def _check_format_str(format_, path):
        if format_ not in [
            DOT1_FORMAT,
            DOT3_FORMAT,
            INT_FORMAT,
            COLON_FORMAT,
            HEX_FORMAT,
        ]:
            raise SchemaDefinitionError(  # pylint: disable=raise-missing-from
                msg="Format unknown",
                path=path,
            )

    def _detect_data_format(self, data) -> str:
        if isinstance(data, int):
            return INT_FORMAT
        if isinstance(data, str):
            if data.count(".") == 1:
                return DOT1_FORMAT
            if data.count(".") == 3:
                return DOT3_FORMAT
            if data.count(":") == 1:
                return COLON_FORMAT
            if data.startswith("0x"):
                return HEX_FORMAT
        return None

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)
        nadap.schema.is_list(self._formats, f"{schema_path}.formats")
        for index, format_ in enumerate(self._formats):
            self._check_format_str(format_, f"{schema_path}.formats[{index}]")
        self._formats = sorted(self._formats)

        if self._convert_to_format is not None:
            nadap.schema.is_str(
                self._convert_to_format, f"{schema_path}.convert_to_format"
            )
            self._check_format_str(
                self._convert_to_format, f"{schema_path}.convert_to_format"
            )

    def _pop_options(self, definition: dict, schema_path: str):
        self._formats = definition.pop("formats", self._formats)
        self._convert_to_format = definition.pop(
            "convert_to_format", self._convert_to_format
        )
        super()._pop_options(definition, schema_path)

    def _validate_format(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> str:
        # pylint: disable=too-many-branches,too-many-statements
        self._detected_format = None
        if not self._formats:
            format_mismatch = "String does not represent a 4-byte value"
        else:
            format_mismatch = (
                "String does not represent a 4-byte value in format "
                + str_list_out(self._formats)
            )
        try:
            r_data = None
            if isinstance(data, int):
                if self._formats and INT_FORMAT not in self._formats:
                    raise ValueError(format_mismatch)
                self._detected_format = INT_FORMAT
                r_data = data
            elif data.count(".") == 1:
                # 1-dot format candidate
                if self._formats and DOT1_FORMAT not in self._formats:
                    raise ValueError(format_mismatch)
                words = data.split(".")
                try:
                    part1 = int(words[0])
                    part2 = int(words[1])
                except ValueError:
                    raise ValueError(  # pylint: disable=raise-missing-from
                        format_mismatch
                    )
                r_data = part1 * 2**16 + part2
                self._detected_format = DOT1_FORMAT
            elif data.count(".") == 3:
                # 3-dot format candidate
                if self._formats and DOT3_FORMAT not in self._formats:
                    raise ValueError(format_mismatch)
                words = data.split(".")
                try:
                    part1 = int(words[0])
                    part2 = int(words[1])
                    part3 = int(words[2])
                    part4 = int(words[3])
                except ValueError:
                    raise ValueError(  # pylint: disable=raise-missing-from
                        format_mismatch
                    )
                r_data = part1 * 2**24 + part2 * 2**16 + part3 * 2**8 + part4
                self._detected_format = DOT3_FORMAT
            elif data.count(":") == 1:
                # colon format candidate
                if self._formats and COLON_FORMAT not in self._formats:
                    raise ValueError(format_mismatch)
                words = data.split(":")
                try:
                    part1 = int(words[0])
                    part2 = int(words[1])
                except ValueError:
                    raise ValueError(  # pylint: disable=raise-missing-from
                        format_mismatch
                    )
                r_data = part1 * 2**16 + part2
                self._detected_format = COLON_FORMAT
            elif data.startswith("0x"):
                # hex format candidate
                if self._formats and HEX_FORMAT not in self._formats:
                    raise ValueError(format_mismatch)
                try:
                    r_data = int(data[2:], 16)
                except ValueError:
                    raise ValueError(  # pylint: disable=raise-missing-from
                        format_mismatch
                    )
                self._detected_format = HEX_FORMAT
            if r_data is not None:
                if not 0 <= r_data < 2**32:
                    raise ValueError("Data out of range of a 4-byte value")
                return r_data
            raise ValueError(format_mismatch)
        except ValueError as e:
            if env is None:
                raise SchemaDefinitionError(  # pylint: disable=raise-missing-from
                    str(e),
                    path,
                )
            self._create_finding_with_error(str(e), path, env)
        return data

    def _apply_data_format(self, data: "any", fmt: str = None) -> "any":
        if fmt == DOT1_FORMAT:
            return f"{int(data / 2**16)}.{data % 2**16}"
        if fmt == DOT3_FORMAT:
            return (
                f"{int(data / 2**24)}.{int((data % 2**24)/ 2**16)}."
                + f"{int((data % 2**16)/ 2**8)}.{data % 2**8}"
            )
        if fmt == COLON_FORMAT:
            return f"{int(data / 2**16)}:{data % 2**16}"
        if fmt == HEX_FORMAT:
            return hex(data)
        return data

    def _preprocess_data(self, data: any, env: "ValEnv"):
        if self._convert_to and self._convert_to in [int, float]:
            return self._convert_to(data)
        if CONVERT_DATA in env.flags:
            if self._convert_to_format is not None:
                data = self._apply_data_format(data, self._convert_to_format)
            else:
                data = self._apply_data_format(data, self._detected_format)
        else:
            data = self._apply_data_format(data, self._detected_format)
        if self._convert_to and self._convert_to == str:
            return self._convert_to(data)
        return data

    def _test_data_type(self, data: str, path: str, env: "ValEnv" = None) -> "str":
        data = super()._test_data_type(data=data, path=path, env=env)
        data = self._validate_format(data=data, path=path, env=env)
        return data

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        tf = super().restrictions
        if self._formats:
            tf.append("4-byte value:")
            tf.append(
                UnorderedTextList(["must be in format " + str_list_out(self._formats)])
            )
        return tf

    @property
    def yaml_data_type(self) -> str:
        """Get YAML data type string"""
        return self._doc_data_type

    @property
    def doc_types(self) -> list[str]:
        """Get list of data type strings"""
        return [self._doc_data_type]

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        allowed_formats = (
            "allowed_values:<br>"
            + f"{cls._markdown_indent}- {INT_FORMAT}<br>"
            + f"{cls._markdown_indent}- {DOT1_FORMAT}<br>"
            + f"{cls._markdown_indent}- {DOT3_FORMAT}<br>"
            + f"{cls._markdown_indent}- {COLON_FORMAT}<br>"
            + f"{cls._markdown_indent}- {HEX_FORMAT}"
        )
        convert_formats = (
            "allowed_values:<br>"
            + f"{cls._markdown_indent}- {DOT1_FORMAT}<br>"
            + f"{cls._markdown_indent}- {DOT3_FORMAT}<br>"
            + f"{cls._markdown_indent}- {COLON_FORMAT}<br>"
            + f"{cls._markdown_indent}- {HEX_FORMAT}"
        )
        f_desc = (
            f"- {INT_FORMAT} example: 101202<br>"
            + f"- {DOT1_FORMAT} example: 123.12<br>"
            + f"- {DOT3_FORMAT} example: 10.1.0.255<br>"
            + f"- {COLON_FORMAT} example: 123:12<br>"
            + f"- {HEX_FORMAT} example: 0x1f23a"
        )
        return super()._doc_options_md_upper_part() + [
            "| **formats** | <code>list[enum]</code> | | | |",
            f"| &nbsp;&nbsp;- < format > | <code>enum</code> | | {allowed_formats} | {f_desc} |",
            f"| **convert_to_format** | <code>enum</code> | | {convert_formats} | |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            f"format: <{INT_FORMAT}|{COLON_FORMAT}|{HEX_FORMAT}>",
            f"convert_to_format: <{COLON_FORMAT}|{HEX_FORMAT}>",
        ]


DOC_DT_CLASS = Byte4Value  # pylint: disable=invalid-name
