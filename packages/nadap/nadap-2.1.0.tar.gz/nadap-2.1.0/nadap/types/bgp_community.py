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


DOC_DT_NAME = "BGP Community"
DOC_DT_DESCRIPTION = """
A **bgp_community** data type tests data for being an instance of
python's built-in class `str` or `int` and if it represents a BGP standard community (4 bytes).
"""
DOC_DT_FEATURES = """
- Validate BGP Community format
- Supports BGP Community format conversion
- Validate BGP Community specific attributes
- Validate against allowed and not allowed BGP Communities
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = r"""
type: bgp_community
description: "Example bgp_community definition"
default_value: GRACEFUL_SHUTDOWN

format: colon-separated
well_known: false
public: false
convert_to_format: integer

not_allowed_values:
  - NO_EXPORT
  - 7001
  - 0:7002
  - 0xA0001

not_allowed_ranges:
  - start: 65498:0
    end: 65498:65535

reference: ref_key
"""


NEW_FORMAT = "new-format"  # "65000:100"
INT_FORMAT = "integer"  # 11223344
HEX_FORMAT = "hex"  # FFFF0001 or ffff0001
WELL_KNOWN_MAP = {
    # Source:
    # https://www.iana.org/assignments/bgp-well-known-communities/bgp-well-known-communities.xhtml
    "GRACEFUL_SHUTDOWN": 4294901760,
    "ACCEPT_OWN": 4294901761,
    "ROUTE_FILTER_TRANSLATED_v4": 4294901762,
    "ROUTE_FILTER_v4": 4294901763,
    "ROUTE_FILTER_TRANSLATED_v6": 4294901764,
    "ROUTE_FILTER_v6": 4294901765,
    "LLGR_STALE": 4294901766,
    "NO_LLGR": 4294901767,
    "accept-own-nexthop": 4294901768,
    "BLACKHOLE": 4294902426,
    "NO_EXPORT": 4294967041,
    "NO_ADVERTISE": 4294967042,
    "NO_EXPORT_SUBCONFED": 4294967043,
    "NOPEER": 4294967044,
}


class BgpCommunity(
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
    nadap.mixin.ranges.ValueRangesMixin,
    nadap.types.base.BaseType,
):
    """
    BGP Community datatype class
    """

    data_type_name = "bgp_community"
    _cls_python_classes = [int, str]
    _convert_to_classes = {}
    _doc_data_type = "BGP Community"

    def __init__(self, **kwargs):
        self._format = None
        self._public = None
        self._well_known = None
        self._detected_format = None
        self._was_well_known_string = None
        self._convert_to_format = None
        super().__init__(**kwargs)

    @staticmethod
    def _check_format_str(format_, path):
        if format_ not in [NEW_FORMAT, INT_FORMAT, HEX_FORMAT]:
            raise SchemaDefinitionError(  # pylint: disable=raise-missing-from
                msg="Format unknown",
                path=path,
            )

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)

        if self._format is not None:
            nadap.schema.is_str(self._format, f"{schema_path}.format")
            self._check_format_str(self._format, f"{schema_path}.format")

        if self._convert_to_format is not None:
            self._check_format_str(
                self._convert_to_format, f"{schema_path}.convert_to_format"
            )

    def _pop_options(self, definition: dict, schema_path: str):
        self._format = definition.pop("format", self._format)
        self._public = definition.pop("public", self._public)
        self._well_known = definition.pop("well_known", self._well_known)
        self._convert_to_format = definition.pop(
            "convert_to_format", self._convert_to_format
        )
        super()._pop_options(definition, schema_path)

    def _validate_source_as(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ):
        source_as = int(data / 2**16)
        msg = None
        if self._public is not None:
            if self._public:
                if 64512 <= source_as <= 65534:
                    msg = "BGP community's source AS number is within private space"
            elif 1 <= source_as < 64512:
                msg = "BGP community's source AS number is within public space"
        self._raise_exceptions(messages=msg, path=path, env=env)

    def _validate_well_known(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ):
        msg = None
        if self._well_known is None:
            return
        if self._well_known:
            if data not in WELL_KNOWN_MAP.values():
                msg = "BGP community is not a well-known community"
        elif data in WELL_KNOWN_MAP.values():
            msg = "BGP community is a well-known community"
        self._raise_exceptions(messages=msg, path=path, env=env)

    def _apply_data_format(self, data: "any", fmt: str = None) -> "any":
        if fmt == NEW_FORMAT:
            source_as = int(data / 2**16)
            operator_value = data % 2**16
            return f"{source_as}:{operator_value}"
        if fmt == HEX_FORMAT:
            return hex(data).upper().replace("0X", "0x")
        if self._was_well_known_string:
            return self._was_well_known_string
        return data

    def _detect_data_format(self, data) -> str:
        if isinstance(data, int):
            return INT_FORMAT
        if isinstance(data, str):
            if data.count(":") == 1:
                return NEW_FORMAT
            if data.startswith("0x"):
                return HEX_FORMAT
        return None

    def _validate_format(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> str:
        # pylint: disable=too-many-branches
        if isinstance(data, int):
            # BGP AS number is in asplain format.
            if self._format and self._format != INT_FORMAT:
                self._raise_exceptions(
                    f"BGP community is not in {self._format} format", path, env
                )
            self._detected_format = INT_FORMAT
            return data
        if self._format == INT_FORMAT:
            self._raise_exceptions(
                f"BGP community is not in {INT_FORMAT} format", path, env
            )

        if data.count(":") == 1:
            # BGP community is in new format.
            self._detected_format = NEW_FORMAT
            source_as, operator_value = data.split(":")
            try:
                source_as = int(source_as)
                operator_value = int(operator_value)
            except ValueError:
                self._raise_exceptions("Invalid BGP community format", path, env)
            if self._format and self._format == HEX_FORMAT:
                self._raise_exceptions(
                    f"BGP community is not in {self._format} format", path, env
                )
            return source_as * 2**16 + operator_value

        # BGP community is not in new format
        if len(data) == 0:
            self._raise_exceptions(
                "Empty string is not allowed as a BGP community", path, env
            )
        if data in WELL_KNOWN_MAP:
            self._was_well_known_string = data
            return WELL_KNOWN_MAP[data]
        self._detected_format = HEX_FORMAT
        if data.startswith("0x"):
            try:
                int_data = int(data, 16)
                return int_data
            except ValueError:
                pass
        self._raise_exceptions("String is no valid BGP community", path, env)
        return None

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
        if not 0 <= data <= 4294967295:
            self._raise_exceptions(
                "BGP community value is out of allowed range 0-4294967295", path, env
            )
        self._validate_well_known(data=data, path=path, env=env)
        self._validate_source_as(data=data, path=path, env=env)
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
            _restrictions.append(
                f"Source AS must be {'public' if self._public else 'private'}"
            )
        if self._well_known is not None:
            _restrictions.append(
                f"must{'' if self._well_known else ' not'} be a well-known BGP community"
            )
        if _restrictions:
            tf.append("BGP Community:")
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
            + f"{cls._markdown_indent}- {INT_FORMAT}<br>"
            + f"{cls._markdown_indent}- {NEW_FORMAT}<br>"
            + f"{cls._markdown_indent}- {HEX_FORMAT}"
        )
        f_desc = (
            f"- {INT_FORMAT} example: 70116<br>"
            + f"- {NEW_FORMAT} example: 1.4580<br>"
            + f"- {HEX_FORMAT} example: '0x111E4'"
        )
        return super()._doc_options_md_upper_part() + [
            f"| **format** | <code>enum</code> | | {allowed_formats} | {f_desc} |",
            "| **public** | <code>bool</code> | | | "
            + "BGP Community's source AS must be a public (true) or a private (false) AS number |",
            "| **well_known** | <code>bool</code> | | | "
            + "BGP Community must (true) or must not (false) be well-known |",
            f"| **convert_to_format** | <code>enum</code> | | {allowed_formats} | |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            f"format: <{INT_FORMAT}|{NEW_FORMAT}|{HEX_FORMAT}>",
            "public: <true|false>",
            "well_known: <true|false>",
            f"convert_to_format: <{INT_FORMAT}|{NEW_FORMAT}|{HEX_FORMAT}>",
        ]


DOC_DT_CLASS = BgpCommunity  # pylint: disable=invalid-name
