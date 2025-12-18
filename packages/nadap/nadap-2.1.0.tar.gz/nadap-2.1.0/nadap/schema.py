"""
Class Schema
"""

# pylint: disable=too-few-public-methods

import copy
import re
import nadap.types.byte4_value
import nadap.types.any
import nadap.types.list
import nadap.types.base
import nadap.types.bgp_as
import nadap.types.bool
import nadap.types.bool_false
import nadap.types.bool_true
import nadap.types.enum
import nadap.types.float
import nadap.types.hostname
import nadap.types.hostname_or_ip
import nadap.types.idlist
import nadap.types.int
import nadap.types.int8
import nadap.types.int16
import nadap.types.int32
import nadap.types.ip_address
import nadap.types.ip4_address
import nadap.types.ip6_address
import nadap.types.ip_interface
import nadap.types.ip4_interface
import nadap.types.ip6_interface
import nadap.types.ip_network
import nadap.types.ip4_network
import nadap.types.ip6_network
import nadap.types.mac_address
import nadap.types.multitype
import nadap.types.multitype2
import nadap.types.none
import nadap.types.number
import nadap.types.dict
import nadap.types.str
import nadap.types.str_float
import nadap.types.str_int
import nadap.types.str_number
import nadap.types.uint8
import nadap.types.uint16
import nadap.types.uint32
from nadap.doc import Doc
import nadap.references
from nadap.base import merge_dictionaries, RegexObject
from nadap.errors import SchemaDefinitionError

if hasattr(re, "PatternError"):
    PatternError = re.PatternError
else:
    PatternError = re.error


def is_list(l, path: str):
    """
    Test if given value (t) is a instance of class list; else raise an error.
    """
    if not isinstance(l, list):
        raise SchemaDefinitionError(msg="Must be a list", path=path)


def is_non_empty_list(l, path: str):
    """
    Test if given value (t) is a instance of class list
    and is not empty; else raise an error.
    """
    is_list(l, path)
    if not l:
        raise SchemaDefinitionError(
            msg="Mustn't be empty",
            path=path,
        )


def is_dict(d, path: str):
    """
    Test if given value (d) is a instance of class dict; else raise an error.
    """
    if not isinstance(d, dict):
        raise SchemaDefinitionError(msg="Must be a dictionary", path=path)


def is_str(s, path: str):
    """
    Test if given value (s) is a instance of class str; else raise an error.
    """
    if not isinstance(s, str):
        raise SchemaDefinitionError(msg="Must be a string", path=path)


def is_bool(b, path: str):
    """
    Test if given value (b) is a instance of class bool; else raise an error.
    """
    if not isinstance(b, bool):
        raise SchemaDefinitionError(msg="Must be a boolean", path=path)


def is_int(s, path: str):
    """
    Test if given value (s) is a instance of class int; else raise an error.
    """
    if not isinstance(s, int):
        raise SchemaDefinitionError(msg="Must be an integer", path=path)


def is_list_merge_option(o: str, path: str):
    """
    Test if given list_merge option is valid
    """
    is_str(o, path)
    if o not in ["append", "append_rp", "prepend", "prepend_rp", "replace"]:
        raise SchemaDefinitionError(msg="Invalid list merge option", path=path)


def no_more_definition_options(definition: dict, source: str, path: str):
    """
    Test if given definition dictionary is empty.
    Else raise an error for containing (unknown) options.
    """
    if definition:
        str_list = list(definition)
        if len(definition) > 1:
            last = str_list[-1]
            str_list = str_list[:-1]
            msg = f"Unknown {source} options {', '.join(str_list)} and {last}"
        else:
            msg = f"Unknown {source} option {str_list[0]}"
        raise SchemaDefinitionError(msg, path)


def compile_regex_string(
    pattern: str, multiline: bool, fullmatch: bool, schema_path: str
) -> "RegexObject":
    """
    Try to compile regex object based on given arguments
    """
    try:
        re_obj = RegexObject(pattern, multiline, fullmatch)
    except (PatternError, TypeError) as e:
        raise SchemaDefinitionError("Not a valid regex pattern", schema_path) from e
    if not pattern:
        raise SchemaDefinitionError(
            "Empty string not allowed as regex pattern", schema_path
        )
    return re_obj


def match_regex_objects(regex_objects: list, data: str) -> tuple[bool, str]:
    """
    Check if string matches any of the regex objects
    """
    for re_obj in regex_objects:
        if re_obj.match(data):
            return True, re_obj.pattern
    return False, ""


class Schema:
    """
    Class Schema
    """

    # pylint: disable=too-many-instance-attributes

    type_class_matching = {
        "4byte_value": nadap.types.byte4_value.Byte4Value,
        "any": nadap.types.any.Any,
        "bgp_as": nadap.types.bgp_as.BgpAs,
        "bool": nadap.types.bool.Bool,
        "bool_false": nadap.types.bool_false.BoolFalse,
        "bool_true": nadap.types.bool_true.BoolTrue,
        "dict": nadap.types.dict.Dict,
        "enum": nadap.types.enum.Enum,
        "float": nadap.types.float.Float,
        "hostname": nadap.types.hostname.Hostname,
        "hostname_or_ip": nadap.types.hostname_or_ip.HostnameOrIP,
        "idlist": nadap.types.idlist.IDList,
        "int": nadap.types.int.Int,
        "int8": nadap.types.int8.Int8,
        "int16": nadap.types.int16.Int16,
        "int32": nadap.types.int32.Int32,
        "ip_address": nadap.types.ip_address.IpAddress,
        "ip4_address": nadap.types.ip4_address.Ip4Address,
        "ip6_address": nadap.types.ip6_address.Ip6Address,
        "ip_network": nadap.types.ip_network.IpNetwork,
        "ip4_network": nadap.types.ip4_network.Ip4Network,
        "ip6_network": nadap.types.ip6_network.Ip6Network,
        "ip_interface": nadap.types.ip_interface.IpInterface,
        "ip4_interface": nadap.types.ip4_interface.Ip4Interface,
        "ip6_interface": nadap.types.ip6_interface.Ip6Interface,
        "list": nadap.types.list.List,
        "multitype": nadap.types.multitype.MultiType,
        "multitype2": nadap.types.multitype2.MultiType2,
        "mac_address": nadap.types.mac_address.MacAddress,
        "none": nadap.types.none.Null,
        "number": nadap.types.number.Number,
        "str": nadap.types.str.Str,
        "str_float": nadap.types.str_float.StrFloat,
        "str_int": nadap.types.str_int.StrInt,
        "str_number": nadap.types.str_number.StrNumber,
        "uint8": nadap.types.uint8.Uint8,
        "uint16": nadap.types.uint16.Uint16,
        "uint32": nadap.types.uint32.Uint32,
    }

    def __init__(self, definition: dict = None):
        self.references = nadap.references.References()
        self.reference_findings = []

        self.name = ""
        self.description = ""

        self.root = None
        self.custom_data_types = {}
        self.templates = {}
        self.template_merge_recursive = True
        self.template_list_merge = "append_rp"
        self.template_stack = []

        if definition is not None:
            self.load_definition(definition)

    def _is_loaded(self):
        """
        Check if Schema has loaded a schema definition
        """
        if self.root is None:
            raise RuntimeError("Schema definition hasn't been loaded")

    def _merge_template_definition(self, definition: dict, path: str) -> dict:
        definition = copy.deepcopy(definition)
        template_name = definition.pop("template", None)
        if template_name:
            if f"template.{template_name}" in path.split(" > "):
                raise SchemaDefinitionError(
                    "Nested template loop", f"{path} > template.{template_name}"
                )
            if template_name not in self.templates:
                raise SchemaDefinitionError(
                    f"Unknown template {template_name}",
                    f"{path}.template",
                )
            t_merge_opts = definition.pop("template_merge_options", {})
            list_merge_option = t_merge_opts.pop("list_merge", self.template_list_merge)
            is_list_merge_option(
                list_merge_option, f"{path}.template_merge_options.list_merge"
            )
            definition = merge_dictionaries(
                left=self.templates[template_name],
                right=definition,
                recursive=t_merge_opts.pop("recursive", self.template_merge_recursive),
                list_merge=list_merge_option,
            )
            definition = self._merge_template_definition(
                definition, f"{path} > template.{template_name}"
            )
        return definition

    def load_data_type_by_definition(
        self, definition: dict | str, path: str
    ) -> nadap.types.base.BaseType:
        """
        Identify and load data type object by given definition.
        """
        if isinstance(definition, str):
            definition = {"type": definition}
        elif not isinstance(definition, dict):
            raise SchemaDefinitionError(
                "Data type definition must be a string or dictionary", path
            )
        # First look up if this is an custom data type:
        if cdt_def := self.custom_data_types.get(definition.get("type", None), None):
            new_def = copy.deepcopy(cdt_def)
            new_def.update(definition)
            definition = new_def
        if template_name := definition.pop("template", None):
            if template_name not in self.templates:
                raise SchemaDefinitionError(
                    f"Unknown template {template_name}",
                    f"{path}.template",
                )
            t_merge_opts = definition.pop("template_merge_options", {})
            list_merge_option = t_merge_opts.pop("list_merge", self.template_list_merge)
            is_list_merge_option(
                list_merge_option, f"{path}.template_merge_options.list_merge"
            )
            definition = merge_dictionaries(
                left=self.templates[template_name],
                right=definition,
                recursive=t_merge_opts.pop("recursive", self.template_merge_recursive),
                list_merge=list_merge_option,
            )
        _type = definition.pop("type", None)
        if _type is None:
            raise SchemaDefinitionError(msg="Key 'type' missing.", path=path)
        # If this is a CDT options have already been merged,
        # but "type" was overwritten. Pull in "type" excplicitly from CDT.
        if _type in self.custom_data_types:
            _type = self.custom_data_types[_type]["type"]
        if _type not in self.type_class_matching:
            raise SchemaDefinitionError(
                msg=f"Data type '{_type}' not found",
                path=path,
            )
        data_type_class = self.type_class_matching[_type]
        data_type = data_type_class(
            schema=self, definition=definition, schema_path=path
        )
        if unknown_options := sorted(definition):
            if len(unknown_options) > 1:
                unknown_options = [f"'{x}'" for x in unknown_options]
                msg = f"Unknown options {', '.join(unknown_options)}"
            else:
                msg = f"Unknown option '{unknown_options[0]}'"
            raise SchemaDefinitionError(
                msg=f"{msg} for data type {data_type_class.data_type_name}", path=path
            )
        return data_type

    def _parse_custom_data_types(self, definition):
        for name, cdt_definition in definition.pop("custom_data_types", {}).items():
            if cdt_definition.get("type", None) not in self.type_class_matching:
                raise SchemaDefinitionError(
                    "Not a built-in data type", f"custom_data_types.{name}"
                )
            self.load_data_type_by_definition(
                copy.deepcopy(cdt_definition),
                f"custom_data_types.{name}",
            )
            self.custom_data_types[name] = cdt_definition

    def _parse_template_merge_options(self, definition):
        template_merge_options = definition.pop("template_merge_options", {})
        path = "template_merge_options"
        is_dict(template_merge_options, path)
        self.template_merge_recursive = template_merge_options.pop(
            "recursive", self.template_merge_recursive
        )
        self.template_list_merge = template_merge_options.pop(
            "list_merge", self.template_list_merge
        )
        is_list_merge_option(self.template_list_merge, f"{path}.list_merge")

    def _parse_templates(self, definition):
        self.templates = definition.pop("templates", {})
        # Check if template definition is a correct data type definition.
        for name, t_definition in self.templates.items():
            self.templates[name] = self._merge_template_definition(
                t_definition, f"template.{name}"
            )

    def load_definition(self, definition: dict) -> "nadap.types.base.DataType":
        """
        Parse schema definition and returns the root data type of this schema.
        """
        definition = copy.deepcopy(definition)
        self.name = definition.pop("name", "")
        self.description = definition.pop("description", "")
        self._parse_template_merge_options(definition)
        self._parse_templates(definition)
        self._parse_custom_data_types(definition)
        try:
            root = definition.pop("root")
        except KeyError as e:
            raise SchemaDefinitionError(f"Missing schema definition key {e}") from e
        if unknown_options := sorted(definition):
            if len(unknown_options) > 1:
                unknown_options = [f"'{x}'" for x in unknown_options]
                msg = f"Unknown schema options {', '.join(unknown_options)}"
            else:
                msg = f"Unknown schema option '{unknown_options[0]}'"
            raise SchemaDefinitionError(msg=msg)
        self.root = self.load_data_type_by_definition(
            definition=root,
            path="root",
        )
        return self.root

    @property
    def _doc_table(self) -> "Doc":
        entries = self.root.doc_table_rows
        if (
            len(entries) > 1
            and (entries[0].type.types in [["dict"], ["list"]])
            and not entries[0].default
            and not entries[0].description
        ):
            entries = entries[1:]
        return Doc(entries)

    def doc(self, fmt: str) -> str:
        """
        Get documentation for this data schema

        Arguments:
            format:     str
                        Intended output format
                        Allowed values:
                        - markdown
                        - yaml
                        - none
        Returns:        str
                        Documentation in requested format
        """
        self._is_loaded()

        doc_table = self._doc_table

        if fmt == "markdown":
            ret_str = doc_table.markdown_table
        elif fmt == "yaml":
            ret_str = doc_table.nice_yaml
        elif fmt == "none":
            ret_str = doc_table
        else:
            raise RuntimeError("Unknown documentation format")
        return ret_str

    def doc_sections(self, fmt: str, level: int = 0) -> dict:
        """
        Get documentation split into sections.
        If data type is an object data type, documentation is
        split into each key. This is done recursively up to 'level' deep.

        Arguments:
            format:     str
                        Intended output format
                        Allowed values:
                        - markdown
                        - yaml
                        - none
            level:      int >= 0
                        Split level
        Returns:        dict
                        Keys: keys in data type
                        Values:
                            str - Key path within data schema
                            str - Documentation of sub data schema
        """
        # Check if schema is initialized
        self._is_loaded()

        # Parse split rows to intended format
        dict_str = {}
        split_doc, remain_doc = self.root.get_doc_table_rows_dict(max_level=level)
        if remain_doc:
            raise RuntimeError("Schema's root data type is not 'dict'")
        if fmt == "markdown":
            for key_path, entries in split_doc.items():
                dict_str[key_path] = Doc(entries).markdown_table
        elif fmt == "yaml":
            for key_path, entries in split_doc.items():
                dict_str[key_path] = Doc(entries).nice_yaml
        elif fmt == "none":
            for key_path, entries in split_doc.items():
                dict_str[key_path] = Doc(entries)
        else:
            raise RuntimeError("Unknown documentation format")
        return dict_str

    def structured_doc(
        self, fmt: str, structure: "dict|list[str]"
    ) -> "tuple[dict[str, str], str]":
        """
        Get documentation snippets based on given structure.

        Structure means a list of strings or lists of strings
        in a nested dictionary.
        Dictionaries in the structure shall map to
        the 'dict' data types in the schema.
        List of strings shall represent keys in the 'dict' data type.

        Matching dict/keys will be returned as dictioniary with key path as key
        and documentation string as value. (First tuple element)

        Non-matching keys or structure elements will be return in
        a documentation string. (Second tuple element)

        Arguments:
            format:     str
                        Intended output format
                        Allowed values:
                        - markdown
                        - yaml
                        - none
            structure:  List of strings (keys)
                        or nested dicts of list of strings
        """
        # Check if schema is initialized
        self._is_loaded()

        # Parse split rows to intended format
        structured_doc = {}
        structured_doc, remaining_entries = self.root.get_structured_doc_table_rows(
            structure=structure
        )
        if fmt == "markdown":
            for key_path, entries in structured_doc.items():
                structured_doc[key_path] = Doc(entries).markdown_table
            remaining_doc = Doc(remaining_entries).markdown_table
        elif fmt == "yaml":
            for key_path, entries in structured_doc.items():
                structured_doc[key_path] = Doc(entries).nice_yaml
            remaining_doc = Doc(remaining_entries).nice_yaml
        elif fmt == "none":
            for key_path, entries in structured_doc.items():
                structured_doc[key_path] = Doc(entries)
            remaining_doc = Doc(remaining_entries)
        else:
            raise RuntimeError("Unknown documentation format")
        return (structured_doc, remaining_doc)
