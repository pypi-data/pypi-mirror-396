"""
Reference classes and errors
"""

# pylint: disable=too-few-public-methods

import nadap.results
from nadap.base import OPT
from nadap.errors import NadapReferenceError


class RefDef:
    """
    Represent all information from reference definition for a data type.
    """

    def __init__(
        self,
        ref_key: str,
        ref_options: OPT,
        ref_credits: int = None,
        ns_separator: str = None,
    ):
        self.key = ref_key
        self.options = ref_options
        if ref_credits is None and OPT.CONSUMER in ref_options:
            self.credits = 1
        else:
            self.credits = ref_credits
        self.ns_separator = ns_separator

    def __eq__(self, v: "RefDef"):
        return (
            self.key == v.key
            and self.options == v.options
            and self.credits == v.credits
            and self.ns_separator == v.ns_separator
        )


class ReferenceElement:
    """ReferenceElement stores all information regarding a reference value analyzed in data"""

    def __init__(
        self,
        ref_def: RefDef,
        path: str = "",
        value: any = None,
        namespace: str = "",
    ) -> None:
        """
        Args:
            ref_def: RefDef object - Reference definition from schema

            path: string - Value's path in data structure

            value: any - Value data

            namespace: string - active namepsace during reference creation

        Raises:
            ValueError: If arg's data type is wrong.
        """
        self.ref_def = ref_def
        self.namespace = namespace
        self.path = path
        self.value = value
        self.consumes_from = []
        self.provides_to = []

    @property
    def key(self) -> str:
        """
        Get reference key from reference definition
        """
        return self.ref_def.key

    @property
    def options(self) -> str:
        """
        Get reference options from reference definition
        """
        return self.ref_def.options

    @property
    def credits(self) -> str:
        """
        Get reference credits from reference definition
        """
        return self.ref_def.credits


class ConsumerElement(ReferenceElement):
    """
    Sub-class to ReferenceElement
    Specialized for Consumer References
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments

    def __init__(
        self,
        ref_def: RefDef,
        path: str = "",
        value: any = None,
        namespace: str = "",
        provider_namespace: str = "",
    ) -> None:
        """
        Args:
            < ReferenceElement's arguements >

            provider_namespace: string - namespace where to search
                                for providers (namespace lookup feature)

        Raises:
            ValueError: If arg's data type is wrong.
        """
        super().__init__(
            ref_def=ref_def,
            path=path,
            value=value,
            namespace=namespace,
        )
        self.provider_namespace = provider_namespace


class ReferenceFinding(nadap.results.Finding):
    """
    Sub-class to Finding
    ReferenceFinding stores all information to a reference issue and
    provides a method to present all information as a string (makes it easy for user interfaces)
    """

    def __init__(
        self, message: str, path: str = None, reference: ReferenceElement = None
    ) -> None:
        super().__init__(message, path)
        self.reference = reference

    def __str__(self):
        ns_lookup = False
        namespace = ""
        if self.reference:
            if (
                isinstance(self.reference, ConsumerElement)
                and self.reference.provider_namespace
            ):
                ns_lookup = True
                namespace = self.reference.namespace + " > "
            elif self.reference.namespace:
                namespace = self.reference.namespace + " > "
        path = self.path + ": " if self.path else ""
        message = (
            f"{self.message} in '{self.reference.provider_namespace}'"
            if ns_lookup
            else self.message
        )
        return namespace + path + message


class GlobalSpace:
    """
    GlobalSpace is a space where to register references in global scope.
    Adding References will stored according to the mode and
    links (consumer<>producer) to other refererences will be created.
    """

    uOPT = OPT.UNIQUE_GLOBAL
    pOPT = OPT.PRODUCER_GLOBAL
    cOPT = OPT.CONSUMER_GLOBAL

    def __init__(self) -> None:
        self.references = {}

    def get_uniques_by_value(self, value: any, ref_key: str) -> list[ReferenceElement]:
        """
        Get all unique elements to a reference key with given value
        """
        return self._get_elements_by_value(value, ref_key, "uniques")

    def get_producers_by_value(
        self, value: any, ref_key: str
    ) -> list[ReferenceElement]:
        """
        Get all producer elements to a reference key with given value
        """
        return self._get_elements_by_value(value, ref_key, "producers")

    def get_consumers_by_value(
        self, value: any, ref_key: str
    ) -> list[ReferenceElement]:
        """
        Get all consumer elements to a reference key with given value
        """
        return self._get_elements_by_value(value, ref_key, "consumers")

    def _get_elements_by_value(
        self, value: any, ref_key: str, _list: str
    ) -> list[ReferenceElement]:
        if ref_key not in self.references:
            return []
        return [e for e in self.references[ref_key][_list] if e.value == value]

    def get_uniques_by_ref_key(self, ref_key: str) -> list[ReferenceElement]:
        """
        Get all unique elements to a reference key
        """
        return self.references.get(ref_key, {}).get("uniques", [])

    def get_producers_by_ref_key(self, ref_key: str) -> list[ReferenceElement]:
        """
        Get all producer elements to a reference key
        """
        return self.references.get(ref_key, {}).get("producers", [])

    def get_consumers_by_ref_key(self, ref_key: str) -> list[ReferenceElement]:
        """
        Get all consumer elements to a reference key
        """
        return self.references.get(ref_key, {}).get("consumers", [])

    def get_unique_values_by_ref_key(self, reference_key: str) -> set:
        """
        Returns:
            list - with all 'unique' values with the same reference key
        """
        unique_values = set()
        for i in self.get_uniques_by_ref_key(reference_key):
            unique_values.add(i.value)
        return unique_values

    def _add_ref_key(self, reference_key: str):
        """
        If reference key is new to this space,
        creates all required lists (unique,producers and consumers) for key 'ref_key' in references.

        Args:
            ref_key: string - reference key from schema definition
        """
        if reference_key in self.references:
            return
        self.references[reference_key] = {
            "uniques": [],
            "producers": [],
            "consumers": [],
            "producer_credits": {},
            "consumer_credits": {},
        }

    def _add_unique_element(self, e: ReferenceElement):
        if match := self.get_uniques_by_value(e.value, e.key):
            raise NadapReferenceError(f"Reference already defined at {match[0].path}")
        self.references[e.key]["uniques"].append(e)

    def _add_producing_element(self, e: ReferenceElement) -> list[ReferenceElement]:
        self.references[e.key]["producers"].append(e)
        # Check if value can be used as a key in a dictionary.
        # If not convert to string.
        try:
            hash(e.value)
            value = e.value
        except TypeError:
            value = str(e.value)
        if value in self.references[e.key]["producer_credits"]:
            if e.credits is None:
                # Producer sets credits for this value to infinite (None)
                self.references[e.key]["producer_credits"][value] = None
            elif self.references[e.key]["producer_credits"][value] is not None:
                # Only add credits if not a producer created
                # this value with infinite credits (None)
                self.references[e.key]["producer_credits"][value] += e.credits
        else:
            # New produced value. Just set credits.
            self.references[e.key]["producer_credits"][value] = e.credits
        return self._link_to_consumers(e)

    def _add_consuming_element(self, e: ReferenceElement) -> list[ReferenceElement]:
        self.references[e.key]["consumers"].append(e)
        # Check if value can be used as a key in a dictionary.
        # If not convert to string.
        try:
            hash(e.value)
            value = e.value
        except TypeError:
            value = str(e.value)
        # Defaulting credits to 1.
        new_credits = 1 if e.credits is None else e.credits
        if value in self.references[e.key]["consumer_credits"]:
            # Add credits to existing credits for this value
            self.references[e.key]["consumer_credits"][value] += new_credits
        else:
            # Just set credits for this value
            self.references[e.key]["consumer_credits"][value] = new_credits
        return self._link_to_producers(e)

    def add_element(self, e: ReferenceElement) -> list[ReferenceElement]:
        """
        Add a new reference to the space, if reference options matches the class scope:
        - stores reference according to mode in corresponding lists under the reference key
        - create all links (consumer<>producer) to other references in this space

        Args:
            e: ReferenceElement object - New reference for this space

        Returns:
            list of ReferenceElements - which were linked to the new reference

        Raises:
            NadapReferenceError: If reference already in this space
        """
        self._add_ref_key(e.key)
        if self.uOPT in e.options:
            self._add_unique_element(e)
        if self.pOPT in e.options:
            return self._add_producing_element(e)
        if self.cOPT in e.options:
            return self._add_consuming_element(e)
        return []

    def _link_to_producers(self, consumer: ReferenceElement) -> list[ReferenceElement]:
        producer_list = []
        for producer in self.references[consumer.key]["producers"]:
            if (
                consumer.value == producer.value
                and producer not in consumer.consumes_from
            ):
                # Maybe linking already from another NS or in Global
                consumer.consumes_from.append(producer)
                producer.provides_to.append(consumer)
                producer_list.append(producer)
        return producer_list

    def _link_to_consumers(self, producer: ReferenceElement) -> list[ReferenceElement]:
        consumer_list = []
        for consumer in self.references[producer.key]["consumers"]:
            if (
                producer.value == consumer.value
                and consumer not in producer.provides_to
            ):
                # Maybe linking already from another NS or in Global
                producer.provides_to.append(consumer)
                consumer.consumes_from.append(producer)
                consumer_list.append(consumer)
        return consumer_list

    def get_producer_consumer_issues(self) -> list[ReferenceFinding]:
        """
        Collects and returns
        - all consumer references without a linked provider and
        - all provider references without a linked consumer, if orphan procuders are not allowed,
        as a list of ReferenceFindings

        Returns:
            list of ReferenceFindings
        """
        results = []
        for ref_lists in self.references.values():
            for consumer in ref_lists["consumers"]:
                if len(consumer.consumes_from) == 0:
                    # No producer found during analysis!
                    results.append(
                        ReferenceFinding(
                            path=consumer.path,
                            message="No producer found",
                            reference=consumer,
                        )
                    )
            for producer in ref_lists["producers"]:
                if (
                    OPT.ALLOW_ORPHAN_PRODUCER not in producer.options
                    and len(producer.provides_to) == 0
                ):
                    # Producer has no consumer!
                    results.append(
                        ReferenceFinding(
                            path=producer.path,
                            message="Producer has no consumer",
                            reference=producer,
                        )
                    )
        return results

    def get_credit_issues(self) -> list[ReferenceFinding]:
        """
        Checks if consumer credits exceeds provider credits.

        Returns:
            list of ReferenceFindings
        """
        results = []
        for ref_key, ref_lists in self.references.items():
            for producer_value, producer_credits in ref_lists[
                "producer_credits"
            ].items():
                if producer_credits is not None:
                    consumer_credits = ref_lists["consumer_credits"].get(
                        producer_value, None
                    )
                    if (
                        consumer_credits is not None
                        and consumer_credits > producer_credits
                    ):
                        results.append(
                            ReferenceFinding(
                                path="n.a.",
                                message=f"reference key '{ref_key}': Consumer credits exceeds "
                                + f"producer credits for value '{producer_value}'",
                            )
                        )
        return results


class NameSpace(GlobalSpace):
    """
    Sub-class to GlobalSpace
    Namespace is a space in namespace scope
    """

    uOPT = OPT.UNIQUE
    pOPT = OPT.PRODUCER
    cOPT = OPT.CONSUMER


class References:
    """
    References stores all references according to the current active namespace and
    according to the reference options (mode, scope, ...)
    """

    def __init__(self, namespace: str = "") -> None:
        self.namespace = namespace
        self.globalspace_obj = GlobalSpace()
        self.ns_obj_store = {}
        self._create_namespace(namespace)
        self.namespace_obj = self.ns_obj_store[namespace]

    def change_namespace(self, namespace: str) -> None:
        """
        Change namespace
        """
        self._create_namespace(namespace)
        self.namespace_obj = self.ns_obj_store[namespace]
        self.namespace = namespace

    def _create_namespace(self, namespace: str) -> None:
        if namespace not in self.ns_obj_store:
            self.ns_obj_store[namespace] = NameSpace()

    def add_element(self, reference: ReferenceElement) -> list[ReferenceElement]:
        """
        Add a new reference to the reference store, if reference options matches the class scope:
        - add the reference to global space and
        - if mode is consumer and provider namespace is given (namespace lookup),
          add the reference to provider namespace,
          else add the reference to the current active namespace

        Args:
            reference: ReferenceElement object - New reference for this store

        Returns:
            list of ReferenceElements - which were linked to the new reference

        Raises:
            Cd2tReferenceError: If reference already in this store
        """
        reference.namespace = self.namespace
        linked_elements = self.globalspace_obj.add_element(reference)

        if isinstance(reference, ConsumerElement) and reference.provider_namespace:
            self._create_namespace(reference.provider_namespace)
            linked_elements += self.ns_obj_store[
                reference.provider_namespace
            ].add_element(reference)
        else:
            linked_elements += self.namespace_obj.add_element(reference)
        return linked_elements

    def get_producer_consumer_issues(self):
        """
        Collects and returns
        - all consumer references without a linked provider and
        - all provider references without a linked consumer, if orphan procuders are not allowed,
        from all namespaces as a list of ReferenceFindings.
        Note: As each reference in global space is also in a namespace, globalspace is skipped.

        Returns:
            list of ReferenceFindings
        """
        credit_results = self.globalspace_obj.get_credit_issues()
        for finding in credit_results:
            finding.message = "Global " + finding.message
        results = credit_results

        for namespace, ns_obj in self.ns_obj_store.items():
            results += ns_obj.get_producer_consumer_issues()
            credit_results = ns_obj.get_credit_issues()
            for finding in credit_results:
                finding.message = f"Namespace '{namespace}' {finding.message}"
            results += credit_results

        return results

    def same_unique(self, reference: ReferenceElement) -> list[ReferenceElement]:
        """
        Returns first found 'unique' references with
        the same reference key and value as given reference.

        Args:
            reference: ReferenceElement

        Returns:
            list of ReferenceElements
        """
        others = self.namespace_obj.get_uniques_by_value(reference.value, reference.key)
        if OPT.UNIQUE_GLOBAL in reference.options:
            others += self.globalspace_obj.get_uniques_by_value(
                reference.value, reference.key
            )
        if others:
            return others[0]
        return None

    def get_unique_values_by_ref_key(self, reference_key: str) -> set:
        """
        Returns all found 'unique' values with the same reference key.

        Args:
            reference_key: string

        Returns:
            list of values
        """
        ns_uniques = set(self.namespace_obj.get_unique_values_by_ref_key(reference_key))
        global_unique = set(
            self.globalspace_obj.get_unique_values_by_ref_key(reference_key)
        )
        return ns_uniques.union(global_unique)
