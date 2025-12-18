"""
List classes
"""

# pylint: disable=too-few-public-methods

import nadap.types.base
import nadap.mixin.replace_empty_to
import nadap.mixin.min_max
import nadap.mixin.allow_duplicate
from nadap.doc import TableRow


DOC_DT_NAME = "List"
DOC_DT_DESCRIPTION = """
An **list** data type tests data for being an instance of
python's built-in class `list`.
"""
DOC_DT_FEATURES = """
- Validate list length
- Validate uniqueness of elements
- Supports **Referencing Feature**
"""
DOC_DT_YAML_EXAMPLE = """
type: list
description: "Example list definition for a list of strings"
default_value:
  - nadap
  - rulez!

minimum: 2
maximum: 15
allow_duplicates: false

elements: str

reference: ref_key
"""


class ListBase(
    nadap.mixin.replace_empty_to.ReplaceEmptyToMixin,
    nadap.mixin.min_max.MinMaxLengthMixin,
    nadap.types.base.BaseType,
):
    """
    List datatype base class
    """

    _cls_python_classes = [list]
    _support_replace_empty_to = True

    def __init__(self, **kwargs):
        self.elements_data_type = None
        super().__init__(**kwargs)

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)
        self.elements_data_type = self._schema.load_data_type_by_definition(
            self.elements_data_type, f"{schema_path}.elements"
        )

    def _pop_options(self, definition: dict, schema_path: str):
        self.elements_data_type = definition.pop("elements", "any")
        super()._pop_options(definition, schema_path)

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **elements** | <code>dict&#124;str</code> | | required | "
            + "List element's data type definition |",
            "| &nbsp;&nbsp;*option 1* | <code>str</code> | | "
            + "List element's data type string (short definition) |",
            "| &nbsp;&nbsp;*option 2* | <code>dict</code> | | "
            + "List element's data type definition |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "",
            "elements: <dict|str>",
            "  # Mulitype!!!",
            "  <str>",
            "  # or",
            "  <dict>",
        ]


class List(nadap.mixin.allow_duplicate.AllowDuplicateMixin, ListBase):
    """
    List datatype class
    """

    data_type_name = "list"
    _doc_data_type = "list"

    @property
    def yaml_data_type(self) -> str:
        """Get YAML data type string"""
        if self.elements_data_type.python_classes:
            return f"list[{self.elements_data_type.yaml_data_type}]"
        return f"list[{self.elements_data_type.data_type_name}]"

    @property
    def doc_table_rows(self) -> "list[TableRow]":
        """
        Get doc table entries for this data type definition
        """
        e_entries = self.elements_data_type.doc_table_rows
        for e in e_entries:
            e.path = "[]" + e.path
        if len(e_entries) == 1:
            # Element is not a data structure
            e_entries[0].indent = 1
            e_entries[0].variable = self.elements_data_type.doc_value_name
            e_entries[0].variable.placeholder = True
        elif e_entries[0].type.types == ["list"]:
            # Element is a list
            for entry in e_entries:
                entry.indent.level += 1
        else:
            # Element is a non-empty dictionary
            e_entries = e_entries[1:]
            for entry in e_entries:
                entry.indent.level += 1
        e_entries[0].indent.start_list = True

        return super().doc_table_rows + e_entries

    @property
    def doc_yaml(self) -> "list[str]":
        """
        Get data structure
        """
        element_doc_yaml = self.elements_data_type.doc_yaml
        ret_lines = []
        for index, line in enumerate(element_doc_yaml):
            if not index:
                ret_lines.append(f"- {line}")
                continue
            ret_lines.append(f"  {line}")
        return ret_lines


DOC_DT_CLASS = List  # pylint: disable=invalid-name
