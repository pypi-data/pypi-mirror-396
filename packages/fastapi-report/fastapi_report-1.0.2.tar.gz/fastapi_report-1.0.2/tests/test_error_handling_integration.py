"""
Integration test for error handling and validation.

This test demonstrates the error handling capabilities working together
across the entire enum processing pipeline.
"""
import logging
from enum import Enum
from typing import Optional
from fastapi import FastAPI, Query
from fastapi_report.discovery.fastapi_discovery import FastAPIDiscovery
from fastapi_report.formatters.json_formatter import JSONFormatter
from fastapi_report.models import APIReport


class ValidEnum(Enum):
    """A valid enum for testing."""
    OPTION_A = "a"
    OPTION_B = "b"


class EmptyEnum(Enum):
    """An empty enum for testing edge cases."""
    pass


def test_error_handling_integration():
    """Test error handling across the entire pipeline."""
    # Set up logging to capture warnings and errors
    logging.basicConfig(level=logging.DEBUG)
    
    # Create a FastAPI app with various enum scenarios
    app = FastAPI()
    
    @app.get("/valid-enum")
    def valid_enum_endpoint(status: ValidEnum = Query(...)):
        """Endpoint with valid enum parameter."""
        return {"status": status}
    
    @app.get("/empty-enum")
    def empty_enum_endpoint(status: Optional[EmptyEnum] = Query(None)):
        """Endpoint with empty enum parameter."""
        return {"status": status}
    
    @app.get("/conflicting-enum")
    def conflicting_enum_endpoint(
        status: ValidEnum = Query(..., enum=["x", "y", "z"])  # Conflicts with ValidEnum
    ):
        """Endpoint with conflicting enum constraints."""
        return {"status": status}
    
    # Discover endpoints with error handling
    discovery = FastAPIDiscovery(app)
    endpoints = discovery.discover_endpoints()
    
    # Verify that all endpoints were discovered despite errors
    assert len(endpoints) == 3
    
    # Create a report
    report = APIReport(
        server_name="Test Server",
        server_version="1.0.0",
        endpoints=endpoints
    )
    
    # Format the report with error handling
    formatter = JSONFormatter()
    json_output = formatter.format(report)
    
    # Verify that the JSON output is valid despite any errors
    import json
    parsed_json = json.loads(json_output)
    assert "endpoints" in parsed_json
    assert len(parsed_json["endpoints"]) == 3
    
    # Check that enum information is present where expected
    valid_enum_endpoint = next(
        (ep for ep in parsed_json["endpoints"] if ep["path"] == "/valid-enum"), 
        None
    )
    assert valid_enum_endpoint is not None
    
    # The valid enum should have proper enum metadata
    status_param = next(
        (p for p in valid_enum_endpoint["parameters"] if p["name"] == "status"), 
        None
    )
    assert status_param is not None
    assert "enum_metadata" in status_param
    
    # The empty enum endpoint should still work (graceful handling)
    empty_enum_endpoint = next(
        (ep for ep in parsed_json["endpoints"] if ep["path"] == "/empty-enum"), 
        None
    )
    assert empty_enum_endpoint is not None
    
    print("Integration test passed - error handling works across the pipeline!")


if __name__ == "__main__":
    test_error_handling_integration()