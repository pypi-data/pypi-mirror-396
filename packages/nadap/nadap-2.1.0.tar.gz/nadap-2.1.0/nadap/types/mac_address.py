"""
MAC address data type class
"""

# pylint: disable=too-few-public-methods

from typing import TYPE_CHECKING
import re

import nadap.results
import nadap.types.base
import nadap.mixin.ranges
import nadap.mixin.allowed_value
import nadap.mixin.not_allowed_value
import nadap.schema
from nadap.base import ValEnv, CONVERT_DATA, str_list_out
from nadap.errors import SchemaDefinitionError, DataValidationError
from nadap.doc import UnorderedTextList

if TYPE_CHECKING:
    from nadap.doc import TextField


DOC_DT_NAME = "MAC Adress"
DOC_DT_DESCRIPTION = """
A **mac_address** data type tests data for being an instance of
python's built-in class `str` and if it represents a MAC address (EUI-48).
"""
DOC_DT_FEATURES = """
- Validate MAC notation
- Validate MAC format
- Supports MAC format conversion
- Validate MAC specific attributes
- Validate against allowed and not allowed MAC addresses
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = r"""
type: mac_address
description: "Example mac_address definition"
default_value: "00:00:02:aa:bb:cc"

notation: canonical
formats:
  - EUI_48
  - dot-separated
uaa: true
group: false
convert_notation: bit-reversed
convert_to_format: colon-separated

not_allowed_values:
  - 04-01-01-ff-ff-ff

reference: ref_key
"""

CANONICAL = "canonical"
BIT_REVERSED = "bit-reversed"

EUI_48_FORMAT = "EUI-48"  # aa-bb-cc-dd-ee-ff
COLON_FORMAT = "colon-separated"  # aa:bb:cc:dd:ee:ff
DOT_FORMAT = "dot-separated"  # aabb.ccdd.eeff
HEX12_FORMAT = "HEX-12"  # aabbccddeeff


class MacAddress(
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.types.base.BaseType,
):
    """
    MAC address datatype class
    """

    data_type_name = "mac_address"
    _cls_python_classes = [str]
    _convert_to_classes = {}
    _doc_data_type = "MAC address"

    def __init__(self, **kwargs):
        self._notation = CANONICAL
        self._formats = []
        self._detected_format = None
        self._uaa = None
        self._group = None
        self._convert_notation = None
        self._convert_to_format = None
        super().__init__(**kwargs)

    @staticmethod
    def _check_format_str(format_, path):
        if format_ not in [
            EUI_48_FORMAT,
            COLON_FORMAT,
            DOT_FORMAT,
            HEX12_FORMAT,
        ]:
            raise SchemaDefinitionError(  # pylint: disable=raise-missing-from
                msg="Format unknown",
                path=path,
            )

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)

        if self._notation not in [CANONICAL, BIT_REVERSED]:
            raise SchemaDefinitionError(
                msg="Notation unknown",
                path=f"{schema_path}.notation",
            )
        nadap.schema.is_list(self._formats, f"{schema_path}.formats")
        for index, format_ in enumerate(self._formats):
            self._check_format_str(format_, f"{schema_path}.formats[{index}]")
        self._formats = sorted(self._formats)

        if self._convert_to_format is not None:
            self._check_format_str(
                self._convert_to_format, f"{schema_path}.convert_to_format"
            )

    def _pop_options(self, definition: dict, schema_path: str):
        self._notation = definition.pop("notation", self._notation)
        if "format" in definition:
            if "formats" in definition:
                raise SchemaDefinitionError(
                    msg="excludes key 'formats'",
                    path=f"{schema_path}.format",
                )
            _format = definition.pop("format")
            nadap.schema.is_str(_format, f"{schema_path}.format")
            self._check_format_str(_format, f"{schema_path}.format")
            self._formats = [_format]
        else:
            self._formats = definition.pop("formats", self._formats)
        self._uaa = definition.pop("uaa", self._uaa)
        self._group = definition.pop("group", self._group)
        self._convert_notation = definition.pop(
            "convert_notation", self._convert_notation
        )
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
        # pylint: disable=too-many-branches
        data = self._int2hex8(data)
        msg = ""
        messages = []
        if self._uaa is not None:
            if self._notation == CANONICAL:
                if self._uaa and data[1] in "2367abef":
                    msg = "MAC address is locally administered"
                    messages.append(msg)
                if not self._uaa and data[1] in "014589cd":
                    msg = "MAC address is universally administered"
                    messages.append(msg)
            else:  # bit-reversed (i.e. Token Ring)
                if self._uaa and data[0] in "4567cdef":
                    msg = "MAC address is locally administered"
                    messages.append(msg)
                if not self._uaa and data[0] in "012389ab":
                    msg = "MAC address is universally administered"
                    messages.append(msg)
        if self._group is not None:
            if self._notation == CANONICAL:
                if self._group and data[1] in "02468ace":
                    msg = "MAC address is a unicast address"
                    messages.append(msg)
                if not self._group and data[1] in "13579bdf":
                    msg = "MAC address is a group address"
                    messages.append(msg)
            else:  # bit-reversed (i.e. Token Ring)
                if self._group and data[0] in "01234567":
                    msg = "MAC address is a unicast address"
                    messages.append(msg)
                if not self._group and data[0] in "89abcdef":
                    msg = "MAC address is a group address"
                    messages.append(msg)
        if msg:
            if env is None:
                raise SchemaDefinitionError(
                    msg,
                    path,
                )
            for m in messages:
                env.findings.append(
                    nadap.results.ValidationFinding(
                        message=m,
                        path=path,
                    )
                )
            raise DataValidationError()

    def _detect_data_format(self, data) -> str:
        if "-" in data:
            return EUI_48_FORMAT
        if ":" in data:
            return COLON_FORMAT
        if "." in data:
            return DOT_FORMAT
        return HEX12_FORMAT

    def _apply_data_format(self, data: "any", fmt: str = None) -> "any":
        data = self._int2hex8(data)
        if fmt == EUI_48_FORMAT:
            return f"{data[0:2]}-{data[2:4]}-{data[4:6]}-{data[6:8]}-{data[8:10]}-{data[10:12]}"
        if fmt == COLON_FORMAT:
            return f"{data[0:2]}:{data[2:4]}:{data[4:6]}:{data[6:8]}:{data[8:10]}:{data[10:12]}"
        if fmt == DOT_FORMAT:
            return f"{data[0:4]}.{data[4:8]}.{data[8:12]}"
        return data

    def _validate_format(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> str:
        # pylint: disable=too-many-branches
        if not self._formats:
            format_mismatch = "String does not represent a MAC address"
        else:
            format_mismatch = (
                "String does not represent a MAC address in format "
                + str_list_out(self._formats)
            )
        ret_value = None
        try:
            if "-" in data:
                # EUI-48 candidate
                if self._formats and EUI_48_FORMAT not in self._formats:
                    raise ValueError(format_mismatch)
                if not re.fullmatch("([0-9a-f]{2}-){5}[0-9a-f]{2}", data):
                    raise ValueError(format_mismatch)
                self._detected_format = EUI_48_FORMAT
                ret_value = data.replace("-", "")
            elif ":" in data:
                # colon format candidate
                if self._formats and COLON_FORMAT not in self._formats:
                    raise ValueError(format_mismatch)
                if not re.fullmatch(r"([0-9a-f]{2}\:){5}[0-9a-f]{2}", data):
                    raise ValueError(format_mismatch)
                self._detected_format = COLON_FORMAT
                ret_value = data.replace(":", "").lower()
            elif "." in data:
                # dotted format candidate
                if self._formats and DOT_FORMAT not in self._formats:
                    raise ValueError(format_mismatch)
                if not re.fullmatch(r"([0-9a-f]{4}\.){2}[0-9a-f]{4}", data):
                    raise ValueError(format_mismatch)
                self._detected_format = DOT_FORMAT
                ret_value = data.replace(".", "").lower()
            elif not re.fullmatch("[0-9a-f]{12}", data):
                raise ValueError(format_mismatch)
            else:
                self._detected_format = HEX12_FORMAT
                ret_value = data
        except ValueError as e:
            if env is None:
                raise SchemaDefinitionError(  # pylint: disable=raise-missing-from
                    str(e),
                    path,
                )
            self._create_finding_with_error(str(e), path, env)
        return self._hex2int(ret_value)

    @staticmethod
    def _hex2int(h: str) -> int:
        return int(h, 16)

    @staticmethod
    def _int2hex8(i: int) -> str:
        h = hex(i)
        return (14 - len(h)) * "0" + h[2:]

    @classmethod
    def _apply_convert_notation(cls, data: str) -> str:
        def _translate_hex(h):
            bit_str = bin(int(h, 16))[2:]
            bit_str = (4 - len(bit_str)) * "0" + bit_str
            reversed_bits = bit_str[::-1]
            hex_ = hex(int(reversed_bits, 2))
            return hex_[-1]

        ret_mac = ""
        for byte in [
            data[0:2],
            data[2:4],
            data[4:6],
            data[6:8],
            data[8:10],
            data[10:12],
        ]:
            ret_mac += _translate_hex(byte[1]) + _translate_hex(byte[0])
        return ret_mac

    def _preprocess_data(self, data: any, env: "ValEnv"):
        if CONVERT_DATA in env.flags:
            if self._convert_notation is not None:
                data = self._int2hex8(data)
                data = self._apply_convert_notation(data)
                data = self._hex2int(data)
            if self._convert_to_format is not None:
                data = self._apply_data_format(data, self._convert_to_format)
            else:
                data = self._apply_data_format(data, self._detected_format)
        else:
            data = self._apply_data_format(data, self._detected_format)
        return data

    def _test_data_type(self, data: str, path: str, env: "ValEnv" = None) -> "str":
        data = super()._test_data_type(data=data, path=path, env=env).lower()
        data = self._validate_format(data=data, path=path, env=env)
        self._validate_scope(data=data, path=path, env=env)
        return data

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        tf = super().restrictions
        mac_restrictions = UnorderedTextList()
        if self._formats:
            mac_restrictions.append(
                ("must be in format " + str_list_out(self._formats))
            )
        if self._uaa is not None or self._group is not None:
            if self._uaa is not None:
                mac_restrictions.append(
                    f"must be {'universally' if self._uaa else 'locally'} administered"
                )
            if self._group is not None:
                mac_restrictions.append(
                    f"must be a {'group' if self._group else 'unicast'} address"
                )
            mac_restrictions.append(f"treated as in {self._notation} notation")

        if mac_restrictions:
            tf.append("MAC address:")
            tf.append(mac_restrictions)
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
        allowed_notations = (
            f"allowed_values:<br>{cls._markdown_indent}- "
            + f"{CANONICAL}<br>{cls._markdown_indent}- {BIT_REVERSED}"
        )
        allowed_formats = (
            f"allowed_values:<br>{cls._markdown_indent}- "
            + f"{EUI_48_FORMAT}<br>{cls._markdown_indent}- {COLON_FORMAT}"
            + f"<br>{cls._markdown_indent}- {DOT_FORMAT}<br>{cls._markdown_indent}- "
            + f"{HEX12_FORMAT}"
        )
        f_desc = (
            f"- {EUI_48_FORMAT} example: 01-01-01-aa-bb-cc<br>"
            + f"- {COLON_FORMAT} example: 01:01:01:aa:bb:cc<br>"
            + f"- {DOT_FORMAT} example: 0101.01aa.bbcc<br>"
            + f"- {HEX12_FORMAT} example: 010101aabbcc"
        )
        return super()._doc_options_md_upper_part() + [
            f"| **notation** | <code>enum</code> | {CANONICAL} | {allowed_notations} | "
            + "Canonical is used in i.e. Ethernet<br>Bit-reversed is used i.e. in Token Ring|",
            f"| **format** | <code>enum</code> | | {allowed_formats} | {f_desc} |",
            "| **formats** | <code>list[enum]</code> | | excludes: format | |",
            f"| &nbsp;&nbsp;- < format > | <code>enum</code> | | {allowed_formats} | {f_desc} |",
            "| **uaa** | <code>bool</code> | | | "
            + "MAC address must be universally (true) or locally (false) administered |",
            "| **group** | <code>bool</code> | | | "
            + "MAC address must be a group (true) or a unicast (false) address |",
            "| **convert_notation** | <code>bool</code> | <code>False</code> | | |",
            f"| **convert_to_format** | <code>enum</code> | | {allowed_formats} | |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            f"notation: <{CANONICAL}|{BIT_REVERSED}>",
            f"format: <{EUI_48_FORMAT}|{COLON_FORMAT}|{DOT_FORMAT}|{HEX12_FORMAT}>",
            "formats:",
            f"  - <{EUI_48_FORMAT}|{COLON_FORMAT}|{DOT_FORMAT}|{HEX12_FORMAT}>",
            "uaa: <true|false>",
            "group: <true|false>",
            "convert_notation: <true|false>",
            f"convert_to_format: <{EUI_48_FORMAT}|{COLON_FORMAT}|{DOT_FORMAT}|{HEX12_FORMAT}>",
        ]


DOC_DT_CLASS = MacAddress  # pylint: disable=invalid-name
