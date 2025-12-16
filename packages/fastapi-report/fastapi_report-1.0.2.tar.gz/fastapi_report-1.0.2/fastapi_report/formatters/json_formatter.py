"""JSON formatter for API reports."""
import json
import logging
from fastapi_report.models import APIReport
from .base import BaseFormatter
from .enum_formatter import EnumFormatter

# Configure logger for JSON formatting
logger = logging.getLogger(__name__)


class JSONFormatter(BaseFormatter):
    """Formats API reports as JSON."""
    
    def __init__(self):
        """Initialize JSON formatter with enum formatter."""
        self.enum_formatter = EnumFormatter()
    
    def format(self, report: APIReport) -> str:
        """
        Convert report to formatted JSON with enhanced enum support.
        
        Args:
            report: APIReport to format
            
        Returns:
            JSON string with proper indentation and enum information
        """
        report_dict = self._enhance_report_with_enum_info(report.to_dict())
        return json.dumps(report_dict, indent=2, default=str)
    
    def _enhance_report_with_enum_info(self, report_dict: dict) -> dict:
        """
        Enhance report dictionary with formatted enum information.
        
        Args:
            report_dict: Base report dictionary from APIReport.to_dict()
            
        Returns:
            Enhanced dictionary with formatted enum information
        """
        # Enhance endpoints with enum information
        if "endpoints" in report_dict:
            for endpoint in report_dict["endpoints"]:
                self._enhance_endpoint_enum_info(endpoint)
        
        return report_dict
    
    def _enhance_endpoint_enum_info(self, endpoint: dict) -> None:
        """
        Enhance endpoint dictionary with enum information.
        
        Args:
            endpoint: Endpoint dictionary to enhance
        """
        # Enhance parameter enum information
        if "parameters" in endpoint:
            for param in endpoint["parameters"]:
                self._enhance_parameter_enum_info(param)
        
        # Enhance response schema enum information
        if "responses" in endpoint:
            for status_code, response in endpoint["responses"].items():
                self._enhance_response_enum_info(response)
        
        # Enhance Pydantic model enum information in request/response schemas
        if "pydantic_enum_info" in endpoint and endpoint["pydantic_enum_info"]:
            self._enhance_pydantic_enum_info(endpoint)
    
    def _enhance_parameter_enum_info(self, param: dict) -> None:
        """
        Enhance parameter dictionary with enum information.
        
        Args:
            param: Parameter dictionary to enhance
        """
        if "enum_info" in param and param["enum_info"]:
            # Convert dict to EnumInfo object and format
            enum_info_obj = self._dict_to_enum_info(param["enum_info"])
            formatted_enum = self.enum_formatter.format_enum_for_json(enum_info_obj)
            
            # Add formatted enum information to constraints
            if "constraints" not in param:
                param["constraints"] = {}
            
            # Add enum values to constraints for backward compatibility
            if formatted_enum and "values" in formatted_enum:
                param["constraints"]["enum"] = [v["value"] for v in formatted_enum["values"]]
            
            # Add comprehensive enum metadata
            param["enum_metadata"] = formatted_enum
    
    def _enhance_response_enum_info(self, response: dict) -> None:
        """
        Enhance response dictionary with enum information.
        
        Args:
            response: Response dictionary to enhance
        """
        # Add enum information from response schema if available
        if "enum_info" in response and response["enum_info"]:
            # Format the enum information for each content type
            for content_type, enum_data in response["enum_info"].items():
                if isinstance(enum_data, dict) and "enum_fields" in enum_data:
                    # Format enum fields information
                    formatted_enum_fields = {}
                    for field_name, field_info in enum_data["enum_fields"].items():
                        if "enum_info" in field_info:
                            enum_info_obj = self._dict_to_enum_info(field_info["enum_info"])
                            formatted_enum_fields[field_name] = self.enum_formatter.format_enum_for_json(enum_info_obj)
                    
                    # Add formatted enum metadata to response
                    if "enum_metadata" not in response:
                        response["enum_metadata"] = {}
                    response["enum_metadata"][content_type] = {
                        "enum_fields": formatted_enum_fields
                    }
    
    def _enhance_pydantic_enum_info(self, endpoint: dict) -> None:
        """
        Enhance endpoint with Pydantic model enum information.
        
        Args:
            endpoint: Endpoint dictionary to enhance
        """
        pydantic_info = endpoint["pydantic_enum_info"]
        enhanced_pydantic_info = {}
        
        for model_name, model_info in pydantic_info.items():
            if "enum_fields" in model_info:
                enhanced_enum_fields = {}
                
                for field_name, field_info in model_info["enum_fields"].items():
                    if "enum_info" in field_info:
                        # Format the enum info
                        enum_info_obj = self._dict_to_enum_info(field_info["enum_info"])
                        formatted_enum = self.enum_formatter.format_enum_for_json(enum_info_obj)
                        
                        enhanced_enum_fields[field_name] = {
                            "field_type": field_info.get("field_type", "unknown"),
                            "enum_metadata": formatted_enum,
                            # Keep original enum_info for backward compatibility
                            "enum_info": field_info["enum_info"]
                        }
                
                enhanced_pydantic_info[model_name] = {
                    "enum_fields": enhanced_enum_fields
                }
        
        # Add enhanced enum metadata while preserving original
        endpoint["pydantic_enum_metadata"] = enhanced_pydantic_info
    
    def _dict_to_enum_info(self, enum_dict: dict):
        """
        Convert dictionary to EnumInfo object with error handling.
        
        Args:
            enum_dict: Dictionary containing enum information
            
        Returns:
            EnumInfo object or mock object with required attributes
        """
        try:
            from fastapi_report.models import EnumInfo, EnumValue
            
            if not isinstance(enum_dict, dict):
                logger.warning(f"Expected dict for enum info, got {type(enum_dict)}")
                return None
            
            # Convert enum values with error handling
            values = []
            if "values" in enum_dict:
                values_data = enum_dict["values"]
                if not isinstance(values_data, list):
                    logger.warning(f"Expected list for enum values, got {type(values_data)}")
                else:
                    for value_dict in values_data:
                        try:
                            if isinstance(value_dict, dict):
                                values.append(EnumValue(
                                    name=value_dict.get("name", ""),
                                    value=value_dict.get("value", ""),
                                    description=value_dict.get("description")
                                ))
                            else:
                                logger.warning(f"Expected dict for enum value, got {type(value_dict)}")
                                # Create fallback EnumValue
                                values.append(EnumValue(
                                    name=str(value_dict),
                                    value=value_dict,
                                    description=None
                                ))
                        except Exception as e:
                            logger.warning(f"Failed to create EnumValue from {value_dict}: {e}")
                            continue
            
            # Create EnumInfo object with fallbacks
            return EnumInfo(
                class_name=enum_dict.get("class_name", "Unknown"),
                module_name=enum_dict.get("module_name"),
                values=values,
                enum_type=enum_dict.get("enum_type", "Enum"),
                description=enum_dict.get("description")
            )
            
        except Exception as e:
            logger.error(f"Failed to convert dict to EnumInfo: {e}")
            # Return a minimal fallback EnumInfo
            from fastapi_report.models import EnumInfo
            return EnumInfo(
                class_name="ConversionError",
                module_name=None,
                values=[],
                enum_type="Enum",
                description=f"Failed to convert enum info: {str(e)}"
            )
    
    def get_file_extension(self) -> str:
        """Return JSON file extension."""
        return ".json"
