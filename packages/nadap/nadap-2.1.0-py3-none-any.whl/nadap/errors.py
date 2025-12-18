"""
Execption classes
"""

# pylint: disable=too-few-public-methods


class SchemaDefinitionError(Exception):
    """
    Error while parsing schema definition.
    """

    def __init__(self, msg: str, path: str = None):
        if path is not None:
            msg = f"{path}: {msg}"
        super().__init__(msg)


class DataValidationError(Exception):
    """
    Exception indicating that data validation failed.
    """


class NadapReferenceError(Exception):
    """
    Class to identify an error during reference processing
    """
