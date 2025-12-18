"""
Results and finding classes
"""

# pylint: disable=too-few-public-methods


class Finding:
    """
    Base class for all findings
    """

    def __init__(self, message: str, path: str = None) -> None:
        self.path = path if path else ""
        self.message = message
        self.namespace = ""

    def __str__(self) -> str:
        _str = self.message
        if self.path:
            _str = self.path + ": " + _str
        if self.namespace:
            _str = self.namespace + " > " + _str
        return _str

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return str(self) > str(other)

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        return str(self) < str(other)

    def __le__(self, other):
        return self < other or self == other


class ValidationFinding(Finding):
    """
    Class to handle a finding during data validation process
    """


class FindingList(list):
    """
    List containing all findings
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace = None

    def append(self, f: "Finding"):
        """
        Append new finding and change namespace within finding.
        """
        if self.namespace:
            f.namespace = self.namespace
        super().append(f)

    def extend(self, f: "list[Finding]"):
        """
        Append new finding and change namespace within finding.
        """
        if self.namespace:
            for i in f:
                i.namespace = self.namespace
        super().extend(f)
