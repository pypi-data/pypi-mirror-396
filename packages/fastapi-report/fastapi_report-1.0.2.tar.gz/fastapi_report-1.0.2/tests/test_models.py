"""
Property-based tests for data models.

Feature: endpoint-reporter, Property 16: JSON Output Validity
Validates: Requirements 4.1
"""
import json
from hypothesis import given, strategies as st
from fastapi_report.models import ParameterInfo, EndpointInfo, MCPToolInfo, APIReport, EnumValue, EnumInfo


# Strategies for generating test data
@st.composite
def enum_value_strategy(draw):
    """Generate random EnumValue instances."""
    return EnumValue(
        name=draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))),
        value=draw(st.one_of(st.integers(), st.text(min_size=1, max_size=50))),
        description=draw(st.one_of(st.none(), st.text(max_size=100)))
    )


@st.composite
def enum_info_strategy(draw):
    """Generate random EnumInfo instances."""
    return EnumInfo(
        class_name=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))),
        module_name=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100))),
        values=draw(st.lists(enum_value_strategy(), min_size=1, max_size=10)),
        enum_type=draw(st.sampled_from(["Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"])),
        description=draw(st.one_of(st.none(), st.text(max_size=200)))
    )


@st.composite
def parameter_info_strategy(draw):
    """Generate random ParameterInfo instances."""
    return ParameterInfo(
        name=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))),
        param_type=draw(st.sampled_from(["query", "path", "body", "header"])),
        python_type=draw(st.sampled_from(["str", "int", "float", "bool", "list", "dict"])),
        required=draw(st.booleans()),
        default=draw(st.one_of(st.none(), st.integers(), st.text(), st.booleans())),
        description=draw(st.one_of(st.none(), st.text(max_size=200))),
        constraints=draw(st.dictionaries(
            st.sampled_from(["ge", "le", "min_length", "max_length", "pattern"]),
            st.one_of(st.integers(), st.text(max_size=50)),
            max_size=3
        )),
        enum_info=draw(st.one_of(st.none(), enum_info_strategy()))
    )


@st.composite
def endpoint_info_strategy(draw):
    """Generate random EndpointInfo instances."""
    return EndpointInfo(
        path=draw(st.text(min_size=1, max_size=100)),
        method=draw(st.sampled_from(["GET", "POST", "PUT", "DELETE", "PATCH"])),
        operation_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
        summary=draw(st.one_of(st.none(), st.text(max_size=100))),
        description=draw(st.one_of(st.none(), st.text(max_size=500))),
        tags=draw(st.lists(st.text(min_size=1, max_size=20), max_size=5)),
        parameters=draw(st.lists(parameter_info_strategy(), max_size=10)),
        request_body=draw(st.one_of(st.none(), st.dictionaries(st.text(), st.text(), max_size=5))),
        responses=draw(st.dictionaries(
            st.integers(min_value=200, max_value=599),
            st.dictionaries(st.text(), st.text(), max_size=3),
            max_size=5
        )),
        deprecated=draw(st.booleans())
    )


@st.composite
def mcp_tool_info_strategy(draw):
    """Generate random MCPToolInfo instances."""
    return MCPToolInfo(
        name=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))),
        description=draw(st.one_of(st.none(), st.text(max_size=200))),
        input_schema=draw(st.dictionaries(st.text(), st.text(), max_size=5)),
        mapped_endpoint=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100)))
    )


@st.composite
def api_report_strategy(draw):
    """Generate random APIReport instances."""
    return APIReport(
        server_name=draw(st.text(min_size=1, max_size=50)),
        server_version=draw(st.text(min_size=1, max_size=20)),
        endpoints=draw(st.lists(endpoint_info_strategy(), max_size=10)),
        mcp_tools=draw(st.lists(mcp_tool_info_strategy(), max_size=10)),
        openapi_spec=draw(st.dictionaries(st.text(), st.text(), max_size=10))
    )


# Property tests
@given(parameter_info_strategy())
def test_parameter_info_serialization(param: ParameterInfo):
    """
    Feature: endpoint-reporter, Property 16: JSON Output Validity
    For any ParameterInfo, serialization to dict and then to JSON should produce valid JSON.
    """
    param_dict = param.to_dict()
    json_str = json.dumps(param_dict)
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)
    assert parsed["name"] == param.name
    assert parsed["param_type"] == param.param_type


@given(endpoint_info_strategy())
def test_endpoint_info_serialization(endpoint: EndpointInfo):
    """
    Feature: endpoint-reporter, Property 16: JSON Output Validity
    For any EndpointInfo, serialization to dict and then to JSON should produce valid JSON.
    """
    endpoint_dict = endpoint.to_dict()
    json_str = json.dumps(endpoint_dict)
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)
    assert parsed["path"] == endpoint.path
    assert parsed["method"] == endpoint.method
    assert len(parsed["parameters"]) == len(endpoint.parameters)


@given(mcp_tool_info_strategy())
def test_mcp_tool_info_serialization(tool: MCPToolInfo):
    """
    Feature: endpoint-reporter, Property 16: JSON Output Validity
    For any MCPToolInfo, serialization to dict and then to JSON should produce valid JSON.
    """
    tool_dict = tool.to_dict()
    json_str = json.dumps(tool_dict)
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)
    assert parsed["name"] == tool.name


@given(api_report_strategy())
def test_api_report_serialization(report: APIReport):
    """
    Feature: endpoint-reporter, Property 16: JSON Output Validity
    For any APIReport, serialization to dict and then to JSON should produce valid, parseable JSON.
    """
    report_dict = report.to_dict()
    json_str = json.dumps(report_dict)
    parsed = json.loads(json_str)
    
    assert isinstance(parsed, dict)
    assert parsed["server_name"] == report.server_name
    assert parsed["server_version"] == report.server_version
    assert len(parsed["endpoints"]) == len(report.endpoints)
    assert len(parsed["mcp_tools"]) == len(report.mcp_tools)
    assert "generated_at" in parsed


@given(enum_value_strategy())
def test_enum_value_serialization(enum_value: EnumValue):
    """
    Feature: enhanced-enum-support, Property 4: Universal Enum Type Support
    For any EnumValue, serialization to dict and then to JSON should produce valid JSON.
    """
    value_dict = enum_value.to_dict()
    json_str = json.dumps(value_dict)
    parsed = json.loads(json_str)
    
    assert isinstance(parsed, dict)
    assert parsed["name"] == enum_value.name
    assert parsed["value"] == enum_value.value
    assert parsed.get("description") == enum_value.description


@given(enum_info_strategy())
def test_enum_info_serialization(enum_info: EnumInfo):
    """
    Feature: enhanced-enum-support, Property 4: Universal Enum Type Support
    For any EnumInfo, serialization to dict and then to JSON should produce valid JSON.
    """
    info_dict = enum_info.to_dict()
    json_str = json.dumps(info_dict)
    parsed = json.loads(json_str)
    
    assert isinstance(parsed, dict)
    assert parsed["class_name"] == enum_info.class_name
    assert parsed["enum_type"] == enum_info.enum_type
    assert len(parsed["values"]) == len(enum_info.values)
    assert parsed.get("module_name") == enum_info.module_name
    assert parsed.get("description") == enum_info.description


@given(parameter_info_strategy())
def test_parameter_info_with_enum_serialization(param: ParameterInfo):
    """
    Feature: enhanced-enum-support, Property 4: Universal Enum Type Support
    For any ParameterInfo with enum_info, serialization should preserve enum metadata.
    """
    param_dict = param.to_dict()
    json_str = json.dumps(param_dict)
    parsed = json.loads(json_str)
    
    assert isinstance(parsed, dict)
    assert parsed["name"] == param.name
    
    # Check enum_info serialization
    if param.enum_info is not None:
        assert "enum_info" in parsed
        enum_data = parsed["enum_info"]
        assert enum_data["class_name"] == param.enum_info.class_name
        assert len(enum_data["values"]) == len(param.enum_info.values)
    else:
        # enum_info should be None or not present
        assert parsed.get("enum_info") is None
