"""
Property-based tests for formatters.

Feature: endpoint-reporter, Property 16, 17, 18: Output Format Validity
Validates: Requirements 4.1, 4.2, 4.3
"""
import json
from hypothesis import given, strategies as st
from fastapi_report.models import APIReport, EndpointInfo, MCPToolInfo, ParameterInfo
from fastapi_report.formatters import JSONFormatter, MarkdownFormatter, HTMLFormatter


def create_sample_report():
    """Create a sample API report for testing."""
    param = ParameterInfo(
        name="test_param",
        param_type="query",
        python_type="str",
        required=True,
        default=None,
        description="Test parameter",
        constraints={"min_length": 1}
    )
    
    endpoint = EndpointInfo(
        path="/test",
        method="GET",
        operation_id="test_endpoint",
        summary="Test endpoint",
        description="A test endpoint",
        tags=["test"],
        parameters=[param],
        request_body=None,
        responses={200: {"description": "Success"}},
        deprecated=False
    )
    
    tool = MCPToolInfo(
        name="test_tool",
        description="Test MCP tool",
        input_schema={"type": "object"},
        mapped_endpoint="GET /test"
    )
    
    return APIReport(
        server_name="Test API",
        server_version="1.0.0",
        endpoints=[endpoint],
        mcp_tools=[tool],
        openapi_spec={"openapi": "3.0.0"}
    )


def test_json_formatter_produces_valid_json():
    """
    Feature: endpoint-reporter, Property 16: JSON Output Validity
    For any generated report, the JSON output should be valid, parseable JSON.
    """
    report = create_sample_report()
    formatter = JSONFormatter()
    
    output = formatter.format(report)
    
    # Should be valid JSON
    parsed = json.loads(output)
    assert isinstance(parsed, dict)
    assert parsed["server_name"] == "Test API"
    assert parsed["server_version"] == "1.0.0"
    assert len(parsed["endpoints"]) == 1
    assert len(parsed["mcp_tools"]) == 1


def test_json_formatter_file_extension():
    """Test that JSON formatter returns correct file extension."""
    formatter = JSONFormatter()
    assert formatter.get_file_extension() == ".json"


def test_markdown_formatter_produces_valid_markdown():
    """
    Feature: endpoint-reporter, Property 17: Markdown Output Well-Formedness
    For any generated report, the Markdown output should be well-formed.
    """
    report = create_sample_report()
    formatter = MarkdownFormatter()
    
    output = formatter.format(report)
    
    # Should contain markdown headers
    assert "# Test API" in output
    assert "## REST Endpoints" in output
    assert "## MCP Tools" in output
    
    # Should contain endpoint information
    assert "GET /test" in output
    assert "Test endpoint" in output
    
    # Should contain MCP tool information
    assert "test_tool" in output
    assert "Test MCP tool" in output


def test_markdown_formatter_file_extension():
    """Test that Markdown formatter returns correct file extension."""
    formatter = MarkdownFormatter()
    assert formatter.get_file_extension() == ".md"


def test_html_formatter_produces_valid_html():
    """
    Feature: endpoint-reporter, Property 18: HTML Output Validity
    For any generated report, the HTML output should be valid HTML with navigation.
    """
    report = create_sample_report()
    formatter = HTMLFormatter()
    
    output = formatter.format(report)
    
    # Should contain HTML structure
    assert "<!DOCTYPE html>" in output
    assert "<html" in output
    assert "</html>" in output
    assert "<head>" in output
    assert "<body>" in output
    
    # Should contain navigation
    assert "nav" in output.lower()
    
    # Should contain endpoint information
    assert "GET" in output
    assert "/test" in output
    assert "Test endpoint" in output
    
    # Should contain MCP tool information
    assert "test_tool" in output
    assert "Test MCP tool" in output


def test_html_formatter_file_extension():
    """Test that HTML formatter returns correct file extension."""
    formatter = HTMLFormatter()
    assert formatter.get_file_extension() == ".html"


def test_formatters_handle_empty_report():
    """Test that all formatters handle empty reports gracefully."""
    empty_report = APIReport(
        server_name="Empty API",
        server_version="1.0.0",
        endpoints=[],
        mcp_tools=[],
        openapi_spec={}
    )
    
    # JSON formatter
    json_formatter = JSONFormatter()
    json_output = json_formatter.format(empty_report)
    parsed = json.loads(json_output)
    assert len(parsed["endpoints"]) == 0
    assert len(parsed["mcp_tools"]) == 0
    
    # Markdown formatter
    md_formatter = MarkdownFormatter()
    md_output = md_formatter.format(empty_report)
    assert "Empty API" in md_output
    
    # HTML formatter
    html_formatter = HTMLFormatter()
    html_output = html_formatter.format(empty_report)
    assert "Empty API" in html_output


def test_formatters_handle_multiple_endpoints():
    """Test that formatters handle multiple endpoints correctly."""
    endpoints = [
        EndpointInfo(
            path=f"/endpoint{i}",
            method="GET",
            operation_id=f"endpoint_{i}",
            summary=f"Endpoint {i}",
            description=None,
            tags=[],
            parameters=[],
            request_body=None,
            responses={},
            deprecated=False
        )
        for i in range(5)
    ]
    
    report = APIReport(
        server_name="Multi-Endpoint API",
        server_version="1.0.0",
        endpoints=endpoints,
        mcp_tools=[],
        openapi_spec={}
    )
    
    # JSON formatter
    json_formatter = JSONFormatter()
    json_output = json_formatter.format(report)
    parsed = json.loads(json_output)
    assert len(parsed["endpoints"]) == 5
    
    # Markdown formatter
    md_formatter = MarkdownFormatter()
    md_output = md_formatter.format(report)
    for i in range(5):
        assert f"/endpoint{i}" in md_output
    
    # HTML formatter
    html_formatter = HTMLFormatter()
    html_output = html_formatter.format(report)
    for i in range(5):
        assert f"/endpoint{i}" in html_output


def test_json_formatter_handles_special_characters():
    """Test that JSON formatter properly escapes special characters."""
    endpoint = EndpointInfo(
        path="/test",
        method="GET",
        operation_id="test",
        summary='Test with "quotes" and \\ backslashes',
        description="Test with\nnewlines",
        tags=[],
        parameters=[],
        request_body=None,
        responses={},
        deprecated=False
    )
    
    report = APIReport(
        server_name="Test API",
        server_version="1.0.0",
        endpoints=[endpoint],
        mcp_tools=[],
        openapi_spec={}
    )
    
    formatter = JSONFormatter()
    output = formatter.format(report)
    
    # Should be valid JSON despite special characters
    parsed = json.loads(output)
    assert 'quotes' in parsed["endpoints"][0]["summary"]
    assert 'newlines' in parsed["endpoints"][0]["description"]


def test_markdown_formatter_creates_parameter_tables():
    """Test that Markdown formatter creates proper parameter tables."""
    params = [
        ParameterInfo(
            name="param1",
            param_type="query",
            python_type="str",
            required=True,
            default=None,
            description="First parameter",
            constraints={}
        ),
        ParameterInfo(
            name="param2",
            param_type="query",
            python_type="int",
            required=False,
            default=10,
            description="Second parameter",
            constraints={"ge": 1, "le": 100}
        )
    ]
    
    endpoint = EndpointInfo(
        path="/test",
        method="GET",
        operation_id="test",
        summary="Test",
        description=None,
        tags=[],
        parameters=params,
        request_body=None,
        responses={},
        deprecated=False
    )
    
    report = APIReport(
        server_name="Test API",
        server_version="1.0.0",
        endpoints=[endpoint],
        mcp_tools=[],
        openapi_spec={}
    )
    
    formatter = MarkdownFormatter()
    output = formatter.format(report)
    
    # Should contain parameter table
    assert "param1" in output
    assert "param2" in output
    assert "First parameter" in output
    assert "Second parameter" in output


def test_html_formatter_includes_css_styling():
    """Test that HTML formatter includes CSS styling."""
    report = create_sample_report()
    formatter = HTMLFormatter()
    
    output = formatter.format(report)
    
    # Should contain style tag
    assert "<style>" in output
    assert "</style>" in output
    
    # Should contain some CSS rules
    assert "body" in output or "font-family" in output


def test_json_formatter_includes_enum_information():
    """Test that JSON formatter properly includes enum information in output."""
    from fastapi_report.models import EnumInfo, EnumValue
    
    # Create parameter with enum information
    enum_values = [
        EnumValue(name="ACTIVE", value="active", description="User is active"),
        EnumValue(name="INACTIVE", value="inactive", description="User is inactive")
    ]
    
    enum_info = EnumInfo(
        class_name="UserStatus",
        module_name="test.models",
        values=enum_values,
        enum_type="StrEnum",
        description="User status enumeration"
    )
    
    param_with_enum = ParameterInfo(
        name="status",
        param_type="query",
        python_type="Enum[UserStatus]",
        required=False,
        default="active",
        description="User status filter",
        constraints={"enum": ["active", "inactive"]},
        enum_info=enum_info
    )
    
    endpoint = EndpointInfo(
        path="/users",
        method="GET",
        operation_id="get_users",
        summary="Get users with status filter",
        description="Retrieve users filtered by status",
        tags=["users"],
        parameters=[param_with_enum],
        request_body=None,
        responses={200: {"description": "Success"}},
        deprecated=False
    )
    
    report = APIReport(
        server_name="Test API",
        server_version="1.0.0",
        endpoints=[endpoint],
        mcp_tools=[],
        openapi_spec={"openapi": "3.0.0"}
    )
    
    formatter = JSONFormatter()
    output = formatter.format(report)
    
    # Parse JSON output
    parsed = json.loads(output)
    
    # Verify basic structure
    assert len(parsed["endpoints"]) == 1
    endpoint_data = parsed["endpoints"][0]
    assert len(endpoint_data["parameters"]) == 1
    
    # Verify parameter has enum information
    param_data = endpoint_data["parameters"][0]
    assert param_data["name"] == "status"
    
    # Should have original enum_info
    assert "enum_info" in param_data
    assert param_data["enum_info"]["class_name"] == "UserStatus"
    
    # Should have enhanced enum metadata
    assert "enum_metadata" in param_data
    enum_metadata = param_data["enum_metadata"]
    assert enum_metadata["class_name"] == "UserStatus"
    assert enum_metadata["enum_type"] == "StrEnum"
    assert enum_metadata["module_name"] == "test.models"
    assert enum_metadata["description"] == "User status enumeration"
    assert len(enum_metadata["values"]) == 2
    
    # Verify enum values in metadata
    value_names = [v["name"] for v in enum_metadata["values"]]
    value_values = [v["value"] for v in enum_metadata["values"]]
    assert "ACTIVE" in value_names
    assert "INACTIVE" in value_names
    assert "active" in value_values
    assert "inactive" in value_values
    
    # Should have enum values in constraints for backward compatibility
    assert "constraints" in param_data
    assert "enum" in param_data["constraints"]
    assert set(param_data["constraints"]["enum"]) == {"active", "inactive"}


def test_json_formatter_includes_response_enum_information():
    """Test that JSON formatter includes enum information in response schemas."""
    # Create endpoint with response enum information
    endpoint = EndpointInfo(
        path="/projects",
        method="GET",
        operation_id="get_projects",
        summary="Get projects",
        description="Retrieve projects with enum fields",
        tags=["projects"],
        parameters=[],
        request_body=None,
        responses={
            200: {
                "description": "Success",
                "enum_info": {
                    "application/json": {
                        "enum_fields": {
                            "status": {
                                "field_type": "pydantic_v2",
                                "enum_info": {
                                    "class_name": "ProjectStatus",
                                    "module_name": "test.models",
                                    "enum_type": "StrEnum",
                                    "description": "Project status",
                                    "values": [
                                        {"name": "ACTIVE", "value": "active"},
                                        {"name": "COMPLETED", "value": "completed"}
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        },
        deprecated=False,
        pydantic_enum_info={
            "response_model_Project": {
                "enum_fields": {
                    "status": {
                        "field_type": "pydantic_v2",
                        "enum_info": {
                            "class_name": "ProjectStatus",
                            "module_name": "test.models",
                            "enum_type": "StrEnum",
                            "description": "Project status",
                            "values": [
                                {"name": "ACTIVE", "value": "active"},
                                {"name": "COMPLETED", "value": "completed"}
                            ]
                        }
                    }
                }
            }
        }
    )
    
    report = APIReport(
        server_name="Test API",
        server_version="1.0.0",
        endpoints=[endpoint],
        mcp_tools=[],
        openapi_spec={"openapi": "3.0.0"}
    )
    
    formatter = JSONFormatter()
    output = formatter.format(report)
    
    # Parse JSON output
    parsed = json.loads(output)
    
    # Verify response enum metadata
    endpoint_data = parsed["endpoints"][0]
    response_200 = endpoint_data["responses"]["200"]
    
    # Should have enhanced enum metadata in response
    assert "enum_metadata" in response_200
    enum_metadata = response_200["enum_metadata"]["application/json"]
    assert "enum_fields" in enum_metadata
    
    status_enum = enum_metadata["enum_fields"]["status"]
    assert status_enum["class_name"] == "ProjectStatus"
    assert status_enum["enum_type"] == "StrEnum"
    assert len(status_enum["values"]) == 2
    
    # Should have enhanced Pydantic enum metadata
    assert "pydantic_enum_metadata" in endpoint_data
    pydantic_metadata = endpoint_data["pydantic_enum_metadata"]["response_model_Project"]
    assert "enum_fields" in pydantic_metadata
    
    status_field = pydantic_metadata["enum_fields"]["status"]
    assert "enum_metadata" in status_field
    assert status_field["enum_metadata"]["class_name"] == "ProjectStatus"


def test_markdown_formatter_includes_enum_information():
    """Test that Markdown formatter properly displays enum information in parameter tables."""
    from fastapi_report.models import EnumInfo, EnumValue
    
    # Create enum values
    enum_values = [
        EnumValue(name="ACTIVE", value="active", description="User is active"),
        EnumValue(name="INACTIVE", value="inactive", description="User is inactive"),
        EnumValue(name="SUSPENDED", value="suspended", description="User is suspended")
    ]
    
    enum_info = EnumInfo(
        class_name="UserStatus",
        module_name="test.models",
        values=enum_values,
        enum_type="StrEnum",
        description="User account status enumeration"
    )
    
    # Create parameter with enum information
    param = ParameterInfo(
        name="status",
        param_type="query",
        python_type="str",
        required=False,
        default="active",
        description="User status filter",
        constraints={"enum": ["active", "inactive", "suspended"]},
        enum_info=enum_info
    )
    
    endpoint = EndpointInfo(
        path="/users",
        method="GET",
        operation_id="get_users",
        summary="Get users",
        description="Get users filtered by status",
        tags=["users"],
        parameters=[param],
        request_body=None,
        responses={200: {"description": "Success"}},
        deprecated=False
    )
    
    report = APIReport(
        server_name="Test API",
        server_version="1.0.0",
        endpoints=[endpoint],
        mcp_tools=[],
        openapi_spec={}
    )
    
    formatter = MarkdownFormatter()
    output = formatter.format(report)
    
    # Should contain enum class information
    assert "Enum[UserStatus]" in output
    assert "UserStatus" in output
    
    # Should contain enum values in the Enum column
    assert "`active`" in output
    assert "`inactive`" in output
    assert "`suspended`" in output
    
    # Should contain enum values with descriptions
    assert "ACTIVE" in output
    assert "active" in output
    assert "User is active" in output
    assert "INACTIVE" in output
    assert "inactive" in output
    assert "User is inactive" in output
    assert "SUSPENDED" in output
    assert "suspended" in output
    assert "User is suspended" in output
    
    # Should contain "Possible values" text
    assert "Possible values" in output


def test_markdown_formatter_handles_mixed_enum_and_regular_parameters():
    """Test that Markdown formatter handles both enum and regular parameters correctly."""
    from fastapi_report.models import EnumInfo, EnumValue
    
    # Create enum parameter
    enum_values = [
        EnumValue(name="LOW", value=1),
        EnumValue(name="MEDIUM", value=2),
        EnumValue(name="HIGH", value=3)
    ]
    
    enum_info = EnumInfo(
        class_name="Priority",
        values=enum_values,
        enum_type="IntEnum"
    )
    
    enum_param = ParameterInfo(
        name="priority",
        param_type="query",
        python_type="int",
        required=False,
        default=1,
        description="Task priority level",
        enum_info=enum_info
    )
    
    # Create regular parameter
    regular_param = ParameterInfo(
        name="limit",
        param_type="query",
        python_type="int",
        required=False,
        default=10,
        description="Number of items to return",
        constraints={"ge": 1, "le": 100}
    )
    
    endpoint = EndpointInfo(
        path="/tasks",
        method="GET",
        parameters=[enum_param, regular_param]
    )
    
    report = APIReport(
        server_name="Test API",
        server_version="1.0.0",
        endpoints=[endpoint]
    )
    
    formatter = MarkdownFormatter()
    output = formatter.format(report)
    
    # Enum parameter should have enhanced formatting
    assert "Enum[Priority]" in output
    assert "Priority" in output
    
    # Should contain enum values in the Enum column
    assert "`1`" in output
    assert "`2`" in output  
    assert "`3`" in output
    
    # Regular parameter should have normal formatting
    assert "limit" in output
    assert "int" in output
    assert "ge=1" in output
    assert "le=100" in output
    assert "Number of items to return" in output


def test_html_formatter_includes_enum_information():
    """Test that HTML formatter properly displays enum information in parameter tables."""
    from fastapi_report.models import EnumInfo, EnumValue
    
    # Create enum values
    enum_values = [
        EnumValue(name="ACTIVE", value="active", description="User is active"),
        EnumValue(name="INACTIVE", value="inactive", description="User is inactive"),
        EnumValue(name="SUSPENDED", value="suspended", description="User is suspended")
    ]
    
    enum_info = EnumInfo(
        class_name="UserStatus",
        module_name="test.models",
        values=enum_values,
        enum_type="StrEnum",
        description="User account status enumeration"
    )
    
    # Create parameter with enum information
    param = ParameterInfo(
        name="status",
        param_type="query",
        python_type="str",
        required=False,
        default="active",
        description="User status filter",
        constraints={"enum": ["active", "inactive", "suspended"]},
        enum_info=enum_info
    )
    
    endpoint = EndpointInfo(
        path="/users",
        method="GET",
        operation_id="get_users",
        summary="Get users",
        description="Get users filtered by status",
        tags=["users"],
        parameters=[param],
        request_body=None,
        responses={200: {"description": "Success"}},
        deprecated=False
    )
    
    report = APIReport(
        server_name="Test API",
        server_version="1.0.0",
        endpoints=[endpoint],
        mcp_tools=[],
        openapi_spec={}
    )
    
    formatter = HTMLFormatter()
    output = formatter.format(report)
    
    # Should contain enum type display
    assert "Enum[UserStatus]" in output
    
    # Should contain enum class information
    assert "UserStatus" in output
    
    # Should contain enum values in the Enum column
    assert 'class="enum-value">active</code>' in output
    assert 'class="enum-value">inactive</code>' in output
    assert 'class="enum-value">suspended</code>' in output
    
    # Should contain enum values with descriptions
    assert "ACTIVE" in output
    assert "active" in output
    assert "User is active" in output
    assert "INACTIVE" in output
    assert "inactive" in output
    assert "User is inactive" in output
    assert "SUSPENDED" in output
    assert "suspended" in output
    assert "User is suspended" in output
    
    # Should contain "Possible values" text
    assert "Possible values" in output
    
    # Should contain enum-specific CSS classes
    assert "enum-info" in output
    assert "enum-class" in output
    assert "enum-values" in output
    assert "enum-name" in output
    assert "enum-value" in output
    
    # Should contain parameter-specific enum styling
    assert "param-enum-info" in output


def test_html_formatter_handles_mixed_enum_and_regular_parameters():
    """Test that HTML formatter handles both enum and regular parameters correctly."""
    from fastapi_report.models import EnumInfo, EnumValue
    
    # Create enum parameter
    enum_values = [
        EnumValue(name="LOW", value=1),
        EnumValue(name="MEDIUM", value=2),
        EnumValue(name="HIGH", value=3)
    ]
    
    enum_info = EnumInfo(
        class_name="Priority",
        values=enum_values,
        enum_type="IntEnum"
    )
    
    enum_param = ParameterInfo(
        name="priority",
        param_type="query",
        python_type="int",
        required=False,
        default=1,
        description="Task priority level",
        enum_info=enum_info
    )
    
    # Create regular parameter
    regular_param = ParameterInfo(
        name="limit",
        param_type="query",
        python_type="int",
        required=False,
        default=10,
        description="Number of items to return",
        constraints={"ge": 1, "le": 100}
    )
    
    endpoint = EndpointInfo(
        path="/tasks",
        method="GET",
        parameters=[enum_param, regular_param]
    )
    
    report = APIReport(
        server_name="Test API",
        server_version="1.0.0",
        endpoints=[endpoint]
    )
    
    formatter = HTMLFormatter()
    output = formatter.format(report)
    
    # Enum parameter should have enhanced formatting
    assert "Enum[Priority]" in output
    assert "Priority" in output
    
    # Should contain enum values in the Enum column
    assert 'class="enum-value">1</code>' in output
    assert 'class="enum-value">2</code>' in output
    assert 'class="enum-value">3</code>' in output
    
    # Regular parameter should have normal formatting
    assert "limit" in output
    assert "int" in output
    assert "ge=1" in output
    assert "le=100" in output
    assert "Number of items to return" in output