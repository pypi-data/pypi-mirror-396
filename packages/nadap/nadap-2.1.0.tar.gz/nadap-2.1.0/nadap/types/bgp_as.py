"""
MAC address data type class
"""

# pylint: disable=too-few-public-methods

from typing import TYPE_CHECKING

import nadap.results
import nadap.types.base
import nadap.mixin.ranges
import nadap.mixin.allowed_value
import nadap.mixin.not_allowed_value
import nadap.schema
from nadap.base import ValEnv, CONVERT_DATA
from nadap.errors import SchemaDefinitionError
from nadap.doc import UnorderedTextList

if TYPE_CHECKING:
    from nadap.doc import TextField


DOC_DT_NAME = "BGP AS Number"
DOC_DT_DESCRIPTION = """
A **bgp_as** data type tests data for being an instance of
python's built-in class `str` or `int` and if it represents a BGP AS number.
"""
DOC_DT_FEATURES = """
- Validate BGP AS format
- Supports BGP AS format conversion
- Validate BGP AS specific attributes
- Validate against allowed and not allowed BGP AS numbers
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = r"""
type: bgp_as
description: "Example bgp_as definition"
default_value: 100111

format: asplain
public: false
4_byte: true
convert_to_format: asdot

not_allowed_values:
  - 100222

not_allowed_ranges:
  - start: 123000
    end: 125000

reference: ref_key
"""


ASDOT_FORMAT = "asdot"  # "65000.100"
ASPLAIN_FORMAT = "asplain"  # 11223344
STRING_FORMAT = "string"  # "11223344"
ASDOT_UNCLEAR = "asdot_unclear"


class BgpAs(
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.types.base.BaseType,
):
    """
    BGP AS datatype class
    """

    data_type_name = "bgp_as"
    _cls_python_classes = [int, str]
    _convert_to_classes = {}
    _doc_data_type = "BGP AS number"

    def __init__(self, **kwargs):
        self._format = None
        self._detected_format = None
        self._public = None
        self._convert_to_format = None
        super().__init__(**kwargs)

    @staticmethod
    def _check_format_str(format_, path):
        if format_ not in [ASDOT_FORMAT, ASPLAIN_FORMAT, STRING_FORMAT]:
            raise SchemaDefinitionError(  # pylint: disable=raise-missing-from
                msg="Format unknown",
                path=path,
            )

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)

        if self._format is not None and self._format not in [
            ASDOT_FORMAT,
            ASPLAIN_FORMAT,
            STRING_FORMAT,
        ]:
            raise SchemaDefinitionError(
                msg="Notation unknown",
                path=f"{schema_path}.notation",
            )

        if self._convert_to_format is not None:
            self._check_format_str(
                self._convert_to_format, f"{schema_path}.convert_to_format"
            )

    def _pop_options(self, definition: dict, schema_path: str):
        if "format" in definition:
            _format = definition.pop("format")
            nadap.schema.is_str(_format, f"{schema_path}.format")
            self._check_format_str(_format, f"{schema_path}.format")
            self._format = _format
        self._public = definition.pop("public", self._public)
        self._convert_to_format = definition.pop(
            "convert_to_format", self._convert_to_format
        )
        super()._pop_options(definition, schema_path)

    def _validate_scope(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ):
        msg = None
        if self._public is not None:
            if self._public:
                if 64512 <= data <= 65534 or 4200000000 <= data <= 4294967294:
                    msg = "BGP AS number is for private use"
            elif data < 64512 or (
                data > 65534 and (data < 4200000000 or data > 4294967294)
            ):
                msg = "BGP AS number is for public use"
        self._raise_exceptions(messages=msg, path=path, env=env)

    def _detect_data_format(self, data) -> str:
        if isinstance(data, int):
            return ASPLAIN_FORMAT
        if isinstance(data, str):
            if "." in data:
                return ASDOT_FORMAT
            try:
                if int(data) <= 65535:
                    return ASDOT_UNCLEAR
            except ValueError:
                pass
        return STRING_FORMAT

    def _apply_data_format(self, data: "any", fmt: str = None) -> "any":
        if fmt == ASDOT_FORMAT:
            part1 = int(data / 2**16)
            if part1 == 0:
                return str(data)
            part2 = data - (part1 * 2**16)
            return f"{part1}.{part2}"
        if fmt == STRING_FORMAT:
            return str(data)
        return data

    def _validate_format(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> str:
        # pylint: disable=too-many-branches
        if isinstance(data, int):
            # BGP AS number is in asplain format.
            int_data = data
            if self._format and self._format != ASPLAIN_FORMAT:
                self._raise_exceptions(
                    f"BGP AS number is not in {self._format} format", path, env
                )
            self._detected_format = ASPLAIN_FORMAT
        else:
            if self._format == ASPLAIN_FORMAT:
                self._raise_exceptions(
                    "BGP AS number is not in asplain format", path, env
                )

            if data.count(".") == 1:
                # BGP AS number is in asdot format.
                part1, part2 = data.split(".")
                try:
                    part1 = int(part1)
                    part2 = int(part2)
                except ValueError:
                    self._raise_exceptions("Invalid BGP AS format", path, env)
                int_data = part1 * 2**16 + part2
                if self._format and self._format != ASDOT_FORMAT:
                    self._raise_exceptions(
                        f"BGP AS number is not in {self._format} format", path, env
                    )
                self._detected_format = ASDOT_FORMAT
            else:
                # BGP AS number is a string
                if len(data) == 0:
                    self._raise_exceptions(
                        "Empty string is not allowed as a BGP AS number", path, env
                    )
                elif len(data) > 1 and data[0] == "0":
                    self._raise_exceptions(
                        "No leading zeros allowed in a BGP AS number", path, env
                    )
                try:
                    int_data = int(data)
                except ValueError:
                    self._raise_exceptions("Invalid BGP AS format", path, env)
                self._detected_format = STRING_FORMAT
                if int_data > 65535 and self._format and self._format == ASDOT_FORMAT:
                    self._raise_exceptions(
                        "BGP AS number is not in asdot format", path, env
                    )
        if not 0 <= int_data <= 4294967295:
            self._raise_exceptions(
                "BGP AS number is out of defined range 0-4294967295", path, env
            )
        return int_data

    def _preprocess_data(self, data: any, env: "ValEnv"):
        if CONVERT_DATA in env.flags:
            if self._convert_to_format is not None:
                data = self._apply_data_format(data, self._convert_to_format)
            else:
                data = self._apply_data_format(data, self._detected_format)
        else:
            data = self._apply_data_format(data, self._detected_format)
        return data

    def _test_data_type(self, data: str, path: str, env: "ValEnv" = None) -> "str":
        data = super()._test_data_type(data=data, path=path, env=env)
        data = self._validate_format(data=data, path=path, env=env)
        self._validate_scope(data=data, path=path, env=env)
        return data

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        tf = super().restrictions
        _restrictions = UnorderedTextList()
        if self._format:
            _restrictions.append((f"must be in format '{self._format}'"))
        if self._public is not None:
            _restrictions.append(f"must be {'public' if self._public else 'private'}")

        if _restrictions:
            tf.append("BGP AS number:")
            tf.append(_restrictions)
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
            + f"{cls._markdown_indent}- {ASPLAIN_FORMAT}<br>"
            + f"{cls._markdown_indent}- {ASDOT_FORMAT}<br>"
            + f"{cls._markdown_indent}- {STRING_FORMAT}"
        )
        f_desc = (
            f"- {ASPLAIN_FORMAT} example: 100100<br>"
            + f"- {ASDOT_FORMAT} example: 100.100<br>"
            + f"- {STRING_FORMAT} example: '100100'"
        )
        return super()._doc_options_md_upper_part() + [
            f"| **format** | <code>enum</code> | | {allowed_formats} | {f_desc} |",
            "| **public** | <code>bool</code> | | | "
            + "BGP AS must be a public (true) or private (false) number |",
            f"| **convert_to_format** | <code>enum</code> | | {allowed_formats} | |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            f"format: <{ASPLAIN_FORMAT}|{ASDOT_FORMAT}|{STRING_FORMAT}>",
            "public: <true|false>",
            f"convert_to_format: <{ASPLAIN_FORMAT}|{ASDOT_FORMAT}|{STRING_FORMAT}>",
        ]


DOC_DT_CLASS = BgpAs  # pylint: disable=invalid-name
