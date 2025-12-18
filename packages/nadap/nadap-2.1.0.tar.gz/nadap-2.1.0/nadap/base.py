"""
Basic constants and functions
"""

# pylint: disable=too-few-public-methods

import enum
import copy
import re

if hasattr(re, "NOFLAG"):
    NOFLAG = re.NOFLAG
else:
    NOFLAG = 0


class OPT(enum.IntFlag):  # pylint: disable=no-member
    """
    Flags used to define a reference
    """

    NONE = 1
    UNIQUE = 2
    UNIQUE_GLOBAL = 4
    PRODUCER = 8
    PRODUCER_GLOBAL = 16
    CONSUMER = 32
    CONSUMER_GLOBAL = 64
    ALLOW_ORPHAN_PRODUCER = 128


INIT_OPTIONS = OPT.UNIQUE | OPT.UNIQUE_GLOBAL | OPT.PRODUCER | OPT.PRODUCER_GLOBAL


class RegexObject:
    """
    Represents a regex allowed or not allowed value
    """

    def __init__(self, pattern: str, multiline: bool, fullmatch: bool):
        self.multiline = multiline
        self.fullmatch = fullmatch
        self.pattern = re.compile(pattern, self.flags)

    @property
    def flags(self) -> list:
        """
        Create a list of re args to pass to match
        """
        if self.multiline:
            return re.MULTILINE
        return NOFLAG

    def match(self, data: any) -> re.Match:
        """
        Test data if it matches
        Returns:
            re.Match object or None
        """
        if self.fullmatch:
            return self.pattern.fullmatch(data)
        return self.pattern.search(data)

    def __hash__(self):
        return self.pattern.pattern.__hash__()


class PreProcessingFlag(enum.IntFlag):  # pylint: disable=no-member
    """
    Flags used as pre-processing options
    """

    NOFLAG = 0
    SET_DEFAULTS = 1
    CONVERT_DATA = 2


class ValEnv:
    """
    Contains information and references required during
    validation and pre-processing
    """

    def __init__(
        self,
        references,
        findings,
        flags: PreProcessingFlag = PreProcessingFlag.NOFLAG,
    ):
        self.references = references
        self.findings = findings
        self.flags = flags


NOFLAG = PreProcessingFlag.NOFLAG
SET_DEFAULTS = PreProcessingFlag.SET_DEFAULTS
CONVERT_DATA = PreProcessingFlag.CONVERT_DATA
UNDEFINED = object()


def str_list_out(l: list) -> str:
    """
    creates a str from a list, representing an proper output
    """
    if len(l) == 0:
        return ""
    if len(l) == 1:
        return f"'{str(l[0])}'"
    return "'" + "', '".join([str(x) for x in l[:-1]]) + f"' or '{str(l[-1])}'"


def number_to_str_number(x: any) -> any:
    """
    Test if x is a str and represents an integer.
    If yes return a string 'x', else return x
    """
    if isinstance(x, str):
        try:
            int(x)
            x = f"'{x}'"
        except ValueError:
            try:
                float(x)
                x = f"'{x}'"
            except ValueError:
                pass
    return x


def merge_lists(left: list, right: list, list_merge: str = "append_rp") -> list:
    """
    Merge elements of list 'right' into list 'left'
    """
    if not isinstance(left, list):
        raise ValueError("'left' is not a list")
    if not isinstance(right, list):
        raise ValueError("'right' is not a list")
    _left = copy.deepcopy(left)
    if list_merge == "replace":
        return copy.deepcopy(right)
    if list_merge == "append":
        return _left + copy.deepcopy(right)
    if list_merge == "prepend":
        return copy.deepcopy(right) + _left
    if list_merge in ["append_rp", "prepend_rp"]:
        append = list_merge == "append_rp"
        for element in right:
            if element not in _left:
                if append:
                    _left.append(copy.deepcopy(element))
                else:
                    _left.insert(0, copy.deepcopy(element))
        return _left
    raise ValueError(f"'list_merge' option {list_merge} is not known")


def merge_dictionaries(
    left: dict, right: dict, recursive: bool = True, list_merge: str = "append_rp"
) -> dict:
    """
    Merge keys (recursively) from dictionary 'right' into dictionary 'left'.
    """
    if not isinstance(left, dict):
        raise ValueError("'left' is not a dictionary")
    if not isinstance(right, dict):
        raise ValueError("'right' is not a dictionary")
    _left = copy.deepcopy(left)
    for key, r_value in right.items():
        if key not in _left or not isinstance(r_value, type(_left[key])):
            # right element not in left or mismatching types => Just copy right to left
            _left[key] = copy.deepcopy(r_value)
        else:
            # left value is same type as right value
            if isinstance(r_value, list):
                # Merge left list with right list
                _left[key] = merge_lists(
                    left=_left[key], right=right[key], list_merge=list_merge
                )
            elif isinstance(r_value, dict):
                if recursive:
                    # Merge left dict with right dict
                    _left[key] = merge_dictionaries(
                        left=_left[key],
                        right=right[key],
                        recursive=recursive,
                        list_merge=list_merge,
                    )
                else:
                    # Overwrite left with right value
                    _left[key] = copy.deepcopy(r_value)
            else:
                # Something like integer or string and just copy right to left
                _left[key] = copy.deepcopy(r_value)
    return _left


def merge_template_data(
    template_data: dict,
    additional_data: dict,
    recursive: bool = True,
    list_merge: str = "append_rp",
) -> dict:
    """
    Merge definition from 'additional' template into template.
    """
    template_data = template_data.copy()
    template_data_keys = set(list(template_data.keys()))
    additional_data_keys = set(list(additional_data.keys()))
    return_dict = template_data
    for key in template_data_keys.intersection(additional_data_keys):
        if isinstance(additional_data[key], list):
            if isinstance(template_data[key], list):
                return_dict[key] = merge_lists(
                    left=template_data[key],
                    right=additional_data[key],
                    list_merge=list_merge,
                )
            else:
                return_dict[key] = additional_data[key]
        elif not isinstance(additional_data[key], dict) or not isinstance(
            template_data[key], dict
        ):
            return_dict[key] = additional_data[key]
        else:
            return_dict[key] = merge_dictionaries(
                left=template_data[key],
                right=additional_data[key],
                recursive=recursive,
                list_merge=list_merge,
            )
    for key in additional_data_keys - template_data_keys:
        return_dict[key] = additional_data[key]
    return return_dict
