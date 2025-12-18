"""
String data type class
"""

# pylint: disable=too-few-public-methods

from typing import TYPE_CHECKING

import nadap.types.base
import nadap.mixin.regex_mode
import nadap.mixin.min_max
import nadap.mixin.replace_empty_to
import nadap.schema
from nadap.base import ValEnv
from nadap.doc import UnorderedTextList

if TYPE_CHECKING:
    from nadap.doc import TextField

DOC_DT_NAME = "String"
DOC_DT_DESCRIPTION = """
A **str** data type tests data for being an instance of
python's built-in class `str`.

> If using *str* data type without regex mode, allowed values and
> no conversion defined, check *enum* data type as a better option.
"""
DOC_DT_FEATURES = """
- Validate string length
- Validate against allowed and not allowed strings
- **Regex Mode** validates data strings based on regex patterns.
- Supports **Referencing Feature**. Adds an option to lookup values in other namespaces.
- Data type conversion is not supported
"""
DOC_DT_YAML_EXAMPLE = r"""
type: str
description: "Example str definition with regex mode disabled"
default_value: "Hello World!"

minimum: 3
maximum: 15

not_allowed_values:
  - nadap sucks!

reference: ref_key
```

Example with regex mode enabled:

```yaml
type: str
description: "Example str definition with regex mode enabled and namespace lookup"

minimum: 4
maximum: 15

regex_mode: true
allowed_values:
  - '[a-z_\.]*'
not_allowed_values:
  - \d+.*

reference:
  key: ref_key
  mode: consumer
  namespace_separator_char: '.'
"""


class Str(
    nadap.mixin.replace_empty_to.ReplaceEmptyToMixin,
    nadap.mixin.regex_mode.RegexModeMixin,
    nadap.mixin.min_max.MinMaxLengthMixin,
    nadap.types.base.BaseType,
):
    """
    String datatype class
    """

    data_type_name = "str"
    _cls_python_classes = [str]
    _convert_to_classes = {}
    _support_ns_separator = True
    _support_replace_empty_to = True
    _doc_data_type = "str"

    def __init__(self, **kwargs):
        self.allowed_values = None
        self.not_allowed_values = []
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
            if self.regex_mode:
                regex_objects.append(
                    nadap.schema.compile_regex_string(
                        pattern=value,
                        multiline=self.regex_multiline,
                        fullmatch=self.regex_fullmatch,
                        schema_path=av_i_path,
                    )
                )
        if self.regex_mode:
            self.allowed_values = regex_objects

    def _validate_not_allowed_values_option(self, schema_path: str):
        regex_objects = []
        av_path = f"{schema_path}.not_allowed_values"
        nadap.schema.is_list(self.not_allowed_values, av_path)
        for index, value in enumerate(self.not_allowed_values):
            av_i_path = f"{av_path}[{index}]"
            self._test_data_type(value, av_i_path)
            if self.regex_mode:
                regex_objects.append(
                    nadap.schema.compile_regex_string(
                        pattern=value,
                        multiline=self.regex_multiline,
                        fullmatch=self.regex_fullmatch,
                        schema_path=av_i_path,
                    )
                )
        if self.regex_mode:
            self.not_allowed_values = regex_objects

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)
        self._validate_allowed_values_option(schema_path)
        self._validate_not_allowed_values_option(schema_path)

    def _pop_options(self, definition: dict, schema_path: str):
        self.allowed_values = definition.pop("allowed_values", None)
        self.not_allowed_values = definition.pop("not_allowed_values", [])
        super()._pop_options(definition, schema_path)

    def _validate_allowed_data(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ):
        if not self.allowed_values:
            return
        if self.regex_mode:
            matches = nadap.schema.match_regex_objects(self.allowed_values, data)[0]
            if not matches:
                self._create_finding_with_error(
                    msg="Data does not match any allowed regex patterns",
                    path=path,
                    env=env,
                )
        elif data not in self.allowed_values:
            self._create_finding_with_error(
                msg="Data not within allowed strings",
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
        if self.regex_mode:
            matches, pattern = nadap.schema.match_regex_objects(
                self.not_allowed_values, data
            )
            if matches:
                self._create_finding_with_error(
                    msg=f"Data does match not allowed regex pattern '{pattern.pattern}'",
                    path=path,
                    env=env,
                )
        elif data in self.not_allowed_values:
            self._create_finding_with_error(
                msg="Data is a not allowed string",
                path=path,
                env=env,
            )

    def _validate_data(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> "any":
        data = super()._validate_data(data=data, path=path, env=env)
        self._validate_allowed_data(data=data, path=path, env=env)
        self._validate_not_allowed_data(data=data, path=path, env=env)
        return data

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        tf = super().restrictions
        if self.regex_mode:
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
            if self.regex_fullmatch or self.regex_multiline:
                r_options = []
                if self.regex_fullmatch:
                    r_options.append("fullmatch")
                if self.regex_multiline:
                    r_options.append("multiline")
                tf.append(f"Regex match options: {', '.join(r_options)}")
        else:
            if self.allowed_values:
                tf.append("allowed strings:")
                tf.append(UnorderedTextList([rf"`{x}`" for x in self.allowed_values]))
            if self.not_allowed_values:
                tf.append("not allowed strings:")
                tf.append(
                    UnorderedTextList([rf"`{x}`" for x in self.not_allowed_values])
                )
        return tf

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **allowed_values** | <code>list[str]</code> | | | "
            + " Data must match one of these strings/regex strings |",
            "| &nbsp;&nbsp;- < str > | <code>str</code> | | | |",
            "| **not_allowed_values** | <code>list[str]</code> | | | "
            + " Data mustn't match any of these strings/regex strings |",
            "| &nbsp;&nbsp;- < str > | <code>str</code> | | | |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "allowed_values:",
            "  - <str>",
            "not_allowed_values:",
            "  - <str>",
        ]


DOC_DT_CLASS = Str  # pylint: disable=invalid-name
