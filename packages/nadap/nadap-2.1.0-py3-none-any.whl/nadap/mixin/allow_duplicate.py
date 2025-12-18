"""
AllowDuplicateMixin
"""

# pylint: disable=too-few-public-methods

from typing import TYPE_CHECKING

from nadap.errors import DataValidationError
from nadap.base import ValEnv
import nadap.results

if TYPE_CHECKING:
    from nadap.doc import TextField


class AllowDuplicateMixin:
    """
    Allow or forbid duplicates in lists
    """

    def __init__(self, **kwargs):
        self.allow_duplicates = True
        super().__init__(**kwargs)

    def _pop_options(self, definition: dict, schema_path: str):
        self.allow_duplicates = definition.pop(
            "allow_duplicates", self.allow_duplicates
        )
        super()._pop_options(definition, schema_path)

    def _validate_data(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> "any":
        data = super()._validate_data(data=data, path=path, env=env)
        ret_data = []
        invalid = False
        processed_elements = []
        for index, v in enumerate(data):
            if not self.allow_duplicates and v in processed_elements:
                env.findings.append(
                    nadap.results.ValidationFinding(
                        "Duplicate list element", f"{path}[{index}]"
                    )
                )
                invalid = True
            else:
                try:
                    e_data = self.elements_data_type.validate(
                        data=v,
                        path=f"{path}[{index}]",
                        env=env,
                    )
                except DataValidationError:
                    invalid = True
                else:
                    ret_data.append(e_data)
                    processed_elements.append(e_data)
        if invalid:
            raise DataValidationError
        return ret_data

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        tf = super().restrictions
        if not self.allow_duplicates:
            tf.append("all elements must be unique")
        return tf

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **allow_duplicates** | <code>bool</code> | <code>True</code> | | |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "allow_duplicates: <true|false>",
        ]
