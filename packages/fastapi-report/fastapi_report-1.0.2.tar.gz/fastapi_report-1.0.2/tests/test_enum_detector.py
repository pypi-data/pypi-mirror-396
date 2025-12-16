"""
Tests for the EnumTypeDetector class.

This module tests the enum type detection utilities including
enum type identification, metadata extraction, and type string formatting.
"""
import pytest
from enum import Enum, IntEnum
from typing import Optional, Union
from fastapi_report.discovery.enum_detector import EnumTypeDetector
from fastapi_report.models import EnumInfo, EnumValue


class ColorEnum(Enum):
    """Test enum for basic enum functionality."""
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class NumberIntEnum(IntEnum):
    """Test integer enum."""
    FIRST = 1
    SECOND = 2
    THIRD = 3


class StatusEnum(Enum):
    """Test enum with documentation."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class TestEnumTypeDetector:
    """Test cases for EnumTypeDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = EnumTypeDetector()
    
    def test_is_enum_type_with_basic_enum(self):
        """Test enum type detection with basic Enum."""
        assert self.detector.is_enum_type(ColorEnum) is True
    
    def test_is_enum_type_with_int_enum(self):
        """Test enum type detection with IntEnum."""
        assert self.detector.is_enum_type(NumberIntEnum) is True
    
    def test_is_enum_type_with_optional_enum(self):
        """Test enum type detection with Optional[Enum]."""
        assert self.detector.is_enum_type(Optional[ColorEnum]) is True
    
    def test_is_enum_type_with_union_enum(self):
        """Test enum type detection with Union containing enum."""
        assert self.detector.is_enum_type(Union[ColorEnum, None]) is True
    
    def test_is_enum_type_with_non_enum(self):
        """Test enum type detection with non-enum types."""
        assert self.detector.is_enum_type(str) is False
        assert self.detector.is_enum_type(int) is False
        assert self.detector.is_enum_type(None) is False
        assert self.detector.is_enum_type("not_a_type") is False
    
    def test_extract_enum_info_basic_enum(self):
        """Test enum info extraction from basic enum."""
        enum_info = self.detector.extract_enum_info(ColorEnum)
        
        assert isinstance(enum_info, EnumInfo)
        assert enum_info.class_name == "ColorEnum"
        assert enum_info.enum_type == "StrEnum"  # All values are strings
        assert len(enum_info.values) == 3
        
        # Check enum values
        value_names = [v.name for v in enum_info.values]
        value_values = [v.value for v in enum_info.values]
        assert "RED" in value_names
        assert "GREEN" in value_names
        assert "BLUE" in value_names
        assert "red" in value_values
        assert "green" in value_values
        assert "blue" in value_values
    
    def test_extract_enum_info_int_enum(self):
        """Test enum info extraction from IntEnum."""
        enum_info = self.detector.extract_enum_info(NumberIntEnum)
        
        assert isinstance(enum_info, EnumInfo)
        assert enum_info.class_name == "NumberIntEnum"
        assert enum_info.enum_type == "IntEnum"
        assert len(enum_info.values) == 3
        
        # Check enum values
        value_names = [v.name for v in enum_info.values]
        value_values = [v.value for v in enum_info.values]
        assert "FIRST" in value_names
        assert "SECOND" in value_names
        assert "THIRD" in value_names
        assert 1 in value_values
        assert 2 in value_values
        assert 3 in value_values
    
    def test_extract_enum_info_optional_enum(self):
        """Test enum info extraction from Optional[Enum]."""
        enum_info = self.detector.extract_enum_info(Optional[ColorEnum])
        
        assert isinstance(enum_info, EnumInfo)
        assert enum_info.class_name == "ColorEnum"
        assert len(enum_info.values) == 3
    
    def test_extract_enum_info_non_enum_raises_error(self):
        """Test that extracting info from non-enum raises ValueError."""
        with pytest.raises(ValueError, match="is not an Enum type"):
            self.detector.extract_enum_info(str)
    
    def test_get_enum_values(self):
        """Test enum values extraction."""
        values = self.detector.get_enum_values(ColorEnum)
        
        assert len(values) == 3
        assert all(isinstance(v, EnumValue) for v in values)
        
        # Check specific values
        red_value = next(v for v in values if v.name == "RED")
        assert red_value.value == "red"
        
        green_value = next(v for v in values if v.name == "GREEN")
        assert green_value.value == "green"
        
        blue_value = next(v for v in values if v.name == "BLUE")
        assert blue_value.value == "blue"
    
    def test_get_enum_values_non_enum_raises_error(self):
        """Test that getting values from non-enum raises ValueError."""
        with pytest.raises(ValueError, match="Expected Enum class"):
            self.detector.get_enum_values(str)
    
    def test_get_enum_type_string(self):
        """Test enum type string formatting."""
        type_string = self.detector.get_enum_type_string(ColorEnum)
        assert type_string == "Enum[ColorEnum]"
        
        int_type_string = self.detector.get_enum_type_string(NumberIntEnum)
        assert int_type_string == "Enum[NumberIntEnum]"
    
    def test_get_enum_type_string_non_enum_raises_error(self):
        """Test that getting type string from non-enum raises ValueError."""
        with pytest.raises(ValueError, match="Expected Enum class"):
            self.detector.get_enum_type_string(str)