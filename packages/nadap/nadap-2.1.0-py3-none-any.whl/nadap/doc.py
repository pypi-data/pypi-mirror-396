"""
Documentation Classes
"""

# pylint: disable=too-few-public-methods

from abc import abstractmethod
from nadap.base import UNDEFINED


HTML_INDENT = "&nbsp;&nbsp;"
START_LIST_CODE = "- "
MARKDOWN_INDENT = "&nbsp;&nbsp;"
STR_INDENT = "  "
NICE_YAML_INDENT = "  "


class TableRowElementMixin:
    """
    Mixin for attributes within the TableRow class
    """

    def __init__(self, *args, **kwargs):
        # pylint: disable=unused-argument
        self.table_row: "TableRow" = None

    @property
    @abstractmethod
    def html(self) -> str:
        """
        Returns a string respresenting this element in html code
        """

    @property
    @abstractmethod
    def markdown(self) -> str:
        """
        Returns a string respresenting this element in markdown code
        """

    @abstractmethod
    def __str__(self):
        return ""


class Indent(TableRowElementMixin):
    """
    Class to handle indent in variable column
    """

    def __init__(self, level: int = 0, start_list: bool = False):
        super().__init__()
        self.level = 0 if level is None else level
        self.start_list = start_list

    def _build_indent_str(self, indent_code: str, start_list_code: str) -> str:
        if self.level < 1:
            return ""
        indent_str = (self.level - 1) * indent_code
        if self.start_list:
            indent_str += start_list_code
        else:
            indent_str += indent_code
        return indent_str

    def __int__(self):
        return self.level

    def __eq__(self, value):
        return self.level == int(value)

    def __ne__(self, value):
        return self.level != int(value)

    def __gt__(self, value):
        return self.level > int(value)

    def __ge__(self, value):
        return self.level >= int(value)

    def __lt__(self, value):
        return self.level < int(value)

    def __le__(self, value):
        return self.level <= int(value)

    def __bool__(self) -> bool:
        return bool(self.level)

    @property
    def html(self) -> str:
        return self._build_indent_str(HTML_INDENT, START_LIST_CODE)

    @property
    def markdown(self) -> str:
        return self.html

    def __str__(self):
        return self._build_indent_str(STR_INDENT, START_LIST_CODE)

    @property
    def yaml(self) -> str:
        """
        Returns a string for indenting in nice YAML text
        """
        return self._build_indent_str(NICE_YAML_INDENT, START_LIST_CODE)


class Variable(TableRowElementMixin):
    """
    Class to handle variable information
    """

    def __init__(self, name: str):
        super().__init__()
        self.name = "" if name is None else name
        self.placeholder = False

    @property
    def _indent_html(self):
        if self.table_row:
            return self.table_row.indent.html
        return ""

    @property
    def _indent_yaml(self):
        if self.table_row:
            return self.table_row.indent.yaml
        return ""

    @property
    def _name_html(self):
        if self.placeholder:
            return f"*<em>{self.name}</em>*"
        return self.name

    @property
    def _name_markdown(self):
        if self.placeholder:
            return rf"\**{self.name}*\*"
        return self.name

    @property
    def _name_yaml(self):
        if self.placeholder:
            return f"*{self.name}*"
        return self.name

    @property
    def html(self) -> str:
        return f"{self._indent_html}{self._name_html}"

    def __str__(self):
        return self.name

    @property
    def markdown(self) -> str:
        return f"{self._indent_html}{self._name_markdown}"

    @property
    def yaml(self) -> str:
        """
        Returns indented name encoded for nice YAML text
        """
        return f"{self._indent_yaml}{self._name_yaml}"


class Type(TableRowElementMixin):
    """
    Class to handle type information
    """

    def __init__(self, t: "str|list[str]"):
        super().__init__()
        if t is None:
            self.types = []
        elif isinstance(t, list):
            self.types = t
        else:
            self.types = [t]

    @property
    def _type_str_html(self) -> str:
        """
        Return a type string encoded as html
        """
        if len(self.types) > 1:
            return "&#124;".join(sorted(self.types))
        return self.types[0]

    @property
    def _type_str_yaml(self) -> str:
        """
        Return a type string encoded as nice YAML text
        """
        if len(self.types) > 1:
            return "|".join(sorted(self.types))
        return self.types[0]

    @property
    def html(self) -> str:
        if not self.types:
            return ""
        return f"<code>{self._type_str_html}</code>"

    def __str__(self):
        return self._type_str_yaml

    @property
    def markdown(self) -> str:
        return self.html

    @property
    def yaml(self) -> str:
        """
        Returns data type encoded for nice YAML text
        """
        if self.types == ["dict"]:
            return "{}"
        if self.types == ["list"]:
            return "[]"
        return f"<{self._type_str_yaml}>"


class DefaultValue(TableRowElementMixin):
    """
    Represent a default value
    """

    def __init__(self, value):
        super().__init__()
        if value is None or value is UNDEFINED:
            self.value = ""
        else:
            self.value = str(value)

    def __bool__(self) -> bool:
        return bool(self.value)

    @property
    def html(self) -> str:
        return self.value

    def __str__(self):
        return self.value

    @property
    def markdown(self) -> str:
        return self.value


def transform_unformatted_text(t: "str|list") -> "TextElement":
    """
    Transform standard python classes to Text classes
    """
    if isinstance(t, str):
        return Text(t)
    return TextList([harmonize_text(x) for x in t])


def harmonize_text(t: "str|list|TextElement") -> "TextElement":
    """
    Transform standard python classes to Text classes if required
    """
    if t is None:
        return Text("")
    if isinstance(t, TextElement):
        return t
    if isinstance(t, (str, list)):
        return transform_unformatted_text(t)
    raise ValueError("Invalid input")


class TextElement:
    """
    Meta class for all TextField elements
    """

    @property
    @abstractmethod
    def html(self) -> str:
        """
        Return text element as html string
        """
        return

    @abstractmethod
    def __str__(self):
        """
        Return text element as plain multiline string
        """
        return ""


class Text(str, TextElement):
    """
    Represents a text in a text field
    """

    @property
    def html(self):
        return self

    def __repr__(self):
        return f"Text({super().__repr__()})"


class TextList(list, TextElement):
    """
    Represents a sequence of text (or other lists) in a text field

    < list element 1 >\n
    < list element 2 >
    """

    def __init__(self, iterable=None):
        if iterable:
            super().__init__([harmonize_text(x) for x in iterable])
        else:
            super().__init__()

    def _html_strings(self, indent: bool = False) -> "list[tuple[str,str]]":
        # pylint: disable=protected-access
        ret_list = []
        html_indent = HTML_INDENT if indent else ""
        for e in self:
            if isinstance(e, TextList):
                ret_list.extend(
                    [(f"{html_indent}{i}", t) for i, t in e._html_strings(indent=True)]
                )
            else:
                ret_list.append((html_indent, e.html))
        return ret_list

    @property
    def html(self):
        return "<br>".join([f"{x[0]}{x[1]}" for x in self._html_strings()])

    def _str_strings(self, indent: bool = False) -> str:
        # pylint: disable=protected-access
        ret_list = []
        str_indent = STR_INDENT if indent else ""
        for e in self:
            if isinstance(e, TextList):
                ret_list.extend(
                    [(f"{str_indent}{i}", t) for i, t in e._str_strings(indent=True)]
                )
            else:
                ret_list.append((str_indent, str(e)))
        return ret_list

    def __str__(self):
        return "\n".join([f"{x[0]}{x[1]}" for x in self._str_strings()])

    def append(self, x):
        x = harmonize_text(x)
        super().append(x)

    def prepend(self, x):
        """
        Insert element at front of the list
        """
        x = harmonize_text(x)
        super().insert(0, x)

    def insert(self, index, x):
        x = harmonize_text(x)
        super().insert(index, x)

    def extend(self, x):
        super().extend([harmonize_text(i) for i in x])

    def __repr__(self):
        return f"TextList({super().__repr__()})"


class UnorderedTextList(TextList):
    """
    Represents an unordered list of text (or other text elements) in a text field

    - < list element 1>\n
    - < list element 2>
    """

    def _html_strings(self, indent: bool = False) -> "list[tuple[str,str]]":
        # pylint: disable=protected-access
        ret_list = []
        for e in self:
            if isinstance(e, TextList):
                e_list = e._html_strings(indent=False)
                if e_list:
                    if e_list[0][0]:
                        if not e_list[0][0].endswith("- "):
                            e_list[0][0] = e_list[0][0][:-2] + "- "
                        ret_list.append((f"{HTML_INDENT}{e_list[0][0]}", e_list[0][1]))
                    else:
                        ret_list.append(("- ", e_list[0][1]))
                    ret_list.extend(
                        [(f"{HTML_INDENT}{x[0]}", x[1]) for x in e_list[1:]]
                    )
            else:
                ret_list.append(("- ", e.html))
        return ret_list

    def _str_strings(self, indent: bool = False) -> str:
        # pylint: disable=protected-access
        ret_list = []
        for e in self:
            if isinstance(e, TextList):
                e_list = e._str_strings(indent=False)
                if e_list:
                    if e_list[0][0]:
                        if not e_list[0][0].endswith(START_LIST_CODE):
                            e_list[0][0] = e_list[0][0][:-2] + START_LIST_CODE
                        ret_list.append((f"{STR_INDENT}{e_list[0][0]}", e_list[0][1]))
                    else:
                        ret_list.append((START_LIST_CODE, e_list[0][1]))
                    ret_list.extend([(f"{STR_INDENT}{x[0]}", x[1]) for x in e_list[1:]])
            else:
                ret_list.append((START_LIST_CODE, str(e)))
        return ret_list

    def __repr__(self):
        return f"UnorderedTextList({super().__repr__()})"


class TextField(TableRowElementMixin):
    """
    Class to handle text information
    """

    def __init__(self, t: "str|list|TextElement|TextField" = None):
        super().__init__()
        self._t = TextList()
        if t is not None:
            self.t = t

    def __bool__(self) -> bool:
        return bool(self._t)

    @property
    def t(self) -> "TextList":
        """
        Get text object
        """
        return self._t

    @t.setter
    def t(self, t: "str|list|TextElement"):
        """
        Set text object
        """
        if t is None:
            self._t = TextList()
        t = self._harmonize_input(t)
        if isinstance(t, TextList):
            self._t = t
        else:
            self._t = TextList()
            self._t.append(t)

    @classmethod
    def _harmonize_input(cls, t: "str|list|TextElement|TextField") -> "TextElement":
        if isinstance(t, TextField):
            return t.t
        return harmonize_text(t)

    def append(self, t: "str|list|TextElement"):
        """
        Add text object to the end of the internal sequence
        """
        if isinstance(t, (TextElement, str)):
            self._t.append(t)
        else:
            self._t.extend(t)

    def prepend(self, t: "str|list|TextElement"):
        """
        Add text object to the front of the internal sequence
        """
        if isinstance(t, list):
            for x in t:
                self._t.prepend(x)
        else:
            self._t.prepend(t)

    @property
    def html(self) -> str:
        """
        Returns text field encoded in html
        """
        return self.t.html

    @property
    def markdown(self) -> str:
        """
        Returns text field encoded in markdown (as html)
        """
        return self.html

    def __str__(self):
        """
        Returns text field as plain multiline string
        """
        return str(self.t)


class TableRow:
    """
    Class represent a row within a documentation table
    """

    # pylint: disable=too-many-instance-attributes,missing-function-docstring

    def __init__(self, **kwargs):
        self.path = kwargs.get("path", "")
        self._indent: "Indent" = None
        self.indent = kwargs.get("indent", None)
        self._variable: "Variable" = None
        self.variable = kwargs.get("variable", None)
        self._type: "Type" = None
        self.type = kwargs.get("type", None)
        self._default: "DefaultValue" = None
        self.default = kwargs.get("default", None)
        self._restrictions: "TextField" = None
        self.restrictions = kwargs.get("restrictions", None)
        self._description: "TextField" = None
        self.description = kwargs.get("description", None)

        # Indicator if corresponding data type is a structure type
        # and sub-sequent table entries exists.
        self.empty_structure = False
        self.key_value = False
        self.skip_yaml = False

    def _setattr(self, attr_, x_, class_):
        if isinstance(x_, class_):
            setattr(self, attr_, x_)
        else:
            setattr(self, attr_, class_(x_))
        getattr(self, attr_).table_row = self

    @property
    def indent(self) -> "Indent":
        return self._indent

    @indent.setter
    def indent(self, x: "Indent|int|None"):
        self._setattr("_indent", x, Indent)

    @property
    def variable(self) -> "Variable":
        return self._variable

    @variable.setter
    def variable(self, x: "Variable"):
        self._setattr("_variable", x, Variable)

    @property
    def type(self) -> "Type":
        return self._type

    @type.setter
    def type(self, x: "Type|str|list[str]|None"):
        self._setattr("_type", x, Type)

    @property
    def default(self) -> "DefaultValue":
        return self._default

    @default.setter
    def default(self, x):
        self._setattr("_default", x, DefaultValue)

    @property
    def description(self) -> "TextField":
        return self._description

    @description.setter
    def description(self, x: "str|list[str]|Text|TextList|UnorderedTextList|TextField"):
        self._setattr("_description", x, TextField)

    @property
    def restrictions(self) -> "TextField":
        return self._restrictions

    @restrictions.setter
    def restrictions(
        self, x: "str|list[str]|Text|TextList|UnorderedTextList|TextField"
    ):
        self._setattr("_restrictions", x, TextField)

    @property
    def markdown(self) -> str:
        """
        Returns a text string representing a row within a markdown table
        """
        return (
            "| "
            + " | ".join(
                [
                    self.variable.markdown,
                    self.type.markdown,
                    self.default.markdown,
                    self.restrictions.markdown,
                    self.description.markdown,
                ]
            )
            + " |"
        )

    @property
    def yaml(self) -> str:
        """
        Returns a text string representing a row within a markdown table
        """
        if (
            not self.empty_structure
            and len(self.type.types) == 1
            and self.type.types[0] in ["dict", "list"]
        ):
            if not self.variable.name:
                return f"{self.indent.yaml}"
            return f"{self.variable.yaml}:"
        if self.variable.placeholder and not self.key_value:
            return self.indent.yaml + self.type.yaml
        return f"{self.variable.yaml}: {self.type.yaml}"


class Doc:
    """
    Class represents the documentation of a schema
    """

    table_columns = [
        "Variable",
        "Type",
        "Default",
        "Restrictions",
        "Description",
    ]

    def __init__(self, rows: "list[TableRow]" = None):
        if rows:
            self.rows: "list[TableRow]" = rows
        else:
            self.rows: "list[TableRow]" = []

    @property
    def markdown_table_header_rows(self) -> list[str]:
        """
        Returns a list of the a markdown table header strings
        """
        return [
            "| " + " | ".join([f"**{x}**" for x in self.table_columns]) + " |",
            "| --- | --- | --- | --- | --- |",
        ]

    def append(self, row: "TableRow"):
        """
        Add a table row at the end of this table
        """
        self.rows.append(row)

    def extend(self, rows: "list[TableRow]"):
        """
        Add a list of table rows at the end of this table
        """
        self.rows.extend(rows)

    @property
    def _markdown_table_rows(self) -> list[str]:
        return [x.markdown for x in self.rows]

    @property
    def markdown_table(self) -> str:
        """
        Returns a multiline string representing a markdown table
        """
        return "\n".join(self.markdown_table_header_rows + self._markdown_table_rows)

    @property
    def nice_yaml(self) -> str:
        """
        Returns a multiline string representing a nice yaml
        """
        return "\n".join([x.yaml for x in self.rows if not x.skip_yaml])
