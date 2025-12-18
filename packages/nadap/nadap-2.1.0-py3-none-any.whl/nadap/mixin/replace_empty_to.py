"""
ReplaceEmptyToMixin
"""

# pylint: disable=too-few-public-methods

from nadap.base import UNDEFINED


class ReplaceEmptyToMixin:
    """
    Add option to replace empty data with defined value
    """

    def __init__(self, **kwargs):
        self._replace_empty_to = UNDEFINED
        super().__init__(**kwargs)

    def _pop_options(self, definition: dict, schema_path: str):
        self._replace_empty_to = definition.pop("replace_empty_to", UNDEFINED)
        super()._pop_options(definition=definition, schema_path=schema_path)

    def _convert_data(self, data: any) -> any:
        if self._replace_empty_to is not UNDEFINED and not data:
            return self._replace_empty_to
        return super()._convert_data(data)

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **replace_empty_to** | <code>any</code> | | | "
            + " An empty input value will be replaced by this data |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "replace_empty_to: <any>",
        ]
