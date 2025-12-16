"""
Integration test for recursive enum discovery functionality.

This test demonstrates the complete workflow of discovering enums in
complex nested structures including request bodies, response models,
and OpenAPI schemas.
"""
from enum import Enum, IntEnum
from typing import List, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi_report.discovery.fastapi_discovery import FastAPIDiscovery


class Status(Enum):
    """Status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class Priority(IntEnum):
    """Priority levels."""
    LOW = 1
    HIGH = 2


class User(BaseModel):
    """User model with enum field."""
    name: str
    status: Status


class Task(BaseModel):
    """Task model with multiple enum fields."""
    title: str
    priority: Priority
    assignee: Optional[User] = None


class Project(BaseModel):
    """Project model with nested enum structures."""
    name: str
    status: Status
    tasks: List[Task]
    owner: User


def test_complete_recursive_enum_discovery():
    """Test complete recursive enum discovery across all components."""
    app = FastAPI()
    
    @app.post("/projects", response_model=Project)
    def create_project(
        project: Project,
        default_priority: Priority = Query(Priority.LOW, description="Default task priority"),
        filter_status: str = Query(..., enum=["active", "inactive"], description="Status filter")
    ):
        return project
    
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    assert len(endpoints) == 1
    endpoint = endpoints[0]
    
    # Test 1: Parameter enum discovery (direct enum type)
    priority_param = next(p for p in endpoint.parameters if p.name == "default_priority")
    assert priority_param.enum_info is not None
    assert priority_param.enum_info.class_name == "Priority"
    assert priority_param.enum_info.enum_type == "IntEnum"
    assert len(priority_param.enum_info.values) == 2
    
    # Test 2: Parameter enum discovery (field enum)
    status_param = next(p for p in endpoint.parameters if p.name == "filter_status")
    assert status_param.enum_info is not None
    assert status_param.enum_info.class_name == "FieldEnum"
    assert len(status_param.enum_info.values) == 2
    
    # Test 3: Request body Pydantic model enum discovery
    assert endpoint.pydantic_enum_info
    assert "parameter_project" in endpoint.pydantic_enum_info
    
    project_info = endpoint.pydantic_enum_info["parameter_project"]
    enum_fields = project_info["enum_fields"]
    
    # Direct enum field
    assert "status" in enum_fields
    status_info = enum_fields["status"]
    assert status_info["field_type"] == "pydantic_v2"
    assert status_info["enum_info"]["class_name"] == "Status"
    
    # Nested model with enum
    assert "owner" in enum_fields
    owner_info = enum_fields["owner"]
    assert owner_info["field_type"] == "nested_model"
    assert "status" in owner_info["nested"]
    
    # List of models with enums
    assert "tasks" in enum_fields
    tasks_info = enum_fields["tasks"]
    assert tasks_info["field_type"] == "list"
    
    task_item_info = tasks_info["list_item"]
    assert task_item_info["field_type"] == "nested_model"
    task_nested = task_item_info["nested"]
    
    # Task should have priority enum
    assert "priority" in task_nested
    priority_info = task_nested["priority"]
    assert priority_info["field_type"] == "pydantic_v2"
    assert priority_info["enum_info"]["class_name"] == "Priority"
    
    # Task should have optional assignee with nested enum
    assert "assignee" in task_nested
    assignee_info = task_nested["assignee"]
    assert assignee_info["field_type"] == "optional"
    
    optional_user_info = assignee_info["optional"]
    assert optional_user_info["field_type"] == "nested_model"
    assert "status" in optional_user_info["nested"]
    
    # Test 4: Response model enum discovery
    assert "response_model_Project" in endpoint.pydantic_enum_info
    response_info = endpoint.pydantic_enum_info["response_model_Project"]
    
    # Should have the same structure as the request body
    response_enum_fields = response_info["enum_fields"]
    assert "status" in response_enum_fields
    assert "owner" in response_enum_fields
    assert "tasks" in response_enum_fields
    
    # Test 5: OpenAPI schema enum discovery
    assert endpoint.responses
    assert 200 in endpoint.responses
    response_200 = endpoint.responses[200]
    assert "enum_info" in response_200
    
    # The OpenAPI schema should also contain enum information
    enum_info = response_200["enum_info"]
    assert "application/json" in enum_info
    
    print("✅ All recursive enum discovery tests passed!")
    print(f"📊 Discovered enums in:")
    print(f"   - {len(endpoint.parameters)} parameters")
    print(f"   - {len(endpoint.pydantic_enum_info)} Pydantic models")
    print(f"   - {len(endpoint.responses)} response schemas")


if __name__ == "__main__":
    test_complete_recursive_enum_discovery()