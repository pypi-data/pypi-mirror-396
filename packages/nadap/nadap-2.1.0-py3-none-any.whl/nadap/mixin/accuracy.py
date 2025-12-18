"""
Accuracy Mixin
"""

# pylint: disable=too-few-public-methods

from typing import TYPE_CHECKING

import nadap.schema
from nadap.base import ValEnv
from nadap.errors import SchemaDefinitionError, DataValidationError

if TYPE_CHECKING:
    from nadap.doc import TextField


class AccuracyMixin:
    """
    Add options for maximum_decimals
    """

    def __init__(self, **kwargs):
        self._maximum_decimals = None
        self._round_to = None
        super().__init__(**kwargs)

    def _pop_options(self, definition: dict, schema_path: str):
        self._maximum_decimals = definition.pop("maximum_decimals", None)
        self._round_to = definition.pop("round_to_decimals", None)
        super()._pop_options(definition=definition, schema_path=schema_path)

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)
        if self._maximum_decimals is not None:
            _path = f"{schema_path}.maximum_decimals"
            nadap.schema.is_int(self._maximum_decimals, _path)
            if not 0 <= self._maximum_decimals <= 17:
                raise SchemaDefinitionError("Must be >= 0 and <= 17", _path)
        if self._round_to is not None:
            _path = f"{schema_path}.round_to_decimals"
            nadap.schema.is_int(self._round_to, _path)
            if not 0 <= self._round_to <= 17:
                raise SchemaDefinitionError("Must be >= 0 and <= 17", _path)

    def _validate_data(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> "any":
        data = super()._validate_data(data=data, path=path, env=env)
        if self._maximum_decimals is not None and data != round(
            data, self._maximum_decimals
        ):
            env.findings.append(
                nadap.results.ValidationFinding(
                    "Float value has too many decimals",
                    path,
                )
            )
            raise DataValidationError()
        return data

    def _convert_data(self, data: any) -> any:
        if self._round_to is not None:
            data = round(data, self._round_to)
        return super()._convert_data(data)

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        tf = super().restrictions
        if self._maximum_decimals is not None:
            tf.append(f"max allowed decimals: {self._maximum_decimals}")
        return tf

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **maximum_decimals** | <code>int</code> | | Must be >= 0 and <= 17 | "
            + "Value's accuracy must be lower or equal |",
            "| **round_to_decimals** | <code>int</code> | | Must be >= 0 and <= 17 | "
            + "Convert value to this accuracy |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "maximum_decimals: <int>",
            "round_to_decimals: <int>",
        ]
