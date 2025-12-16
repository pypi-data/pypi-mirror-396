"""
Enum type detection utilities.

This module provides comprehensive enum type analysis for FastAPI parameters,
including detection, metadata extraction, and type string formatting.
"""
import inspect
import logging
from enum import Enum, IntEnum
from typing import Any, List, Optional, Type, get_origin, get_args, Union
from fastapi_report.models import EnumInfo, EnumValue

# Configure logger for enum detection
logger = logging.getLogger(__name__)


class EnumTypeDetector:
    """Utility class for comprehensive enum type analysis."""
    
    def is_enum_type(self, type_hint: Any) -> bool:
        """
        Check if a type hint represents an Enum type.
        
        Args:
            type_hint: Python type hint to analyze
            
        Returns:
            True if the type hint is an Enum type, False otherwise
        """
        if type_hint is None:
            return False
        
        # Handle Optional[Enum] types - both old and new syntax
        origin = get_origin(type_hint)
        
        # Handle typing.Union (old syntax)
        if origin is Union:
            args = get_args(type_hint)
            # Check if this is Optional[T] (Union[T, None])
            if type(None) in args:
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    return self.is_enum_type(non_none_args[0])
        
        # Handle types.UnionType (new Python 3.10+ syntax: T | None)
        import types
        if hasattr(types, 'UnionType') and isinstance(type_hint, types.UnionType):
            args = get_args(type_hint)
            # Check if this is Optional[T] (T | None)
            if type(None) in args:
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    return self.is_enum_type(non_none_args[0])
        
        # Check if the type is a direct Enum subclass
        try:
            return (inspect.isclass(type_hint) and 
                    issubclass(type_hint, Enum))
        except TypeError:
            # issubclass can raise TypeError for non-class types
            return False
    
    def extract_enum_info(self, type_hint: Any) -> EnumInfo:
        """
        Extract comprehensive enum metadata from a type hint.
        
        Args:
            type_hint: Python type hint representing an Enum
            
        Returns:
            EnumInfo object with complete enum metadata
            
        Raises:
            ValueError: If type_hint is not an Enum type
        """
        if not self.is_enum_type(type_hint):
            logger.warning(f"Attempted to extract enum info from non-enum type: {type_hint}")
            raise ValueError(f"Type {type_hint} is not an Enum type")
        
        try:
            # Handle Optional[Enum] types - both old and new syntax
            enum_class = type_hint
            origin = get_origin(type_hint)
            
            # Handle typing.Union (old syntax)
            if origin is Union:
                args = get_args(type_hint)
                if type(None) in args:
                    non_none_args = [arg for arg in args if arg is not type(None)]
                    if len(non_none_args) == 1:
                        enum_class = non_none_args[0]
            
            # Handle types.UnionType (new Python 3.10+ syntax: T | None)
            import types
            if hasattr(types, 'UnionType') and isinstance(type_hint, types.UnionType):
                args = get_args(type_hint)
                if type(None) in args:
                    non_none_args = [arg for arg in args if arg is not type(None)]
                    if len(non_none_args) == 1:
                        enum_class = non_none_args[0]
            
            # Validate enum class has members
            if not hasattr(enum_class, '__members__') or not enum_class.__members__:
                logger.warning(f"Enum class {enum_class.__name__} has no members")
                # Return empty enum info rather than failing
                return EnumInfo(
                    class_name=getattr(enum_class, '__name__', str(enum_class)),
                    module_name=getattr(enum_class, '__module__', None),
                    values=[],
                    enum_type="Enum",
                    description="Empty enum - no members defined"
                )
            
            # Extract enum values with error handling
            enum_values = self.get_enum_values(enum_class)
            
            # Determine enum type string with fallback
            try:
                enum_type_str = self._get_enum_type_name(enum_class)
            except Exception as e:
                logger.warning(f"Failed to determine enum type for {enum_class.__name__}: {e}")
                enum_type_str = "Enum"  # Fallback to base type
            
            # Get module name with fallback
            module_name = getattr(enum_class, '__module__', None)
            
            # Get class documentation with error handling
            try:
                description = inspect.getdoc(enum_class)
            except Exception as e:
                logger.warning(f"Failed to get documentation for enum {enum_class.__name__}: {e}")
                description = None
            
            return EnumInfo(
                class_name=getattr(enum_class, '__name__', str(enum_class)),
                module_name=module_name,
                values=enum_values,
                enum_type=enum_type_str,
                description=description
            )
            
        except Exception as e:
            logger.error(f"Failed to extract enum info from {type_hint}: {e}")
            # Return a minimal enum info as fallback
            return EnumInfo(
                class_name=str(type_hint),
                module_name=None,
                values=[],
                enum_type="Enum",
                description=f"Failed to extract enum info: {str(e)}"
            )
    
    def get_enum_values(self, enum_class: Type[Enum]) -> List[EnumValue]:
        """
        Extract all enum member values from an Enum class.
        
        Args:
            enum_class: Enum class to analyze
            
        Returns:
            List of EnumValue objects representing all enum members
        """
        if not (inspect.isclass(enum_class) and issubclass(enum_class, Enum)):
            logger.error(f"Expected Enum class, got {enum_class}")
            raise ValueError(f"Expected Enum class, got {enum_class}")
        
        enum_values = []
        
        try:
            for member in enum_class:
                try:
                    # Get member documentation if available
                    description = None
                    if hasattr(member, '__doc__') and member.__doc__:
                        description = member.__doc__.strip()
                    
                    # Validate member has required attributes
                    if not hasattr(member, 'name') or not hasattr(member, 'value'):
                        logger.warning(f"Enum member {member} missing name or value attributes")
                        continue
                    
                    # Handle special characters or encoding issues in enum values
                    try:
                        member_value = member.value
                        member_name = member.name
                        
                        # Ensure values are serializable
                        if not self._is_serializable_value(member_value):
                            logger.warning(f"Enum value {member_value} is not JSON serializable, converting to string")
                            member_value = str(member_value)
                        
                        enum_values.append(EnumValue(
                            name=member_name,
                            value=member_value,
                            description=description
                        ))
                        
                    except Exception as e:
                        logger.warning(f"Failed to process enum member {member}: {e}")
                        # Add a fallback entry
                        enum_values.append(EnumValue(
                            name=str(member),
                            value=str(member),
                            description=f"Failed to extract member info: {str(e)}"
                        ))
                        
                except Exception as e:
                    logger.warning(f"Error processing enum member: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to iterate over enum members for {enum_class.__name__}: {e}")
            # Return empty list as fallback
            return []
        
        return enum_values
    
    def get_enum_type_string(self, enum_class: Type[Enum]) -> str:
        """
        Generate proper type string formatting for an Enum class.
        
        Args:
            enum_class: Enum class to format
            
        Returns:
            String representation in "Enum[ClassName]" format
        """
        if not (inspect.isclass(enum_class) and issubclass(enum_class, Enum)):
            logger.error(f"Expected Enum class, got {enum_class}")
            raise ValueError(f"Expected Enum class, got {enum_class}")
        
        try:
            class_name = getattr(enum_class, '__name__', str(enum_class))
            return f"Enum[{class_name}]"
        except Exception as e:
            logger.warning(f"Failed to get class name for enum {enum_class}: {e}")
            return f"Enum[{str(enum_class)}]"
    
    def _get_enum_type_name(self, enum_class: Type[Enum]) -> str:
        """
        Determine the specific enum type name (Enum, IntEnum, StrEnum, etc.).
        
        Args:
            enum_class: Enum class to analyze
            
        Returns:
            String name of the enum type
        """
        # Check for IntEnum
        if issubclass(enum_class, IntEnum):
            return "IntEnum"
        
        # Check for StrEnum (Python 3.11+)
        try:
            from enum import StrEnum
            if issubclass(enum_class, StrEnum):
                return "StrEnum"
        except ImportError:
            # StrEnum not available in older Python versions
            pass
        
        # Check if all values are strings (custom StrEnum-like)
        if all(isinstance(member.value, str) for member in enum_class):
            return "StrEnum"
        
        # Check if all values are integers (custom IntEnum-like)
        if all(isinstance(member.value, int) for member in enum_class):
            return "IntEnum"
        
        # Default to base Enum
        return "Enum"
    
    def _is_serializable_value(self, value: Any) -> bool:
        """
        Check if a value is JSON serializable.
        
        Args:
            value: Value to check
            
        Returns:
            True if value is serializable, False otherwise
        """
        try:
            import json
            json.dumps(value)
            return True
        except (TypeError, ValueError):
            return False
    
    def validate_enum_constraints(self, field_enum_values: List[Any], type_enum_values: List[Any]) -> bool:
        """
        Validate that enum constraints from different sources are compatible.
        
        Args:
            field_enum_values: Enum values from FastAPI field constraints
            type_enum_values: Enum values from type hint analysis
            
        Returns:
            True if constraints are compatible, False otherwise
        """
        try:
            # Convert to sets for comparison
            field_set = set(field_enum_values) if field_enum_values else set()
            type_set = set(type_enum_values) if type_enum_values else set()
            
            # If either is empty, they're compatible
            if not field_set or not type_set:
                return True
            
            # Check if they're identical
            if field_set == type_set:
                return True
            
            # Check if one is a subset of the other
            if field_set.issubset(type_set) or type_set.issubset(field_set):
                logger.warning(f"Enum constraint mismatch: field values {field_enum_values} "
                             f"and type values {type_enum_values} are not identical but compatible")
                return True
            
            # Incompatible constraints
            logger.error(f"Incompatible enum constraints: field values {field_enum_values} "
                        f"and type values {type_enum_values} have no overlap")
            return False
            
        except Exception as e:
            logger.error(f"Failed to validate enum constraints: {e}")
            return False