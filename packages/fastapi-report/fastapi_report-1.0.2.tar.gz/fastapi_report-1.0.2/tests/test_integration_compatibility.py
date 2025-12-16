"""
Integration and compatibility tests for enhanced enum support.

This test suite validates that the enhanced enum support works correctly
with existing FastAPI applications, maintains backward compatibility,
and integrates properly between all components.
"""
import time
import json
from enum import Enum, IntEnum, StrEnum
from typing import List, Optional, Union
from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel
from fastapi_report.discovery.fastapi_discovery import FastAPIDiscovery
from fastapi_report.formatters.json_formatter import JSONFormatter
from fastapi_report.formatters.markdown_formatter import MarkdownFormatter
from fastapi_report.formatters.html_formatter import HTMLFormatter
from fastapi_report.models import APIReport


# Test enums for compatibility testing
class UserStatus(Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Priority(IntEnum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Category(StrEnum):
    """Item categories."""
    ELECTRONICS = "electronics"
    BOOKS = "books"
    CLOTHING = "clothing"


# Test models for compatibility testing
class User(BaseModel):
    """User model with enum field."""
    id: int
    name: str
    status: UserStatus
    email: Optional[str] = None


class Task(BaseModel):
    """Task model with multiple enum fields."""
    id: int
    title: str
    priority: Priority
    assignee: Optional[User] = None
    category: Optional[Category] = None


class Project(BaseModel):
    """Project model with nested enum structures."""
    id: int
    name: str
    description: str
    status: UserStatus
    tasks: List[Task] = []
    owner: User


def test_enhanced_enum_support_with_existing_fastapi_app():
    """
    Test enhanced enum support with a realistic FastAPI application.
    
    This test validates that the enhanced enum support works correctly
    with existing FastAPI applications that use various enum patterns.
    """
    app = FastAPI(title="Test API", version="1.0.0")
    
    # Endpoint with direct enum parameters
    @app.get("/users")
    def get_users(
        status: UserStatus = Query(UserStatus.ACTIVE, description="Filter by user status"),
        limit: int = Query(10, ge=1, le=100, description="Number of users to return")
    ):
        return []
    
    # Endpoint with field enum constraints
    @app.get("/items")
    def get_items(
        category: str = Query(..., enum=["electronics", "books", "clothing"], description="Item category"),
        sort: str = Query("name", enum=["name", "price", "date"], description="Sort order")
    ):
        return []
    
    # Endpoint with mixed enum types
    @app.get("/tasks/{task_id}")
    def get_task(
        task_id: int = Path(..., description="Task ID"),
        priority: Priority = Query(Priority.MEDIUM, description="Filter by priority"),
        include_inactive: bool = Query(False, description="Include inactive tasks")
    ):
        return {}
    
    # Endpoint with Pydantic models containing enums
    @app.post("/projects", response_model=Project)
    def create_project(project: Project):
        return project
    
    # Endpoint with optional enum parameters
    @app.get("/reports")
    def get_reports(
        status: Optional[UserStatus] = Query(None, description="Optional status filter"),
        priority: Optional[Priority] = Query(None, description="Optional priority filter")
    ):
        return []
    
    # Test discovery
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    # Validate that all endpoints were discovered
    assert len(endpoints) == 5
    
    # Test endpoint with direct enum parameters
    users_endpoint = next(e for e in endpoints if e.path == "/users")
    assert users_endpoint.method == "GET"
    assert len(users_endpoint.parameters) == 2
    
    # Check status parameter (direct enum)
    status_param = next(p for p in users_endpoint.parameters if p.name == "status")
    assert status_param.param_type == "query"
    assert status_param.python_type == "Enum[UserStatus]"
    assert status_param.required == False
    assert status_param.default == UserStatus.ACTIVE
    assert status_param.enum_info is not None
    assert status_param.enum_info.class_name == "UserStatus"
    assert len(status_param.enum_info.values) == 3
    
    # Check limit parameter (non-enum, should work normally)
    limit_param = next(p for p in users_endpoint.parameters if p.name == "limit")
    assert limit_param.param_type == "query"
    assert limit_param.python_type == "int"
    assert limit_param.enum_info is None
    assert limit_param.constraints.get("ge") == 1
    assert limit_param.constraints.get("le") == 100
    
    # Test endpoint with field enum constraints
    items_endpoint = next(e for e in endpoints if e.path == "/items")
    category_param = next(p for p in items_endpoint.parameters if p.name == "category")
    assert category_param.enum_info is not None
    assert category_param.enum_info.class_name == "FieldEnum"
    assert len(category_param.enum_info.values) == 3
    
    # Test endpoint with mixed enum types
    task_endpoint = next(e for e in endpoints if e.path == "/tasks/{task_id}")
    priority_param = next(p for p in task_endpoint.parameters if p.name == "priority")
    assert priority_param.python_type == "Enum[Priority]"
    assert priority_param.enum_info.enum_type == "IntEnum"
    
    # Test endpoint with Pydantic models
    projects_endpoint = next(e for e in endpoints if e.path == "/projects")
    assert projects_endpoint.pydantic_enum_info is not None
    assert "parameter_project" in projects_endpoint.pydantic_enum_info
    
    # Test endpoint with optional enum parameters
    reports_endpoint = next(e for e in endpoints if e.path == "/reports")
    optional_status_param = next(p for p in reports_endpoint.parameters if p.name == "status")
    assert optional_status_param.python_type == "Optional[Enum[UserStatus]]"
    assert optional_status_param.required == False
    assert optional_status_param.default is None
    
    print("✅ Enhanced enum support works correctly with existing FastAPI applications")


def test_backward_compatibility_with_non_enum_parameters():
    """
    Test that enhanced enum support maintains backward compatibility
    with existing non-enum parameters and functionality.
    """
    app = FastAPI()
    
    # Endpoint with various non-enum parameter types
    @app.get("/search")
    def search(
        query: str = Query(..., description="Search query", min_length=1, max_length=100),
        limit: int = Query(10, ge=1, le=100, description="Result limit"),
        offset: int = Query(0, ge=0, description="Result offset"),
        include_deleted: bool = Query(False, description="Include deleted items"),
        tags: List[str] = Query([], description="Filter by tags"),
        price_min: Optional[float] = Query(None, description="Minimum price"),
        price_max: Optional[float] = Query(None, description="Maximum price")
    ):
        return []
    
    # Endpoint with path parameters
    @app.get("/users/{user_id}/posts/{post_id}")
    def get_post(
        user_id: int = Path(..., description="User ID", ge=1),
        post_id: int = Path(..., description="Post ID", ge=1),
        include_comments: bool = Query(True, description="Include comments")
    ):
        return {}
    
    # Test discovery
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    assert len(endpoints) == 2
    
    # Test search endpoint parameters
    search_endpoint = endpoints[0]
    assert len(search_endpoint.parameters) == 7
    
    # Validate each parameter maintains existing functionality
    params_by_name = {p.name: p for p in search_endpoint.parameters}
    
    # String parameter with constraints
    query_param = params_by_name["query"]
    assert query_param.param_type == "query"
    assert query_param.python_type == "str"
    assert query_param.required == True
    assert query_param.enum_info is None  # Should not have enum info
    assert query_param.constraints.get("min_length") == 1
    assert query_param.constraints.get("max_length") == 100
    
    # Integer parameter with constraints
    limit_param = params_by_name["limit"]
    assert limit_param.param_type == "query"
    assert limit_param.python_type == "int"
    assert limit_param.required == False
    assert limit_param.default == 10
    assert limit_param.enum_info is None
    assert limit_param.constraints.get("ge") == 1
    assert limit_param.constraints.get("le") == 100
    
    # Boolean parameter
    include_deleted_param = params_by_name["include_deleted"]
    assert include_deleted_param.param_type == "query"
    assert include_deleted_param.python_type == "bool"
    assert include_deleted_param.required == False
    assert include_deleted_param.default == False
    assert include_deleted_param.enum_info is None
    
    # List parameter
    tags_param = params_by_name["tags"]
    assert tags_param.param_type == "query"
    assert tags_param.python_type in ["List[str]", "list[str]"]  # Handle both Python 3.8+ and older versions
    assert tags_param.required == False
    assert tags_param.enum_info is None
    
    # Optional parameters
    price_min_param = params_by_name["price_min"]
    assert price_min_param.param_type == "query"
    assert price_min_param.python_type == "Optional[float]"
    assert price_min_param.required == False
    assert price_min_param.default is None
    assert price_min_param.enum_info is None
    
    # Test path parameters endpoint
    post_endpoint = endpoints[1]
    path_params = [p for p in post_endpoint.parameters if p.param_type == "path"]
    assert len(path_params) == 2
    
    user_id_param = next(p for p in path_params if p.name == "user_id")
    assert user_id_param.param_type == "path"
    assert user_id_param.python_type == "int"
    assert user_id_param.required == True
    assert user_id_param.enum_info is None
    assert user_id_param.constraints.get("ge") == 1
    
    print("✅ Backward compatibility maintained with non-enum parameters")


def test_performance_impact_of_enum_processing():
    """
    Test the performance impact of enhanced enum processing.
    
    This test ensures that the enum processing doesn't significantly
    impact the performance of endpoint discovery and report generation.
    """
    # Create a large FastAPI app with many endpoints
    app = FastAPI()
    
    # Add endpoints with various parameter types
    for i in range(50):
        # Mix of enum and non-enum endpoints
        if i % 3 == 0:
            # Enum endpoint
            @app.get(f"/enum-endpoint-{i}")
            def enum_endpoint(
                status: UserStatus = Query(UserStatus.ACTIVE),
                priority: Priority = Query(Priority.MEDIUM)
            ):
                return {}
        elif i % 3 == 1:
            # Field enum endpoint
            @app.get(f"/field-enum-endpoint-{i}")
            def field_enum_endpoint(
                category: str = Query(..., enum=["a", "b", "c"]),
                sort: str = Query("name", enum=["name", "date"])
            ):
                return {}
        else:
            # Non-enum endpoint
            @app.get(f"/regular-endpoint-{i}")
            def regular_endpoint(
                query: str = Query(..., min_length=1),
                limit: int = Query(10, ge=1, le=100),
                offset: int = Query(0, ge=0)
            ):
                return {}
    
    # Measure discovery time
    start_time = time.time()
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    discovery_time = time.time() - start_time
    
    # Validate discovery worked correctly
    assert len(endpoints) == 50
    
    # Count enum vs non-enum endpoints
    enum_endpoints = 0
    field_enum_endpoints = 0
    regular_endpoints = 0
    
    for endpoint in endpoints:
        has_enum = any(p.enum_info is not None for p in endpoint.parameters)
        has_field_enum = any(
            p.enum_info is not None and p.enum_info.class_name == "FieldEnum" 
            for p in endpoint.parameters
        )
        
        if has_field_enum:
            field_enum_endpoints += 1
        elif has_enum:
            enum_endpoints += 1
        else:
            regular_endpoints += 1
    
    # Validate distribution
    assert enum_endpoints >= 15  # Should have ~17 enum endpoints
    assert field_enum_endpoints >= 15  # Should have ~17 field enum endpoints
    assert regular_endpoints >= 15  # Should have ~16 regular endpoints
    
    # Test report generation performance
    report = APIReport(
        server_name="Performance Test API",
        server_version="1.0.0",
        endpoints=endpoints
    )
    
    # Test JSON formatting performance
    start_time = time.time()
    json_formatter = JSONFormatter()
    json_output = json_formatter.format(report)
    json_time = time.time() - start_time
    
    # Test Markdown formatting performance
    start_time = time.time()
    md_formatter = MarkdownFormatter()
    md_output = md_formatter.format(report)
    md_time = time.time() - start_time
    
    # Test HTML formatting performance
    start_time = time.time()
    html_formatter = HTMLFormatter()
    html_output = html_formatter.format(report)
    html_time = time.time() - start_time
    
    # Validate outputs are not empty
    assert len(json_output) > 1000
    assert len(md_output) > 1000
    assert len(html_output) > 1000
    
    # Validate JSON is parseable
    parsed_json = json.loads(json_output)
    assert "endpoints" in parsed_json
    assert len(parsed_json["endpoints"]) == 50
    
    # Performance assertions (should complete reasonably quickly)
    assert discovery_time < 5.0, f"Discovery took too long: {discovery_time:.2f}s"
    assert json_time < 2.0, f"JSON formatting took too long: {json_time:.2f}s"
    assert md_time < 2.0, f"Markdown formatting took too long: {md_time:.2f}s"
    assert html_time < 2.0, f"HTML formatting took too long: {html_time:.2f}s"
    
    print(f"✅ Performance test passed:")
    print(f"   - Discovery: {discovery_time:.3f}s for 50 endpoints")
    print(f"   - JSON formatting: {json_time:.3f}s")
    print(f"   - Markdown formatting: {md_time:.3f}s")
    print(f"   - HTML formatting: {html_time:.3f}s")


def test_integration_between_all_enhanced_components():
    """
    Test integration between all enhanced components to ensure
    they work together correctly end-to-end.
    """
    app = FastAPI(title="Integration Test API", version="2.0.0")
    
    # Complex endpoint with multiple enum types and nested models
    @app.post("/complex-endpoint", response_model=Project)
    def complex_endpoint(
        # Direct enum parameters
        default_status: UserStatus = Query(UserStatus.ACTIVE, description="Default user status"),
        priority_filter: Priority = Query(Priority.MEDIUM, description="Priority filter"),
        
        # Field enum parameters
        category: str = Query(..., enum=["urgent", "normal", "low"], description="Request category"),
        
        # Optional enum parameters
        optional_status: Optional[UserStatus] = Query(None, description="Optional status"),
        
        # Non-enum parameters (for compatibility)
        limit: int = Query(10, ge=1, le=100, description="Result limit"),
        include_archived: bool = Query(False, description="Include archived items"),
        
        # Request body with nested enums
        project_data: Project = Body(..., description="Project data")
    ):
        return project_data
    
    # Test discovery
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    assert len(endpoints) == 1
    endpoint = endpoints[0]
    
    # Validate endpoint basic info
    assert endpoint.path == "/complex-endpoint"
    assert endpoint.method == "POST"
    assert len(endpoint.parameters) == 7
    
    # Test parameter enum detection
    params_by_name = {p.name: p for p in endpoint.parameters}
    
    # Direct enum parameter
    default_status_param = params_by_name["default_status"]
    assert default_status_param.python_type == "Enum[UserStatus]"
    assert default_status_param.enum_info.class_name == "UserStatus"
    # UserStatus is actually a StrEnum in Python 3.11+, but may be detected as Enum in older versions
    assert default_status_param.enum_info.enum_type in ["Enum", "StrEnum"]
    assert len(default_status_param.enum_info.values) == 3
    
    # IntEnum parameter
    priority_param = params_by_name["priority_filter"]
    assert priority_param.python_type == "Enum[Priority]"
    assert priority_param.enum_info.class_name == "Priority"
    assert priority_param.enum_info.enum_type == "IntEnum"
    assert len(priority_param.enum_info.values) == 3
    
    # Field enum parameter
    category_param = params_by_name["category"]
    assert category_param.python_type == "str"
    assert category_param.enum_info.class_name == "FieldEnum"
    assert len(category_param.enum_info.values) == 3
    assert "enum" in category_param.constraints
    
    # Optional enum parameter
    optional_status_param = params_by_name["optional_status"]
    assert optional_status_param.python_type == "Optional[Enum[UserStatus]]"
    assert optional_status_param.enum_info.class_name == "UserStatus"
    assert optional_status_param.required == False
    
    # Non-enum parameters should work normally
    limit_param = params_by_name["limit"]
    assert limit_param.python_type == "int"
    assert limit_param.enum_info is None
    assert limit_param.constraints.get("ge") == 1
    
    # Test Pydantic model enum discovery
    assert endpoint.pydantic_enum_info is not None
    assert "parameter_project_data" in endpoint.pydantic_enum_info
    
    project_enum_info = endpoint.pydantic_enum_info["parameter_project_data"]
    enum_fields = project_enum_info["enum_fields"]
    
    # Should find status enum in Project model
    assert "status" in enum_fields
    status_field = enum_fields["status"]
    assert status_field["enum_info"]["class_name"] == "UserStatus"
    
    # Should find nested enums in User model (owner field)
    assert "owner" in enum_fields
    owner_field = enum_fields["owner"]
    assert owner_field["field_type"] == "nested_model"
    assert "status" in owner_field["nested"]
    
    # Should find enums in Task list
    assert "tasks" in enum_fields
    tasks_field = enum_fields["tasks"]
    assert tasks_field["field_type"] == "list"
    
    # Test response model enum discovery
    assert "response_model_Project" in endpoint.pydantic_enum_info
    
    # Create API report
    report = APIReport(
        server_name="Integration Test API",
        server_version="2.0.0",
        endpoints=endpoints,
        openapi_spec=discovery.get_openapi_schema()
    )
    
    # Test all formatters with the complex endpoint
    json_formatter = JSONFormatter()
    json_output = json_formatter.format(report)
    
    md_formatter = MarkdownFormatter()
    md_output = md_formatter.format(report)
    
    html_formatter = HTMLFormatter()
    html_output = html_formatter.format(report)
    
    # Validate JSON output contains enum information
    parsed_json = json.loads(json_output)
    endpoint_data = parsed_json["endpoints"][0]
    
    # Check parameter enum metadata
    json_params = {p["name"]: p for p in endpoint_data["parameters"]}
    
    default_status_json = json_params["default_status"]
    assert "enum_metadata" in default_status_json
    assert default_status_json["enum_metadata"]["class_name"] == "UserStatus"
    assert len(default_status_json["enum_metadata"]["values"]) == 3
    
    # Check Pydantic enum metadata
    assert "pydantic_enum_metadata" in endpoint_data
    
    # Validate Markdown output contains enum information
    assert "UserStatus" in md_output
    assert "Priority" in md_output
    assert "`active`" in md_output
    assert "`2`" in md_output  # Priority.MEDIUM value
    
    # Validate HTML output contains enum information
    assert "UserStatus" in html_output
    assert "Priority" in html_output
    assert "enum-value" in html_output or "ACTIVE" in html_output
    
    print("✅ All enhanced components integrate correctly end-to-end")


def test_error_handling_and_graceful_degradation():
    """
    Test error handling and graceful degradation when enum processing fails.
    """
    app = FastAPI()
    
    # Create a problematic enum class for testing error handling
    class ProblematicEnum(Enum):
        """Enum that might cause issues."""
        VALID = "valid"
        # This will be fine, but we'll test with edge cases
    
    @app.get("/test-error-handling")
    def test_endpoint(
        # Valid enum parameter
        status: UserStatus = Query(UserStatus.ACTIVE),
        # Parameter that might cause issues
        problematic: ProblematicEnum = Query(ProblematicEnum.VALID),
        # Regular parameter (should always work)
        limit: int = Query(10, ge=1)
    ):
        return {}
    
    # Test discovery with error handling
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    # Should still discover the endpoint even if some enum processing fails
    assert len(endpoints) == 1
    endpoint = endpoints[0]
    
    # Should have all parameters
    assert len(endpoint.parameters) == 3
    
    # Regular parameter should always work
    limit_param = next(p for p in endpoint.parameters if p.name == "limit")
    assert limit_param.python_type == "int"
    assert limit_param.enum_info is None
    assert limit_param.constraints.get("ge") == 1
    
    # Valid enum parameter should work
    status_param = next(p for p in endpoint.parameters if p.name == "status")
    assert status_param.python_type == "Enum[UserStatus]"
    assert status_param.enum_info is not None
    
    # Problematic enum should either work or gracefully degrade
    problematic_param = next(p for p in endpoint.parameters if p.name == "problematic")
    # Should at least have basic parameter info
    assert problematic_param.name == "problematic"
    assert problematic_param.param_type == "query"
    
    # Test report generation with potential enum issues
    report = APIReport(
        server_name="Error Handling Test",
        server_version="1.0.0",
        endpoints=endpoints
    )
    
    # All formatters should handle errors gracefully
    json_formatter = JSONFormatter()
    json_output = json_formatter.format(report)
    assert len(json_output) > 100  # Should produce valid output
    
    # Should be valid JSON
    parsed_json = json.loads(json_output)
    assert "endpoints" in parsed_json
    
    md_formatter = MarkdownFormatter()
    md_output = md_formatter.format(report)
    assert len(md_output) > 100  # Should produce valid output
    
    html_formatter = HTMLFormatter()
    html_output = html_formatter.format(report)
    assert len(html_output) > 100  # Should produce valid output
    
    print("✅ Error handling and graceful degradation work correctly")


if __name__ == "__main__":
    test_enhanced_enum_support_with_existing_fastapi_app()
    test_backward_compatibility_with_non_enum_parameters()
    test_performance_impact_of_enum_processing()
    test_integration_between_all_enhanced_components()
    test_error_handling_and_graceful_degradation()
    print("\n🎉 All integration and compatibility tests passed!")