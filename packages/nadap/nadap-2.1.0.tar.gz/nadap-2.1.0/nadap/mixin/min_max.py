"""
Mixins for minimal and maximal value/length
"""

# pylint: disable=too-few-public-methods

from typing import TYPE_CHECKING

from nadap.errors import SchemaDefinitionError
from nadap.base import ValEnv

if TYPE_CHECKING:
    from nadap.doc import TextField


class _PopOptionsMixin:
    """
    Mixin for popping the options
    """

    def __init__(self, **kwargs):
        if not hasattr(self, "_minimum_default"):
            self._minimum_default = None
        self.minimum = None
        self._min_fmt = None
        if not hasattr(self, "_maximum_default"):
            self._maximum_default = None
        self.maximum = None
        self._max_fmt = None
        super().__init__(**kwargs)

    def _pop_options(self, definition: dict, schema_path: str):
        self.maximum = definition.pop("maximum", self._maximum_default)
        self.minimum = definition.pop("minimum", self._minimum_default)
        super()._pop_options(definition=definition, schema_path=schema_path)


class MinMaxValueMixin(_PopOptionsMixin):
    """
    Add min/max tests for value data
    """

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
        if self.minimum is not None and data < self.minimum:
            self._create_finding_with_error(
                msg=f"Value is lower than defined minimum of {self.minimum}",
                path=path,
                env=env,
            )
        if self.maximum is not None and data > self.maximum:
            self._create_finding_with_error(
                msg=f"Value is greater than defined maximum of {self.maximum}",
                path=path,
                env=env,
            )
        return data

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)
        if self.maximum is not None:
            self._max_fmt = self._detect_data_format(self.maximum)
            self.maximum = self._test_data_type(
                data=self.maximum, path=f"{schema_path}.maximum"
            )
        if self.minimum is not None:
            self._min_fmt = self._detect_data_format(self.minimum)
            self.minimum = self._test_data_type(
                data=self.minimum, path=f"{schema_path}.minimum"
            )
        if (
            self.minimum is not None
            and self.maximum is not None
            and self.minimum > self.maximum
        ):
            raise SchemaDefinitionError(
                "maximum must be greater than or equal to minimum",
                schema_path,
            )

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        tf = super().restrictions
        if self.minimum is not None:
            tf.append(f"min: {self._apply_data_format(self.minimum, self._min_fmt)}")
        if self.maximum is not None:
            tf.append(f"max: {self._apply_data_format(self.maximum, self._max_fmt)}")
        return tf

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **minimum** | <code>"
            + "&#124;".join(sorted([x.__name__ for x in cls._cls_python_classes]))
            + "</code> | | |  Value must be greater or equal |",
            "| **maximum** | <code>"
            + "&#124;".join(sorted([x.__name__ for x in cls._cls_python_classes]))
            + "</code> | | >= 'minimum' |  Value must be lower or equal |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            f"maximum: <{'|'.join(sorted([x.__name__ for x in cls._cls_python_classes]))}>",
            f"minimum: <{'|'.join(sorted([x.__name__ for x in cls._cls_python_classes]))}>",
        ]


class MinMaxLengthMixin(_PopOptionsMixin):
    """
    Add min/max tests for value data length
    """

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
        if self.minimum is not None and len(data) < self.minimum:
            self._create_finding_with_error(
                msg=f"Length is lower than defined minimum of {self.minimum}",
                path=path,
                env=env,
            )
        if self.maximum is not None and len(data) > self.maximum:
            self._create_finding_with_error(
                msg=f"Length is greater than defined maximum of {self.maximum}",
                path=path,
                env=env,
            )
        return data

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)
        if self.maximum is not None:
            if not isinstance(self.maximum, int):
                raise SchemaDefinitionError(
                    "Data is not an instance of 'int'",
                    f"{schema_path}.maximum",
                )
            if self.maximum < 0:
                raise SchemaDefinitionError(
                    "Must be >= 0",
                    f"{schema_path}.maximum",
                )
        if self.minimum is not None:
            if not isinstance(self.minimum, int):
                raise SchemaDefinitionError(
                    "Data is not an instance of 'int'",
                    f"{schema_path}.minimum",
                )
            if self.minimum < 0:
                raise SchemaDefinitionError(
                    "Must be >= 0",
                    f"{schema_path}.minimum",
                )
        if (
            self.minimum is not None
            and self.maximum is not None
            and self.minimum > self.maximum
        ):
            raise SchemaDefinitionError(
                "maximum must be greater than or equal to minimum",
                schema_path,
            )

    @property
    def restrictions(self) -> "list[str]":
        """
        Get all restrictions for valid data
        """
        ret_list = super().restrictions
        if self.minimum is not None:
            ret_list.append(f"min length: {self.minimum}")
        if self.maximum is not None:
            ret_list.append(f"max length: {self.maximum}")
        return ret_list

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **minimum** | <code>int</code> | | min: 1 "
            + "| Data's length must be greater or equal |",
            "| **maximum** | <code>int</code> | | min: 1<br>>= 'minimum' | "
            + "Data's length must be lower or equal |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "maximum: <int>",
            "minimum: <int>",
        ]
