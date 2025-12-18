"""
Multitype2 data type class
"""

# pylint: disable=too-few-public-methods

import nadap.schema
from nadap.doc import TableRow
import nadap.types.base
from nadap.base import ValEnv
from nadap.errors import SchemaDefinitionError, DataValidationError

DOC_DT_NAME = "Multitype2"
DOC_DT_DESCRIPTION = """
A **multitype2** data type represents a selection of different data types.
It test data for being a valid input for a listed data type definition -
one by one. If a data type definition matches, a requested preprocessing
is applied. If no data type definition matches, the multitype2 data type
doesn't match and validation fails.

> Note: **multitype2** relaxes restrictions of **multitype** but loses
> details why a validation fails.
"""
DOC_DT_FEATURES = """
- Overlapping python class matching among listed data types is supported.
- Nesting multitype or multitype2 in multitype2 is supported.
- Data type conversion is not supported.
  Use conversion within listed data types instead.
"""
DOC_DT_YAML_EXAMPLE = """
type: multitype2
description: "Example multitype2 definition"
default_value: 0

types:
  - type: int
    reference: ref_key
  - type: str
    minimum: 4
    not_allowed_values:
      - 'test'
    reference: ref_key
  - type: str
    minimum: 2
    not_allowed_values:
      - 'me'
    reference: ref_key
"""


class MultiType2(nadap.types.base.BaseType):
    """
    Multitype2 datatype class
    """

    data_type_name = "multitype2"
    _convert_to_classes = {}

    def __init__(self, **kwargs):
        self.types = []
        super().__init__(**kwargs)

    def _pop_options(self, definition: dict, schema_path: str):
        if "types" not in definition:
            raise SchemaDefinitionError("Option types is required", schema_path)
        self.types = definition.pop("types")
        super()._pop_options(definition, schema_path)

    def _validate_options(self, schema_path: str):
        types_definition = self.types
        self.types = []
        nadap.schema.is_non_empty_list(types_definition, f"{schema_path}.types")
        _data_types = []
        for index, _type in enumerate(types_definition):
            i_path = f"{schema_path}.types[{index}]"
            if isinstance(_type, str):
                _type = {"type": _type}
            nadap.schema.is_dict(_type, i_path)
            dt = self._schema.load_data_type_by_definition(
                definition=_type, path=i_path
            )
            for python_class in dt.python_classes:
                if python_class in self.types:
                    raise SchemaDefinitionError(
                        f"Data type '{dt.data_type_name}' interferes with '"
                        + f"{self.types[python_class].data_type_name}'",
                        i_path,
                    )
            self.types.append(dt)
            _data_types.append(dt.data_type_name)
            for class_ in dt.python_classes:
                if class_ not in self.python_classes:
                    self.python_classes.append(class_)
        super()._validate_options(schema_path=schema_path)

    def _validate_data(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> "any":
        len_findings = len(env.findings)
        for data_type in self.types:
            try:
                return data_type.validate(data=data, path=path, env=env)
            except DataValidationError:
                if len_findings < len(env.findings):
                    del env.findings[len_findings - len(env.findings) :]
        self._create_finding_with_error(
            msg="None of the data types matches", path=path, env=env
        )
        return data

    @property
    def doc_table_rows(self) -> "list[TableRow]":
        """
        Get doc table rows for this data type definition
        """
        ret_list = super().doc_table_rows
        for index, dt in enumerate(self.types):
            dt_entries = dt.doc_table_rows
            dt_entries[0].variable.name = f"option {index + 1}"
            dt_entries[0].variable.placeholder = True
            for entry in dt_entries:
                entry.skip_yaml = True
            ret_list += dt_entries
            if index + 1 < len(self.types):
                or_entry = TableRow(variable="~or~")
                or_entry.skip_yaml = True
                ret_list.append(or_entry)
        return ret_list

    @property
    def doc_yaml(self) -> "list[str]":
        """
        Get data structure
        """
        if len(self.types) == 1:
            return list(self.types)[0].doc_yaml
        if dict in self.python_classes or list in self.python_classes:
            ret_list = ["# Multitype!!!"]
            for index, dt in enumerate(self.types):
                ret_list += dt.doc_yaml
                if index + 1 < len(self.types):
                    ret_list.append("# or")
            return ret_list
        types = [f"<{x.__name__}>" for x in self.python_classes]
        return [" or ".join(sorted(types))]

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **types** | <code>list[dict&#124;str]</code> | | required<br>min length: 1 | "
            + "List of type definitions |",
            "| &nbsp;&nbsp;- <type> | <code>dict&#124;str</code> | | | |",
            "| &nbsp;&nbsp;&nbsp;&nbsp;*option 1* | <code>str</code> | | "
            + "Data type string (short definition) |",
            "| &nbsp;&nbsp;&nbsp;&nbsp;*option 2* | <code>dict</code> | | "
            + "Data type definition |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "",
            "types:",
            "  - <dict|str>",
            "    # Mulitype!!!",
            "    <str>",
            "    # or",
            "    <dict>",
        ]


DOC_DT_CLASS = MultiType2  # pylint: disable=invalid-name
