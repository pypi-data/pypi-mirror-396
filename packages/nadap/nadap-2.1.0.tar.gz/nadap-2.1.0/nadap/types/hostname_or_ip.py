"""
Hostname or IP address data type class
"""

# pylint: disable=too-few-public-methods

import nadap.types.base
import nadap.types.hostname
import nadap.types.ip_address
import nadap.types.ip4_address
import nadap.types.ip6_address
import nadap.results
import nadap.schema
from nadap.base import ValEnv
from nadap.errors import DataValidationError, SchemaDefinitionError
from nadap.doc import UnorderedTextList, TextField


DOC_DT_NAME = "Hostname or IP Adress "
DOC_DT_DESCRIPTION = """
A **hostname_or_ip** data type tests data for being an instance of
python's built-in class `str` and if it represents a hostname/FQDN
or an IPv4/IPv6 address.
"""
DOC_DT_FEATURES = (
    """
Hostname Features:
"""
    + nadap.types.hostname.DOC_DT_FEATURES
    + """
IP Address Features:
"""
    + nadap.types.ip_address.DOC_DT_FEATURES
)
DOC_DT_YAML_EXAMPLE = r"""
type: hostname_or_ip
description: "Example hostname_or_ip definition"
default_value: "my-host"

hostname:
    minimum: 3
    maximum: 16
    minimum_labels: 3
    maximum_labels: 7

    not_allowed_values:
    - nadap-.*
    relax_length: false

ip:
    version: 4
    multicast: False
    private: True

    not_allowed_values:
    - 10.10.99.1
    - 192.168.0.1

reference: ref_key
"""


class HostnameOrIP(nadap.types.base.BaseType):
    """
    Hostname or IP Address datatype class
    """

    data_type_name = "hostname_or_ip"
    _cls_python_classes = [str]
    _convert_to_classes = {}
    _support_replace_empty_to = True
    _doc_data_type = "str"

    def __init__(self, **kwargs):
        self._ip_definition = {}
        self._ip_version = None
        self._hostname_definition = {}
        self._ip_dt_obj = None
        self._hostname_dt_obj = None
        super().__init__(**kwargs)

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)
        ip_path = f"{schema_path}.ip"
        nadap.schema.is_dict(self._ip_definition, ip_path)
        self._ip_version = self._ip_definition.pop("version", None)
        if self._ip_version:
            nadap.schema.is_int(self._ip_version, f"{ip_path}.version")
            if self._ip_version not in [4, 6]:
                raise SchemaDefinitionError(
                    msg="Must be either 4 or 6", path=f"{ip_path}.version"
                )
            if self._ip_version == 4:
                ip_dt_class = nadap.types.ip4_address.Ip4Address
            else:
                ip_dt_class = nadap.types.ip6_address.Ip6Address
        else:
            ip_dt_class = nadap.types.ip_address.IpAddress
        self._ip_dt_obj = ip_dt_class(
            schema=self._schema,
            definition=self._ip_definition,
            schema_path=ip_path,
        )
        self._hostname_dt_obj = nadap.types.hostname.Hostname(
            schema=self._schema,
            definition=self._hostname_definition,
            schema_path=f"{schema_path}.hostname",
        )

    def _pop_options(self, definition: dict, schema_path: str):
        ref_definition = definition.get("reference", {})
        ref_definitions = definition.get("references", {})
        self._ip_definition = definition.pop("ip", self._ip_definition)
        self._hostname_definition = definition.pop(
            "hostname", self._hostname_definition
        )
        if ref_definition:
            self._ip_definition["reference"] = ref_definition
            self._hostname_definition["reference"] = ref_definition
        if ref_definitions:
            self._ip_definition["references"] = ref_definitions
            self._hostname_definition["references"] = ref_definitions
        super()._pop_options(definition, schema_path)

    def validate(
        self,
        data: any,
        path: str,
        env: "ValEnv",
    ) -> "any":
        """
        - Check if data matches IP Data type
        - If fails, check if data matches Hostname Data Type
        - apply preprocessing and perform referencing
        """
        self._test_data_type(data=data, path=path, env=env)
        len_findings = len(env.findings)
        try:
            data = self._ip_dt_obj.validate(data=data, path=path, env=env)
        except DataValidationError:
            try:
                data = self._hostname_dt_obj.validate(data=data, path=path, env=env)
                if len_findings < len(env.findings):
                    del env.findings[len_findings - len(env.findings) :]
            except DataValidationError:
                env.findings.insert(
                    len_findings,
                    nadap.results.ValidationFinding(
                        message="Data matches wether defined hostname nor defined IP address",
                        path=path,
                    ),
                )
                raise DataValidationError()  # pylint: disable=raise-missing-from
        return data

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        ip_restrictions = self._ip_dt_obj.restrictions
        hostname_restrictions = self._hostname_dt_obj.restrictions
        tf = TextField()
        if self._ip_version or ip_restrictions:
            tf.append("IP Address Restrictions:")
            ip_r = UnorderedTextList()
            if self._ip_version:
                ip_r.append(f"IP Version: {self._ip_version}")
            ip_r.extend(list(ip_restrictions.t))
            tf.append(ip_r)
        if hostname_restrictions:
            tf.append("Hostname Restrictions:")
            tf.append(UnorderedTextList(list(hostname_restrictions.t)))
        return tf

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **hostname** | <code>dict</code> | | | Hostname data type definition part |",
            "| &nbsp;&nbsp;**minimum** | <code>int</code> | | min: 1 | Data's length must be "
            + "greater or equal |",
            "| &nbsp;&nbsp;**maximum** | <code>int</code> | | min: 1<br>>= 'minimum' | Data's "
            + "length must be lower or equal |",
            "| &nbsp;&nbsp;**replace_empty_to** | <code>any</code> | | |  An empty input value "
            + "will be replaced by this data |",
            "| &nbsp;&nbsp;**relax_length** | <code>bool</code> | <code>True</code> | "
            + "| Relax hostname length "
            + "from 63 to 255 characters |",
            "| &nbsp;&nbsp;**minimum_labels** | <code>int</code> | | min: 1 | Minimum amount of "
            + "labels within in hostname |",
            "| &nbsp;&nbsp;**maximum_labels** | <code>int</code> | | min: 1<br>>= 'minimum_labels' "
            + "| Maximum amount of labels within in hostname |",
            "| &nbsp;&nbsp;**allowed_values** | <code>list[str]</code> | | |  Data must match one "
            + "of these regex patterns |",
            "| &nbsp;&nbsp;&nbsp;&nbsp;- < str > | <code>str</code> | | | |",
            "| &nbsp;&nbsp;**not_allowed_values** | <code>list[str]</code> | | |  Data mustn't "
            + "match any of these regex patterns |",
            "| &nbsp;&nbsp;&nbsp;&nbsp;- < str > | <code>str</code> | | | |",
            "| **ip** | <code>dict</code> | | | IP address data type definition part |",
            "| **allowed_ranges** | <code>list[dict]</code> | | min length: 1 | "
            + "Value must be within defined ranges |",
            f"| {cls._markdown_indent}- **start** | <code>str</code> | | required |",
            f"| {cls._markdown_indent * 2}**end** | <code>str</code> | | required |",
            "| **not_allowed_ranges** | <code>list[dict]</code> | | "
            + "| Value mustn't be within defined ranges |",
            f"| {cls._markdown_indent}- **start** | <code>str</code> | | required |",
            f"| {cls._markdown_indent * 2}**end** | <code>str</code> | | required |",
            "| &nbsp;&nbsp;**allowed_values** | <code>list</code> | | |  Data must match one of "
            + "these values |",
            "| &nbsp;&nbsp;&nbsp;&nbsp;- < value > | <code>any</code> | "
            + "| Must match data type's type(s) | |",
            "| &nbsp;&nbsp;**not_allowed_values** | <code>list</code> | "
            + "| |  Data mustn't match all of these "
            + "values |",
            "| &nbsp;&nbsp;&nbsp;&nbsp;- < value > | <code>any</code> | "
            + "| Must match data type's type(s) | |",
            "| &nbsp;&nbsp;**link_local** | <code>bool</code> | | | IP must be link-local |",
            "| &nbsp;&nbsp;**loopback** | <code>bool</code> | | | IP must be loopback |",
            "| &nbsp;&nbsp;**multicast** | <code>bool</code> | | | IP must be multicast |",
            "| &nbsp;&nbsp;**private** | <code>bool</code> | | | IP must be private |",
            "| &nbsp;&nbsp;**public** | <code>bool</code> | | | IP must be public/global |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "ip:",
            "  convert_to: <str>",
            "  allowed_ranges:",
            "    - start: <str>",
            "      end: <str>",
            "  not_allowed_ranges:",
            "   - start: <str>",
            "     end: <str>",
            "  allowed_values:",
            "  - <any>",
            "  not_allowed_values:",
            "  - <any>",
            "  link_local: <true|false",
            "  loopback: <true|false",
            "  multicast: <true|false",
            "  private: <true|false",
            "  public: <true|false",
            "hostname:",
            "  version: <int>",
            "  maximum: <int>",
            "  minimum: <int>",
            "  replace_empty_to: <any>",
            "  relax_length: <true|false>",
            "  minimum_labels: <int>",
            "  maximum_labels: <int>",
            "  allowed_values:",
            "  - <str>",
            "  not_allowed_values:",
            "  - <str>",
        ]


DOC_DT_CLASS = HostnameOrIP  # pylint: disable=invalid-name
