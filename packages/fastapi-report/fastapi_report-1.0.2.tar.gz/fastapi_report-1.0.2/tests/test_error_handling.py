"""
Test error handling and validation for enum processing.

This module tests the error handling capabilities added to the enum
detection, formatting, and discovery components.
"""
import pytest
import logging
from enum import Enum
from typing import Optional, Union
from fastapi_report.discovery.enum_detector import EnumTypeDetector
from fastapi_report.formatters.enum_formatter import EnumFormatter
from fastapi_report.models import EnumInfo, EnumValue


class SampleEnum(Enum):
    """Test enum for error handling tests."""
    VALUE1 = "value1"
    VALUE2 = "value2"


class EmptyEnum(Enum):
    """Empty enum for testing edge cases."""
    pass


class InvalidEnum:
    """Not actually an enum - for testing invalid enum handling."""
    VALUE1 = "value1"


def test_enum_detector_invalid_type():
    """Test enum detector handles invalid types gracefully."""
    detector = EnumTypeDetector()
    
    # Test with non-enum type
    assert not detector.is_enum_type(str)
    assert not detector.is_enum_type(int)
    assert not detector.is_enum_type(InvalidEnum)
    assert not detector.is_enum_type(None)
    
    # Test extract_enum_info with invalid type should raise ValueError
    with pytest.raises(ValueError):
        detector.extract_enum_info(str)


def test_enum_detector_empty_enum():
    """Test enum detector handles empty enums gracefully."""
    detector = EnumTypeDetector()
    
    # Empty enum should still be detected as enum type
    assert detector.is_enum_type(EmptyEnum)
    
    # But extracting info should return empty values
    enum_info = detector.extract_enum_info(EmptyEnum)
    assert enum_info.class_name == "EmptyEnum"
    assert len(enum_info.values) == 0
    assert "Empty enum" in enum_info.description


def test_enum_detector_constraint_validation():
    """Test enum constraint validation."""
    detector = EnumTypeDetector()
    
    # Compatible constraints
    assert detector.validate_enum_constraints(["a", "b"], ["a", "b"])
    assert detector.validate_enum_constraints(["a"], ["a", "b"])  # subset
    assert detector.validate_enum_constraints([], ["a", "b"])  # empty
    
    # Incompatible constraints
    assert not detector.validate_enum_constraints(["a", "b"], ["c", "d"])


def test_enum_formatter_invalid_input():
    """Test enum formatter handles invalid input gracefully."""
    formatter = EnumFormatter()
    
    # Test with None
    assert formatter.format_enum_for_json(None) == {}
    assert formatter.format_enum_for_markdown(None) == ""
    assert formatter.format_enum_for_html(None) == ""
    
    # Test with empty values list
    assert formatter.format_enum_values_list([]) == ""


def test_enum_formatter_malformed_enum_info():
    """Test enum formatter handles malformed enum info."""
    formatter = EnumFormatter()
    
    # Create malformed enum info (missing attributes)
    class MalformedEnumInfo:
        pass
    
    malformed = MalformedEnumInfo()
    
    # Should not crash, should return error info
    result = formatter.format_enum_for_json(malformed)
    assert "class_name" in result
    assert result["class_name"] == "Unknown"


def test_enum_formatter_special_characters():
    """Test enum formatter handles special characters properly."""
    formatter = EnumFormatter()
    
    # Create enum with special characters
    enum_value = EnumValue(
        name="TEST_<>&\"'",
        value="value_<>&\"'",
        description="Description with <>&\"' characters"
    )
    
    enum_info = EnumInfo(
        class_name="Test<>&\"'Enum",
        values=[enum_value],
        description="Enum with <>&\"' characters"
    )
    
    # HTML formatting should escape special characters
    html_result = formatter.format_enum_for_html(enum_info)
    assert "&lt;" in html_result
    assert "&gt;" in html_result
    assert "&amp;" in html_result
    assert "&quot;" in html_result
    
    # Markdown formatting should handle special characters (basic test)
    md_result = formatter.format_enum_for_markdown(enum_info)
    assert len(md_result) > 0  # Should produce some output
    assert "Test" in md_result  # Should contain the class name


def test_logging_configuration():
    """Test that logging is properly configured."""
    # Import modules to ensure loggers are created
    from fastapi_report.discovery import enum_detector
    from fastapi_report.discovery import fastapi_discovery
    from fastapi_report.formatters import enum_formatter
    from fastapi_report.formatters import json_formatter
    from fastapi_report.formatters import markdown_formatter
    
    # Check that loggers exist
    assert logging.getLogger(enum_detector.__name__)
    assert logging.getLogger(fastapi_discovery.__name__)
    assert logging.getLogger(enum_formatter.__name__)
    assert logging.getLogger(json_formatter.__name__)
    assert logging.getLogger(markdown_formatter.__name__)


def test_serializable_value_check():
    """Test the serializable value check helper."""
    detector = EnumTypeDetector()
    
    # Serializable values
    assert detector._is_serializable_value("string")
    assert detector._is_serializable_value(123)
    assert detector._is_serializable_value(True)
    assert detector._is_serializable_value([1, 2, 3])
    assert detector._is_serializable_value({"key": "value"})
    
    # Non-serializable values
    assert not detector._is_serializable_value(lambda x: x)  # function
    assert not detector._is_serializable_value(object())  # object instance


if __name__ == "__main__":
    pytest.main([__file__])