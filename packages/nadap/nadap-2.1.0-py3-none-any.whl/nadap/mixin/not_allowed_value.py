"""
NotAllowedValueMixin
"""

# pylint: disable=too-few-public-methods

from typing import TYPE_CHECKING

import nadap.schema
from nadap.base import ValEnv, number_to_str_number
from nadap.doc import UnorderedTextList

if TYPE_CHECKING:
    from nadap.doc import TextField


class NotAllowedValueMixin:
    """
    Add not allowed value tests for data
    """

    def __init__(self, **kwargs):
        self.not_allowed_values = None
        self._not_allowed_value_formats = []
        super().__init__(**kwargs)

    def _validate_data(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> "any":
        """
        Check if data doesn't match not allowed values
        """
        data = super()._validate_data(data=data, path=path, env=env)
        if self.not_allowed_values is not None and data in self.not_allowed_values:
            self._create_finding_with_error(
                msg="Data is a not allowed value",
                path=path,
                env=env,
            )
        return data

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)
        if self.not_allowed_values is not None:
            nadap.schema.is_list(
                self.not_allowed_values, f"{schema_path}.not_allowed_values"
            )
            values = []
            for index, v in enumerate(self.not_allowed_values):
                self._not_allowed_value_formats.append(self._detect_data_format(v))
                values.append(
                    self._test_data_type(
                        data=v, path=f"{schema_path}.not_allowed_values[{index}]"
                    )
                )
            self.not_allowed_values = values

    def _pop_options(self, definition: dict, schema_path: str):
        self.not_allowed_values = definition.pop(
            "not_allowed_values", self.not_allowed_values
        )
        super()._pop_options(definition=definition, schema_path=schema_path)

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        tf = super().restrictions
        if self.not_allowed_values:
            tf.append("not allowed values:")
            out_values = []
            for index, v in enumerate(self.not_allowed_values):
                out_values.append(
                    self._apply_data_format(v, self._not_allowed_value_formats[index])
                )
            tf.append(
                UnorderedTextList([str(number_to_str_number(x)) for x in out_values])
            )
        return tf

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **not_allowed_values** | <code>list</code> | | | "
            + " Data mustn't match all of these values |",
            f"| &nbsp;&nbsp;- < value > | {cls._doc_md_type()}"
            + " | | Must match data type's type(s) | |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "not_allowed_values:",
            f"  - <{cls._doc_yaml_type()}>",
        ]
