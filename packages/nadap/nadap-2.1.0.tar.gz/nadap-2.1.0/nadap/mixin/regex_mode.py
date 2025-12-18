"""
RegexModeMixin
"""

# pylint: disable=too-few-public-methods


class RegexModeMixin:
    """
    Add options for regex mode
    """

    def __init__(self, **kwargs):
        self.regex_mode = False
        self.regex_fullmatch = True
        self.regex_multiline = False
        super().__init__(**kwargs)

    def _pop_options(self, definition: dict, schema_path: str):
        self.regex_fullmatch = definition.pop("regex_fullmatch", True)
        self.regex_multiline = definition.pop("regex_multiline", False)
        self.regex_mode = definition.pop("regex_mode", False)
        super()._pop_options(definition=definition, schema_path=schema_path)

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **regex_mode** | <code>bool</code> | <code>False</code> | | "
            + " Enable testing strings against regex strings |",
            "| **regex_fullmatch** | <code>bool</code> | <code>True</code> | | "
            + " Full string must match |",
            "| **regex_multiline** | <code>bool</code> | <code>False</code> | | "
            + " Regex *^* and *$* matches to newline character |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "regex_mode: <true|false>",
            "regex_fullmatch: <true|false>",
            "regex_multiline: <true|false>",
        ]
