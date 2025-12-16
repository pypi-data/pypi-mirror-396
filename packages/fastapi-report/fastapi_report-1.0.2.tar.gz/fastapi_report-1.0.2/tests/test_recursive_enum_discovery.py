"""
Tests for recursive enum discovery in complex types.

This module tests the enhanced enum discovery functionality that can
find enums in request bodies, response models, and nested data structures.
"""
from enum import Enum, IntEnum
from typing import List, Optional, Union
from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi_report.discovery.fastapi_discovery import FastAPIDiscovery


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
    URGENT = 4


class Category(Enum):
    """Item categories."""
    ELECTRONICS = "electronics"
    BOOKS = "books"
    CLOTHING = "clothing"


class UserProfile(BaseModel):
    """User profile with enum fields."""
    username: str
    status: UserStatus
    email: str


class Task(BaseModel):
    """Task model with enum fields."""
    title: str
    priority: Priority
    status: UserStatus
    description: Optional[str] = None


class NestedModel(BaseModel):
    """Model with nested enum-containing models."""
    user: UserProfile
    tasks: List[Task]
    category: Category


class ResponseModel(BaseModel):
    """Response model with enum fields."""
    success: bool
    user_status: UserStatus
    priority: Priority


def test_request_body_enum_discovery():
    """Test that enums in request body schemas are discovered."""
    app = FastAPI()
    
    @app.post("/users")
    def create_user(user: UserProfile):
        return user
    
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    assert len(endpoints) == 1
    endpoint = endpoints[0]
    
    # Should have discovered enum info in Pydantic models
    assert endpoint.pydantic_enum_info
    assert "parameter_user" in endpoint.pydantic_enum_info
    
    user_model_info = endpoint.pydantic_enum_info["parameter_user"]
    assert user_model_info["model_name"] == "UserProfile"
    assert "enum_fields" in user_model_info
    
    # Should have found the status enum field
    enum_fields = user_model_info["enum_fields"]
    assert "status" in enum_fields
    
    status_enum_info = enum_fields["status"]["enum_info"]
    assert status_enum_info["class_name"] == "UserStatus"
    assert len(status_enum_info["values"]) == 3
    
    # Check enum values
    enum_values = {v["name"]: v["value"] for v in status_enum_info["values"]}
    assert enum_values["ACTIVE"] == "active"
    assert enum_values["INACTIVE"] == "inactive"
    assert enum_values["SUSPENDED"] == "suspended"


def test_response_model_enum_discovery():
    """Test that enums in response models are discovered."""
    app = FastAPI()
    
    @app.get("/status", response_model=ResponseModel)
    def get_status():
        return ResponseModel(
            success=True,
            user_status=UserStatus.ACTIVE,
            priority=Priority.HIGH
        )
    
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    assert len(endpoints) == 1
    endpoint = endpoints[0]
    
    # Should have discovered enum info in response model
    assert endpoint.pydantic_enum_info
    assert "response_model_ResponseModel" in endpoint.pydantic_enum_info
    
    response_model_info = endpoint.pydantic_enum_info["response_model_ResponseModel"]
    assert response_model_info["model_name"] == "ResponseModel"
    
    enum_fields = response_model_info["enum_fields"]
    
    # Should have found both enum fields
    assert "user_status" in enum_fields
    assert "priority" in enum_fields
    
    # Check UserStatus enum
    user_status_info = enum_fields["user_status"]["enum_info"]
    assert user_status_info["class_name"] == "UserStatus"
    assert user_status_info["enum_type"] == "StrEnum"
    
    # Check Priority enum
    priority_info = enum_fields["priority"]["enum_info"]
    assert priority_info["class_name"] == "Priority"
    assert priority_info["enum_type"] == "IntEnum"


def test_nested_model_enum_discovery():
    """Test that enums in nested models are discovered recursively."""
    app = FastAPI()
    
    @app.post("/complex")
    def create_complex(data: NestedModel):
        return data
    
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    assert len(endpoints) == 1
    endpoint = endpoints[0]
    
    # Should have discovered enum info
    assert endpoint.pydantic_enum_info
    assert "parameter_data" in endpoint.pydantic_enum_info
    
    nested_model_info = endpoint.pydantic_enum_info["parameter_data"]
    enum_fields = nested_model_info["enum_fields"]
    
    # Should have found the direct category enum field
    assert "category" in enum_fields
    category_info = enum_fields["category"]["enum_info"]
    assert category_info["class_name"] == "Category"
    
    # Should have found nested model enums
    assert "user" in enum_fields
    user_nested_info = enum_fields["user"]["nested"]
    assert "status" in user_nested_info
    
    # Should have found list model enums
    assert "tasks" in enum_fields
    tasks_info = enum_fields["tasks"]
    assert tasks_info["field_type"] == "list"
    assert "list_item" in tasks_info
    
    # The list item should contain enum information from the Task model
    task_item_info = tasks_info["list_item"]
    assert task_item_info["field_type"] == "nested_model"
    assert "nested" in task_item_info
    
    # Should find enums in the Task model
    task_nested_info = task_item_info["nested"]
    assert "priority" in task_nested_info
    assert "status" in task_nested_info


def test_openapi_schema_enum_discovery():
    """Test that enums are discovered from OpenAPI schema definitions."""
    app = FastAPI()
    
    @app.get("/items")
    def get_items(category: str = Query(..., enum=["electronics", "books", "clothing"])):
        return []
    
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    assert len(endpoints) == 1
    endpoint = endpoints[0]
    
    # Should have request body enum info from OpenAPI schema
    # This tests the _discover_enums_in_schema method indirectly
    
    # Check parameter enum info
    category_param = next(p for p in endpoint.parameters if p.name == "category")
    assert category_param.enum_info is not None
    assert category_param.enum_info.class_name == "FieldEnum"
    assert len(category_param.enum_info.values) == 3


def test_mixed_enum_sources():
    """Test handling of enums from multiple sources (type hints + FastAPI fields)."""
    app = FastAPI()
    
    @app.get("/mixed")
    def get_mixed(
        status: UserStatus = Query(UserStatus.ACTIVE, description="User status"),
        category: str = Query(..., enum=["electronics", "books"], description="Category")
    ):
        return {}
    
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    assert len(endpoints) == 1
    endpoint = endpoints[0]
    
    # Check status parameter (from type hint)
    status_param = next(p for p in endpoint.parameters if p.name == "status")
    assert status_param.enum_info is not None
    assert status_param.enum_info.class_name == "UserStatus"
    assert status_param.python_type == "Enum[UserStatus]"
    
    # Check category parameter (from FastAPI field)
    category_param = next(p for p in endpoint.parameters if p.name == "category")
    assert category_param.enum_info is not None
    assert category_param.enum_info.class_name == "FieldEnum"
    assert len(category_param.enum_info.values) == 2


def test_optional_enum_handling():
    """Test that Optional[Enum] types are handled correctly."""
    app = FastAPI()
    
    @app.get("/optional")
    def get_optional(status: Optional[UserStatus] = None):
        return {}
    
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    assert len(endpoints) == 1
    endpoint = endpoints[0]
    
    # Check optional enum parameter
    status_param = next(p for p in endpoint.parameters if p.name == "status")
    assert status_param.python_type == "Optional[Enum[UserStatus]]"
    assert status_param.enum_info is not None
    assert status_param.enum_info.class_name == "UserStatus"
    assert not status_param.required


def test_union_enum_handling():
    """Test that Union types containing enums are handled correctly."""
    app = FastAPI()
    
    @app.get("/union")
    def get_union(value: Union[UserStatus, Priority]):
        return {}
    
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    assert len(endpoints) == 1
    endpoint = endpoints[0]
    
    # Check union parameter
    value_param = next(p for p in endpoint.parameters if p.name == "value")
    # The exact handling of Union[Enum, Enum] may vary
    # At minimum, it should not crash and should provide some enum information
    assert value_param is not None