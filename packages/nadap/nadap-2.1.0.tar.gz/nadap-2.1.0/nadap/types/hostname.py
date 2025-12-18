"""
Hostname data type class
"""

# pylint: disable=too-few-public-methods

from typing import TYPE_CHECKING

import nadap.results
import nadap.types.base
import nadap.mixin.min_max
import nadap.mixin.replace_empty_to
import nadap.schema
from nadap.base import ValEnv, UNDEFINED
from nadap.errors import DataValidationError, SchemaDefinitionError
from nadap.doc import UnorderedTextList

if TYPE_CHECKING:
    from nadap.doc import TextField

DOC_DT_NAME = "Hostname"
DOC_DT_DESCRIPTION = """
A **hostname** data type tests data for being an instance of
python's built-in class `str` and if it represents a hostname/FQDN.
"""
DOC_DT_FEATURES = """
- Validate conformity to IETF RFC 1123
- Validate string length
- Validate label count
- Validate against allowed and not allowed regex patterns
  (always full matching the string)
- Supports **Referencing Feature**
- Data type conversion is not supported
"""
DOC_DT_YAML_EXAMPLE = r"""
type: hostname
description: "Example hostname definition"
default_value: "my-host"

minimum: 3
maximum: 15
minimum_labels: 3
maximum_labels: 8

not_allowed_values:
  - nadap-.*
relax_length: false

reference: ref_key
"""


class Hostname(
    nadap.mixin.replace_empty_to.ReplaceEmptyToMixin,
    nadap.mixin.min_max.MinMaxLengthMixin,
    nadap.types.base.BaseType,
):
    """
    Hostname datatype class
    """

    data_type_name = "hostname"
    _cls_python_classes = [str]
    _convert_to_classes = {}
    _support_replace_empty_to = True
    _doc_data_type = "str"

    def __init__(self, **kwargs):
        self.allowed_values = None
        self.not_allowed_values = []
        self._relax_length = True
        self._min_labels = None
        self._max_labels = None
        super().__init__(**kwargs)

    def _validate_allowed_values_option(self, schema_path: str):
        if self.allowed_values is None:
            return
        regex_objects = []
        av_path = f"{schema_path}.allowed_values"
        nadap.schema.is_non_empty_list(self.allowed_values, av_path)
        for index, value in enumerate(self.allowed_values):
            av_i_path = f"{av_path}[{index}]"
            self._test_data_type(value, av_i_path)
            regex_objects.append(
                nadap.schema.compile_regex_string(
                    pattern=value,
                    multiline=False,
                    fullmatch=True,
                    schema_path=av_i_path,
                )
            )
        self.allowed_values = regex_objects

    def _validate_not_allowed_values_option(self, schema_path: str):
        regex_objects = []
        av_path = f"{schema_path}.not_allowed_values"
        nadap.schema.is_list(self.not_allowed_values, av_path)
        for index, value in enumerate(self.not_allowed_values):
            av_i_path = f"{av_path}[{index}]"
            self._test_data_type(value, av_i_path)
            regex_objects.append(
                nadap.schema.compile_regex_string(
                    pattern=value,
                    multiline=False,
                    fullmatch=True,
                    schema_path=av_i_path,
                )
            )
        self.not_allowed_values = regex_objects

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)
        self._validate_allowed_values_option(schema_path)
        self._validate_not_allowed_values_option(schema_path)
        if self.maximum is not None:
            if self._relax_length:
                if self.maximum > 255:
                    raise SchemaDefinitionError(
                        msg="Exceeds allowed hostname length of 255 characters",
                        path=f"{schema_path}.maximum",
                    )
            elif self.maximum > 63:
                raise SchemaDefinitionError(
                    msg="Exceeds allowed hostname length of 63 characters",
                    path=f"{schema_path}.maximum",
                )
        if self._min_labels is not None:
            min_path = f"{schema_path}.minimum_labels"
            nadap.schema.is_int(self._min_labels, min_path)
            if self._min_labels < 1:
                raise SchemaDefinitionError(msg="Must be > 0", path=min_path)
        if self._max_labels is not None:
            max_path = f"{schema_path}.maximum_labels"
            nadap.schema.is_int(self._max_labels, max_path)
            if self._max_labels < 1:
                raise SchemaDefinitionError(msg="Must be > 0", path=max_path)
            if self._min_labels is not None and self._min_labels > self._max_labels:
                raise SchemaDefinitionError(
                    msg="Must be >= 'minimum_labels'", path=max_path
                )

    def _pop_options(self, definition: dict, schema_path: str):
        self.allowed_values = definition.pop("allowed_values", None)
        self.not_allowed_values = definition.pop("not_allowed_values", [])
        self._relax_length = definition.pop("relax_length", True)
        self._min_labels = definition.pop("minimum_labels", None)
        self._max_labels = definition.pop("maximum_labels", None)
        super()._pop_options(definition, schema_path)

    def _convert_reference_data(self, data: any) -> any:
        """
        Convert data to reference data
        """
        return data.lower()

    def _validate_allowed_data(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ):
        if not self.allowed_values:
            return
        if not nadap.schema.match_regex_objects(self.allowed_values, data)[0]:
            self._create_finding_with_error(
                msg="Data does not match any allowed regex patterns",
                path=path,
                env=env,
            )

    def _validate_not_allowed_data(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ):
        if not self.not_allowed_values:
            return
        matches, pattern = nadap.schema.match_regex_objects(
            self.not_allowed_values, data
        )
        if matches:
            self._create_finding_with_error(
                msg=f"Data does match not allowed regex pattern '{pattern.pattern}'",
                path=path,
                env=env,
            )

    def _validate_rfc_length(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ):
        invalid = False
        if self.maximum is None:
            if self._relax_length:
                if len(data) > 255:
                    env.findings.append(
                        nadap.results.ValidationFinding(
                            message="String length exceeds allowed 255 characters",
                            path=path,
                        )
                    )
                    invalid = True
            elif len(data) > 63:
                env.findings.append(
                    nadap.results.ValidationFinding(
                        message="String length exceeds allowed 63 characters",
                        path=path,
                    )
                )
                invalid = True
        if invalid:
            raise DataValidationError()
        if self._replace_empty_to is UNDEFINED and not data:
            self._create_finding_with_error(
                msg="Hostname must have at least one character",
                path=path,
                env=env,
            )

    def _validate_label(
        self,
        label: str,
        path: str,
        env: "ValEnv",
        label_index: int,
    ):
        messages = []
        for char_index, char_ in enumerate(label):
            if char_index == 0 and not char_.isalnum():
                if label_index > 0:
                    messages.append(
                        f"Hostname's label {label_index} does not start "
                        + "with an alphanumeric character"
                    )
                else:
                    messages.append(
                        "Hostname does not start with an alphanumeric character"
                    )
            elif char_index == len(label) - 1 and not char_.isalnum():
                if label_index > 0:
                    messages.append(
                        f"Hostname's label {label_index} does not end "
                        + "with an alphanumeric character"
                    )
                else:
                    messages.append(
                        "Hostname does not end with an alphanumeric character"
                    )
            elif not char_.isalnum() and not char_ == "-":
                if label_index > 0:
                    messages.append(
                        f"Hostname's label {label_index} contains illegal "
                        + f"character at position {label_index + 1}"
                    )
                else:
                    messages.append(
                        f"Hostname contains illegal character at position {char_index + 1}"
                    )
        if messages:
            for msg in messages:
                env.findings.append(
                    nadap.results.ValidationFinding(
                        message=msg,
                        path=path,
                    )
                )
            raise DataValidationError()

    def _validate_rfc_labels(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ):
        message = None
        invalid = False
        labels = data.split(".")
        if self._min_labels is not None and len(labels) < self._min_labels:
            message = f"Label count is lower than defined minimum of {self._min_labels}"
        if self._max_labels is not None and len(labels) > self._max_labels:
            message = (
                f"Label count is greater than defined maximum of {self._max_labels}"
            )
        for label_index, label in enumerate(labels, start=1):
            try:
                self._validate_label(
                    label=label,
                    path=path,
                    env=env,
                    label_index=label_index if len(labels) > 1 else 0,
                )
            except DataValidationError:
                invalid = True
        if invalid:
            raise DataValidationError()
        if message:
            env.findings.append(
                nadap.results.ValidationFinding(
                    message=message,
                    path=path,
                )
            )
            raise DataValidationError()

    def _validate_data(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> "any":
        data = super()._validate_data(data=data, path=path, env=env)
        invalid = False
        try:
            self._validate_rfc_length(data=data, path=path, env=env)
        except DataValidationError:
            invalid = True
        try:
            self._validate_rfc_labels(data=data, path=path, env=env)
        except DataValidationError:
            invalid = True
        if invalid:
            raise DataValidationError()
        self._validate_allowed_data(data=data, path=path, env=env)
        self._validate_not_allowed_data(data=data, path=path, env=env)
        return data

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        tf = super().restrictions
        if self.maximum is None and not self._relax_length:
            tf.append("max length: 63")
        if self._min_labels is not None:
            tf.append(f"min labels: {self._min_labels}")
        if self._max_labels is not None:
            tf.append(f"max labels: {self._max_labels}")
        if self.allowed_values:
            tf.append("allowed regex patterns:")
            tf.append(
                UnorderedTextList(
                    [rf"`{x.pattern.pattern}`" for x in self.allowed_values]
                )
            )
        if self.not_allowed_values:
            tf.append("not allowed regex patterns:")
            tf.append(
                UnorderedTextList(
                    [rf"`{x.pattern.pattern}`" for x in self.not_allowed_values]
                )
            )
        return tf

    @property
    def yaml_data_type(self) -> str:
        """Get YAML data type string"""
        return self.data_type_name.title()

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **relax_length** | <code>bool</code> | <code>True</code> | | "
            + "Relax hostname length from 63 to 255 characters |",
            "| **minimum_labels** | <code>int</code> | | min: 1 | "
            + "Minimum amount of labels within in hostname |",
            "| **maximum_labels** | <code>int</code> | | min: 1<br>>= 'minimum_labels' | "
            + "Maximum amount of labels within in hostname |",
            "| **allowed_values** | <code>list[str]</code> | | | "
            + " Data must match one of these regex patterns |",
            "| &nbsp;&nbsp;- < str > | <code>str</code> | | | |",
            "| **not_allowed_values** | <code>list[str]</code> | | | "
            + " Data mustn't match any of these regex patterns |",
            "| &nbsp;&nbsp;- < str > | <code>str</code> | | | |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "relax_length: <true|false>",
            "minimum_labels: <int>",
            "maximum_labels: <int>",
            "allowed_values:",
            "  - <str>",
            "not_allowed_values:",
            "  - <str>",
        ]


DOC_DT_CLASS = Hostname  # pylint: disable=invalid-name
