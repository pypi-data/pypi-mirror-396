"""
Datatype base class
"""

# pylint: disable=too-few-public-methods

from nadap.base import UNDEFINED, SET_DEFAULTS, CONVERT_DATA, ValEnv, OPT
from nadap.errors import SchemaDefinitionError, DataValidationError, NadapReferenceError
import nadap.references
import nadap.results
import nadap.schema
from nadap.doc import TableRow, TextField


class BaseType:
    """
    Abstract root class for all data types
    """

    # pylint: disable=too-many-instance-attributes

    _cls_python_classes = []
    _support_ns_separator = False
    _support_replace_empty_to = False
    _convert_to_classes = {"str": str}
    _markdown_indent = "&nbsp;&nbsp;"
    data_type_name = None
    _doc_data_type_name = None

    def __init__(
        self,
        schema: "nadap.schema.Schema",
        definition: dict,
        schema_path: str,
    ):
        self.default_value = UNDEFINED
        self.description = ""
        self.references = []
        self.python_classes = self._cls_python_classes[:]
        self._convert_to = None
        self._doc_value_name = None
        self._schema = schema

        self._pop_options(definition=definition, schema_path=schema_path)
        nadap.schema.no_more_definition_options(
            definition=definition, source="data type", path=schema_path
        )
        self._validate_options(schema_path=schema_path)

    @staticmethod
    def _raise_exceptions(messages: "list[str]", path: str, env: "ValEnv|None"):
        if messages:
            if isinstance(messages, str):
                messages = [messages]
            if env is None:
                raise SchemaDefinitionError(
                    messages[0],
                    path,
                )
            for m in messages:
                env.findings.append(
                    nadap.results.ValidationFinding(
                        message=m,
                        path=path,
                    )
                )
            raise DataValidationError()

    @property
    def _data_type_mismatch_message(self) -> str:
        """
        Get error message if data does not match data type
        """
        return f"Data is not an instance of {self._python_classes_list_str}"

    @staticmethod
    def _refopt_mode(mode: str, schema_path: str) -> "OPT":
        if mode == "unique":
            return OPT.UNIQUE | OPT.PRODUCER
        if mode == "producer":
            return OPT.PRODUCER
        if mode == "consumer":
            return OPT.CONSUMER
        raise SchemaDefinitionError("Unsupported mode", f"{schema_path}.mode")

    def _pop_reference_definition(self, ref_definition: dict, schema_path: str):
        # pylint: disable=too-many-branches,unsupported-membership-test
        nadap.schema.is_dict(ref_definition, schema_path)
        opt_path = f"{schema_path}."

        if not ref_definition:
            return
        # parse "key"
        if "key" not in ref_definition.keys():
            raise SchemaDefinitionError("Key missing", f"{opt_path}key")
        ref_key = ref_definition.pop("key")
        nadap.schema.is_str(ref_key, f"{opt_path}key")

        # Parse "mode"
        ref_options = self._refopt_mode(
            ref_definition.pop("mode", "unique"), schema_path
        )
        u_scope = ref_definition.pop("unique_scope", "global")
        p_scope = ref_definition.pop("producer_scope", "global")
        c_scope = ref_definition.pop("consumer_scope", "global")
        orphan = ref_definition.pop("allow_orphan_producer", True)
        ref_credits = ref_definition.pop("credits", None)
        if OPT.UNIQUE in ref_options:
            if u_scope == "global":
                ref_options = ref_options | OPT.UNIQUE_GLOBAL
            elif u_scope != "namespace":
                raise SchemaDefinitionError(
                    "Must be either 'global' or 'namespace'",
                    opt_path + "unique_scope",
                )
            if ref_credits is not None and ref_credits < 0:
                raise SchemaDefinitionError(
                    "Must be >=0",
                    opt_path + "credits",
                )
        if OPT.PRODUCER in ref_options:
            if p_scope == "global":
                ref_options = ref_options | OPT.PRODUCER_GLOBAL
            elif p_scope != "namespace":
                raise SchemaDefinitionError(
                    "Must be either 'global' or 'namespace'",
                    opt_path + "producer_scope",
                )
            if orphan:
                ref_options = ref_options | OPT.ALLOW_ORPHAN_PRODUCER
            if ref_credits is not None and ref_credits < 0:
                raise SchemaDefinitionError(
                    "Must be >=0",
                    opt_path + "credits",
                )
        if OPT.CONSUMER in ref_options:
            if c_scope == "global":
                ref_options = ref_options | OPT.CONSUMER_GLOBAL
            elif c_scope != "namespace":
                raise SchemaDefinitionError(
                    "Must be either 'global' or 'namespace'",
                    opt_path + "consumer_scope",
                )
            if ref_credits is not None and ref_credits < 0:
                raise SchemaDefinitionError(
                    "Must be >0",
                    opt_path + "credits",
                )

        if not isinstance(orphan, bool):
            raise SchemaDefinitionError(
                "Must be bool", opt_path + "allow_orphan_producer"
            )

        if self._support_ns_separator:
            ns_sep = ref_definition.pop("namespace_separator_char", None)
            if ns_sep is not None and (not isinstance(ns_sep, str) or len(ns_sep) != 1):
                raise SchemaDefinitionError(
                    "Must be a single character string",
                    f"{schema_path}.namespace_separator_char",
                )
        else:
            ns_sep = None

        nadap.schema.no_more_definition_options(
            definition=ref_definition, source="reference", path=schema_path
        )

        self.references.append(
            nadap.references.RefDef(
                ref_key=ref_key,
                ref_options=ref_options,
                ref_credits=ref_credits,
                ns_separator=ns_sep,
            )
        )

    def _pop_reference(self, ref_definition: "dict|str", schema_path: str):
        # If reference is a string, bypass parsing reference options:
        ref_path = f"{schema_path}.reference"
        if isinstance(ref_definition, str):
            ref_definition = {"key": ref_definition}
        self._pop_reference_definition(ref_definition, ref_path)

    def _pop_references(self, ref_definitions: dict | str, schema_path: str):
        ref_path = f"{schema_path}.references"
        nadap.schema.is_list(ref_definitions, ref_path)

        for index, ref_definition in enumerate(ref_definitions):
            self._pop_reference_definition(ref_definition, f"{ref_path}[{index}]")

    def _pop_convert_options(self, definition: dict, schema_path: str):
        con_to = "convert_to"
        if con_to in definition:
            c_path = f"{schema_path}.{con_to}"
            if not self._convert_to_classes:
                raise SchemaDefinitionError(
                    "Data type does not support conversion", c_path
                )
            target_class = definition.pop(con_to)
            nadap.schema.is_str(target_class, c_path)
            if target_class not in self._convert_to_classes:
                raise SchemaDefinitionError("Target data type not supported", c_path)
            self._convert_to = self._convert_to_classes[target_class]

    def _pop_options(self, definition: dict, schema_path: str):
        """
        Pop data type options from definition
        """
        self.default_value = definition.pop("default_value", UNDEFINED)

        self.description = definition.pop("description", self.description)
        self._pop_convert_options(definition=definition, schema_path=schema_path)

        dvn = "doc_value_name"
        if dvn in definition:
            self._doc_value_name = definition.pop(dvn)
            nadap.schema.is_str(self._doc_value_name, f"{schema_path}.{dvn}")

        if "reference" in definition and "references" in definition:
            raise SchemaDefinitionError(
                "Data type option 'references' excludes option 'reference'",
                schema_path,
            )
        self._pop_reference(definition.pop("reference", {}), schema_path)
        self._pop_references(definition.pop("references", []), schema_path)

    def _validate_options(self, schema_path: str):
        if self.default_value is not UNDEFINED:
            self._test_data_type(self.default_value, f"{schema_path}.default_value")
        nadap.schema.is_str(self.description, f"{schema_path}.description")

    def _set_default(self, data: any):
        """
        Set values of nested data types to default if missing.
        """
        return data

    def _detect_data_format(self, data) -> str:  # pylint: disable=unused-argument
        return None

    def _apply_data_format(self, data: "any", fmt: str = None) -> "any":
        if fmt is None:
            return data
        return data

    def _convert_data(self, data: any) -> any:
        """
        Change data type
        """
        if self._convert_to is not None:
            return self._convert_to(data)
        return data

    def _preprocess_data(self, data: any, env: "ValEnv"):
        if SET_DEFAULTS in env.flags:
            data = self._set_default(data)
        if CONVERT_DATA in env.flags:
            data = self._convert_data(data)
        return data

    def _convert_reference_data(self, data: any) -> any:
        """
        Convert data to reference data
        """
        return data

    def validate(
        self,
        data: any,
        path: str,
        env: "ValEnv",
    ) -> "any":
        """
        Check if data matches defined data type,
        apply preprocessing and
        complies to referencing
        """
        data = self._validate_data(data=data, path=path, env=env)
        data = self._preprocess_data(data=data, env=env)
        return self._reference_data(data=data, path=path, env=env)

    def _validate_data(self, data: any, path: str, env: ValEnv) -> "any":
        """
        Check if data matches defined data type.
        """
        return self._test_data_type(data=data, path=path, env=env)

    def _reference_data(self, data: any, path: str, env: ValEnv) -> "any":
        """
        Check if data matches defined data type.
        """
        for ref_def in self.references:
            if ref_def.ns_separator and ref_def.ns_separator in data:
                provider_ns, value = data.split(ref_def.ns_separator, 1)
                element = nadap.references.ConsumerElement(
                    ref_def=ref_def,
                    path=path,
                    value=self._convert_reference_data(value),
                    provider_namespace=provider_ns,
                )
            else:
                element = nadap.references.ReferenceElement(
                    ref_def=ref_def,
                    path=path,
                    value=self._convert_reference_data(data),
                )
            try:
                env.references.add_element(element)
            except NadapReferenceError as e:
                env.findings.append(
                    nadap.references.ReferenceFinding(message=str(e), path=path)
                )
        return data

    def _test_data_type(self, data: any, path: str, env: "ValEnv" = None) -> "any":
        if not self.python_classes:
            return data
        if not isinstance(data, tuple(self.python_classes)):
            if env is None:
                raise SchemaDefinitionError(
                    self._data_type_mismatch_message,
                    path,
                )
            self._create_finding_with_error(self._data_type_mismatch_message, path, env)
        return data

    def _create_finding_with_error(self, msg: str, path: str, env: "ValEnv"):
        env.findings.append(
            nadap.results.ValidationFinding(
                message=msg,
                path=path,
            )
        )
        raise DataValidationError()

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        return TextField()

    @property
    def doc_value_name(self) -> str:
        """
        Get Value name for documentation
        """
        if self._doc_value_name is not None:
            return self._doc_value_name
        if self.python_classes:
            return "|".join(sorted([x.__name__ for x in self.python_classes]))
        return self.data_type_name

    @property
    def _python_classes_list_str(self) -> str:
        if len(self.python_classes) == 1:
            return f"'{self.python_classes[0].__name__}'"
        cls_str = sorted([f"'{x.__name__}'" for x in self.python_classes])
        return f"{', '.join(cls_str[:-1])} or {cls_str[-1]}"

    @property
    def yaml_data_type(self) -> str:
        """Get YAML data type string"""
        if self.python_classes:
            return "|".join(sorted([x.__name__ for x in self.python_classes]))
        return f"{self.data_type_name}"

    @property
    def doc_types(self) -> list[str]:
        """Get list of data type strings"""
        if self.python_classes:
            return sorted([x.__name__ for x in self.python_classes])
        return [self.data_type_name]

    @property
    def doc_table_rows(self) -> "list[TableRow]":
        """
        Get list of documentation table entries
        """
        return [
            TableRow(
                type=self.doc_types,
                default=self.default_value,
                restrictions=self.restrictions,
                description=self.description.splitlines(),
            )
        ]

    def get_doc_table_rows_dict(
        self, max_level: int = 0, _level: int = 0
    ) -> "tuple[dict[str, list[TableRow]], list[TableRow]]":
        """
        Returns split doc table entry lists.
        First tuple element contains a dictionary with sub-key paths as key and
        list of TableEntry as value.
        Second tuple element contains a list of TableEntry for remaining
        (or non sub-key) documentation.
        """
        # pylint: disable=unused-argument
        return (
            {},
            self.doc_table_rows,
        )

    def get_structured_doc_table_rows(
        self, structure: "dict|list[str]"
    ) -> "tuple[dict[str, list[TableRow]], list[TableRow]]":
        """
        Returns doc table entry lists according to given structure.
        First tuple element contains a dictionary with sub-key paths as key and
        list of TableEntry as value - sub-key paths matches the given structure.
        Second tuple element contains a list of TableEntry for remaining
        (not structure matching) documentation.
        """
        # pylint: disable=unused-argument
        return (
            {},
            self.doc_table_rows,
        )

    @classmethod
    def _doc_md_type(cls):
        if cls._cls_python_classes:
            return (
                "<code>"
                + "&#124;".join(sorted([x.__name__ for x in cls._cls_python_classes]))
                + "</code>"
            )
        return "`any`"

    @classmethod
    def _doc_yaml_type(cls):
        if cls._cls_python_classes:
            return "|".join(sorted([x.__name__ for x in cls._cls_python_classes]))
        return "any"

    @property
    def doc_yaml(self) -> "any":
        """
        Get data structure
        """
        return [f"<{self.yaml_data_type}>"]

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        ret_list = [
            f"| **type** | <code>str</code> | | '{cls.data_type_name}' | |",
            "| **description** | <code>str</code> | | | Data type description |",
            "| **default_value** | | | Must match data type's type(s) | "
            + "Value used to set as default value |",
        ]
        if cls._convert_to_classes:
            ret_list.append(
                "| **convert_to** | <code>str</code> | | Allowed values:<br>- "
                + "<br>- ".join(sorted(cls._convert_to_classes.keys()))
                + " | |"
            )
        return ret_list

    @classmethod
    def _doc_ref_options_md_table_rows(cls, indent: int = 0) -> list[str]:
        ret_list = [
            f"| {'&nbsp;&nbsp;' * indent}**key** | <code>str</code> | | required | |",
            f"| {'&nbsp;&nbsp;' * indent}**mode** | <code>str</code> | "
            + "| Allowed values:<br>- unique<br>- "
            + "producer<br>- consumer | |",
            f"| {'&nbsp;&nbsp;' * indent}**unique_scope** "
            + "| <code>str</code> | | Allowed values:<br>- "
            + "global<br>- namespace | |",
            f"| {'&nbsp;&nbsp;' * indent}**producer_scope** "
            + "| <code>str</code> | | Allowed values:<br>- "
            + "global<br>- namespace | |",
            f"| {'&nbsp;&nbsp;' * indent}**consumer_scope** "
            + "| <code>str</code> | | Allowed values:<br>- "
            + "global<br>- namespace | |",
            f"| {'&nbsp;&nbsp;' * indent}**allow_orphan_producer** "
            + "| <code>bool</code> | <code>True</code> | | |",
            f"| {'&nbsp;&nbsp;' * indent}**credit** | <code>int</code> "
            + "| 1 (if mode consumer) | min: 0 | |",
        ]
        if cls._support_ns_separator:
            ret_list.append(
                f"| {'&nbsp;&nbsp;' * indent}**namespace_separator_char** "
                + "| <code>str</code> | | length must be 1 | |"
            )
        return ret_list

    @classmethod
    def _doc_options_md_lower_part(cls) -> list[str]:
        ret_list = [
            "| **template** | <code>str</code>| | must be definded in schema "
            + "| Merge options from this "
            + "template |",
            "| **template_merge_options** | <code>dict</code>| | "
            + "| Define schema-global template merge "
            + "instructions |",
            "| &nbsp;&nbsp;&nbsp;&nbsp;**recursive** | <code>bool</code> "
            + "| <code>True</code> | | Merge data type "
            + "definition options in template options recursively.<br>If false, data type "
            + "defintion options overwrites template options. |",
            "| &nbsp;&nbsp;&nbsp;&nbsp;**list_merge** | <code>str</code> | append_rp | "
            + "Allowed values:<br>- append<br>- append_rp<br>- prepend<br>- prepend_rp<br>- "
            + "replace | How lists within options data should be merged. |",
            "| **reference** | <code>dict&#124;str</code> | | | |",
            "| &nbsp;&nbsp;*option 1* | <code>str</code> | | "
            + "| Reference keys (implies unique global mode) |",
            "| &nbsp;&nbsp;*option 2* | <code>dict</code> | | | |",
        ]
        ret_list.extend(cls._doc_ref_options_md_table_rows(indent=1))
        ret_list.extend(
            [
                "| **references** | <code>list[dict&#124;str]</code> | | | |",
                "| &nbsp;&nbsp;- <reference defintiion> | <code>dict&#124;str</code> | | | |",
                "| &nbsp;&nbsp;&nbsp;&nbsp;option 1 | <code>str</code> | | | Reference keys "
                + "(implies unique global mode) |",
                "| &nbsp;&nbsp;&nbsp;&nbsp;option 2 | <code>dict</code> | | | |",
            ]
        )
        ret_list.extend(cls._doc_ref_options_md_table_rows(indent=2))
        ret_list.append(
            "| **doc_value_name** | <code>str</code> | | | Set value name for documentation |"
        )
        return ret_list

    @classmethod
    def doc_options_md_table_rows(cls) -> list[str]:
        """
        Get a list of markdown table rows with all
        definition options for this data type for documentation
        """
        return cls._doc_options_md_upper_part() + cls._doc_options_md_lower_part()

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        ret_list = [
            f"type: {cls.data_type_name}",
            "description: <str>",
            "default_value: <default_value>",
            "",
        ]
        if cls._convert_to_classes:
            ret_list.append(
                f"convert_to: <{'|'.join(sorted(cls._convert_to_classes.keys()))}>"
            )
        return ret_list

    @classmethod
    def _doc_ref_options_yaml_rows(cls, indent: int = 0) -> list[str]:
        ret_list = [
            f"{'  ' * indent}key: <str>",
            f"{'  ' * indent}mode: <unique|producer|consumer>",
            f"{'  ' * indent}unique_scope: <global|namespace>",
            f"{'  ' * indent}producer_scope: <global|namespace>",
            f"{'  ' * indent}consumer_scope: <global|namespace>",
            f"{'  ' * indent}allow_orphan_producer: <true|false>",
            f"{'  ' * indent}credits: <int>",
        ]
        if cls._support_ns_separator:
            ret_list.append(f"{'  ' * indent}namespace_separator_char: <str>")
        return ret_list

    @classmethod
    def _doc_options_yaml_lower_part(cls) -> list[str]:
        ret_list = [
            "",
            "template: <str>",
            "template_merge_options:",
            "  recursive: <true|false>",
            "  list_merge: <append|append_rp|prepend|prepend_rp|replace>",
            "",
            "reference: <reference_definition>",
            "  # Multitype!!!",
            "  <str>",
            "  # or:",
        ]
        ret_list.extend(cls._doc_ref_options_yaml_rows(indent=1))
        ret_list.extend(
            [
                "references:",
                "  - <reference_definition>",
                "    # Multitype!!!",
                "    <str>",
                "    # or",
            ]
        )
        ret_list.extend(cls._doc_ref_options_yaml_rows(indent=2))
        ret_list.append("")
        ret_list.append("doc_value_name: <str>")
        return ret_list

    @classmethod
    def doc_options_yaml_rows(cls) -> list[str]:
        """
        Get a list of YAML text rows with all
        definition options for this data type for documentation
        """
        return cls._doc_options_yaml_upper_part() + cls._doc_options_yaml_lower_part()
