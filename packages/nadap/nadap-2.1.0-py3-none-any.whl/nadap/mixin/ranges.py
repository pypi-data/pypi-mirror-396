"""
Mixin for allowed and not allowed value ranges
"""

# pylint: disable=too-few-public-methods

from typing import TYPE_CHECKING

import nadap.schema
from nadap.errors import SchemaDefinitionError
from nadap.base import ValEnv
from nadap.doc import TextList, UnorderedTextList

if TYPE_CHECKING:
    from nadap.doc import TextField

DOC_FEATURES = """
- Validate against allowed and not allowed value ranges"""


class ValueRangesMixin:
    """
    Add allowed and not allowed ranges for value data
    """

    def __init__(self, **kwargs):
        self._allowed_ranges = None
        self._allowed_ranges_fmt = []
        self._not_allowed_ranges = []
        self._not_allowed_ranges_fmt = []
        super().__init__(**kwargs)

    def _validate_data(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> "any":
        """
        Check if data matches defined data type and apply preprocessing
        """
        data = super()._validate_data(data=data, path=path, env=env)
        if self._allowed_ranges:
            matches = False
            for range_ in self._allowed_ranges:
                if range_[0] <= data <= range_[1]:
                    matches = True
                    break
            if not matches:
                self._create_finding_with_error(
                    msg="Value is not within an allowed range",
                    path=path,
                    env=env,
                )
        for range_ in self._not_allowed_ranges:
            if range_[0] <= data <= range_[1]:
                self._create_finding_with_error(
                    msg="Value is within a not allowed range",
                    path=path,
                    env=env,
                )
        return data

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)

        def _validate_range(
            r_def: dict, path: str
        ) -> "tuple[tuple[any, any], tuple[str, str]]":
            nadap.schema.is_dict(r_def, path)
            start = r_def.pop("start", None)
            end = r_def.pop("end", None)
            nadap.schema.no_more_definition_options(
                definition=r_def, source="range", path=path
            )
            if start is None:
                raise SchemaDefinitionError(msg="Key 'start' missing", path=path)
            if end is None:
                raise SchemaDefinitionError(msg="Key 'end' missing", path=path)
            start_fmt = self._detect_data_format(start)
            start = self._test_data_type(data=start, path=f"{path}.start")
            end_fmt = self._detect_data_format(end)
            end = self._test_data_type(data=end, path=f"{path}.end")
            if start > end:
                raise SchemaDefinitionError(
                    msg="must be greater or equal to 'start'", path=f"{path}.end"
                )
            return ((start, end), (start_fmt, end_fmt))

        if self._allowed_ranges is not None:
            a_path = f"{schema_path}.allowed_ranges"
            nadap.schema.is_non_empty_list(self._allowed_ranges, a_path)
            a_range_def = self._allowed_ranges
            self._allowed_ranges = []
            for index, range_ in enumerate(a_range_def):
                range_values, range_formats = _validate_range(
                    range_, f"{a_path}[{index}]"
                )
                self._allowed_ranges.append(range_values)
                self._allowed_ranges_fmt.append(range_formats)

        if self._not_allowed_ranges:
            n_a_path = f"{schema_path}.not_allowed_ranges"
            nadap.schema.is_list(self._not_allowed_ranges, n_a_path)
            n_a_range_def = self._not_allowed_ranges
            self._not_allowed_ranges = []
            for index, range_ in enumerate(n_a_range_def):
                range_values, range_formats = _validate_range(
                    range_, f"{n_a_path}[{index}]"
                )
                self._not_allowed_ranges.append(range_values)
                self._not_allowed_ranges_fmt.append(range_formats)

    def _pop_options(self, definition: dict, schema_path: str):
        self._allowed_ranges = definition.pop("allowed_ranges", self._allowed_ranges)
        self._not_allowed_ranges = definition.pop(
            "not_allowed_ranges", self._not_allowed_ranges
        )
        super()._pop_options(definition=definition, schema_path=schema_path)

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        tf = super().restrictions
        if self._allowed_ranges is not None:
            tf.append("Allowed value ranges:")
            _restrictions = UnorderedTextList()
            for index, range_ in enumerate(self._allowed_ranges):
                _restrictions.append(
                    TextList(
                        [
                            "start: "
                            + str(
                                self._apply_data_format(
                                    range_[0], self._allowed_ranges_fmt[index][0]
                                )
                            ),
                            "end: "
                            + str(
                                self._apply_data_format(
                                    range_[1], self._allowed_ranges_fmt[index][1]
                                )
                            ),
                        ]
                    )
                )
            tf.append(_restrictions)
        if self._not_allowed_ranges:
            tf.append("Not allowed value ranges:")
            _restrictions = UnorderedTextList()
            for index, range_ in enumerate(self._not_allowed_ranges):
                _restrictions.append(
                    TextList(
                        [
                            "start: "
                            + str(
                                self._apply_data_format(
                                    range_[0], self._not_allowed_ranges_fmt[index][0]
                                )
                            ),
                            "end: "
                            + str(
                                self._apply_data_format(
                                    range_[1], self._not_allowed_ranges_fmt[index][1]
                                )
                            ),
                        ]
                    )
                )
            tf.append(_restrictions)
        return tf

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        data_types = (
            "<code>"
            + "&#124;".join(sorted([x.__name__ for x in cls._cls_python_classes]))
            + "</code>"
        )
        return super()._doc_options_md_upper_part() + [
            "| **allowed_ranges** | <code>list[dict]</code> | | min length: 1 | "
            + "Value must be within defined ranges |",
            f"| {cls._markdown_indent}- **start** | {data_types} | | required |",
            f"| {cls._markdown_indent * 2}**end** | {data_types} | | required |",
            "| **not_allowed_ranges** | <code>list[dict]</code> | | "
            + "| Value mustn't be within defined ranges |",
            f"| {cls._markdown_indent}- **start** | {data_types} | | required |",
            f"| {cls._markdown_indent * 2}**end** | {data_types} | | required |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        data_types = "|".join(sorted([x.__name__ for x in cls._cls_python_classes]))
        return super()._doc_options_yaml_upper_part() + [
            "allowed_ranges:",
            f" - start: <{data_types}>",
            f"   end: <{data_types}>",
            "not_allowed_ranges:",
            f" - start: <{data_types}>",
            f"   end: <{data_types}>",
        ]
