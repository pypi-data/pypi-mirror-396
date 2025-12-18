"""
Class Nadap
"""

from nadap.base import PreProcessingFlag, NOFLAG, ValEnv
from nadap.errors import DataValidationError
import nadap.references
import nadap.schema
import nadap.results


class Nadap:
    """
    Class Nadap
    """

    def __init__(self):
        self._references = nadap.references.References()
        self._validation_findings = nadap.results.FindingList()
        self._schema = None

    @property
    def schema(self) -> "nadap.schema.Schema":
        """
        Current loaded schema.
        """
        if self._schema is None:
            raise RuntimeError("Schema hasn't been set")
        return self._schema

    @schema.setter
    def schema(self, schema: nadap.schema.Schema | dict):
        if isinstance(schema, nadap.schema.Schema):
            self._schema = schema
        elif isinstance(schema, dict):
            self._schema = nadap.schema.Schema()
            self._schema.load_definition(schema)
        else:
            raise ValueError("Schema must be dict or Schema")
        self._root = self._schema.root

    @property
    def findings(
        self,
    ) -> "list[nadap.references.ReferenceFinding|nadap.results.ValidationFinding]":
        """
        Get all findings by previous validations
        """
        return (
            self._validation_findings + self._references.get_producer_consumer_issues()
        )

    def load_schema_definition(self, definition: dict) -> "nadap.schema.Schema":
        """
        Load schema definition and returns the initialized schema object.
        """
        self.schema = definition
        return self._schema

    def switch_namespace(self, namespace: str):
        """
        Switch to given namespace.
        Create namespace if not used before
        """
        self._references.change_namespace(namespace)
        self._validation_findings.namespace = namespace

    def validate(self, data: any, flags: PreProcessingFlag = NOFLAG) -> any:
        """
        Validate and pre-process data
        Given data remains unchanged.
        Returned data is pre-processed
        """
        if not isinstance(flags, PreProcessingFlag):
            raise ValueError("flags must be nadap pre-processing flags")
        try:
            r_data = self.schema.root.validate(
                data=data,
                path="",
                env=ValEnv(self._references, self._validation_findings, flags=flags),
            )
        except DataValidationError as e:
            raise DataValidationError(
                "Data Validation failed. Get findings for details."
            ) from e
        return r_data
