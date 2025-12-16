"""
FastAPI endpoint discovery component.

Extracts endpoint information from FastAPI applications using
route introspection and OpenAPI schema generation.
"""
import inspect
import logging
from typing import Any, Dict, List, Optional, get_type_hints, get_origin, get_args, Union
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.params import Query, Path, Body, Header
from fastapi_report.models import EndpointInfo, ParameterInfo, EnumInfo
from fastapi_report.discovery.enum_detector import EnumTypeDetector

# Configure logger for FastAPI discovery
logger = logging.getLogger(__name__)


class FastAPIDiscovery:
    """Discovers and extracts endpoint information from FastAPI applications."""
    
    def __init__(self, app: FastAPI):
        """
        Initialize discovery with a FastAPI application.
        
        Args:
            app: FastAPI application instance to analyze
        """
        self.app = app
        self._openapi_schema: Optional[Dict[str, Any]] = None
        self.enum_detector = EnumTypeDetector()
    
    def discover_endpoints(self) -> List[EndpointInfo]:
        """
        Extract all REST endpoints from FastAPI app.
        
        Returns:
            List of EndpointInfo objects representing all discovered endpoints
        """
        endpoints = []
        
        for route in self.app.routes:
            if isinstance(route, APIRoute):
                endpoint_info = self._extract_endpoint_info(route)
                endpoints.append(endpoint_info)
        
        return endpoints
    
    def get_openapi_schema(self) -> Dict[str, Any]:
        """
        Get complete OpenAPI specification.
        
        Returns:
            OpenAPI schema dictionary
        """
        if self._openapi_schema is None:
            self._openapi_schema = self.app.openapi()
        return self._openapi_schema
    
    def _extract_endpoint_info(self, route: APIRoute) -> EndpointInfo:
        """
        Extract endpoint information from a route.
        
        Args:
            route: FastAPI route to analyze
            
        Returns:
            EndpointInfo object with extracted metadata
        """
        # Get OpenAPI schema for additional metadata
        openapi_schema = self.get_openapi_schema()
        path_item = openapi_schema.get("paths", {}).get(route.path, {})
        
        # Get method-specific operation
        method = list(route.methods)[0].lower() if route.methods else "get"
        operation = path_item.get(method, {})
        
        # Extract parameters
        parameters = self.extract_parameters(route)
        
        # Extract response models
        responses = self.extract_response_models(route, operation)
        
        # Extract request body with enum discovery
        request_body = self._extract_request_body_with_enums(operation)
        
        # Discover enums in route's Pydantic models
        pydantic_enum_info = self._discover_enums_in_route_models(route)
        
        return EndpointInfo(
            path=route.path,
            method=method.upper(),
            operation_id=operation.get("operationId"),
            summary=operation.get("summary") or route.summary,
            description=operation.get("description") or route.description,
            tags=operation.get("tags", []),
            parameters=parameters,
            request_body=request_body,
            responses=responses,
            deprecated=operation.get("deprecated", False),
            pydantic_enum_info=pydantic_enum_info
        )
    
    def extract_parameters(self, route: APIRoute) -> List[ParameterInfo]:
        """
        Extract parameters from route signature.
        
        Args:
            route: FastAPI route to analyze
            
        Returns:
            List of ParameterInfo objects
        """
        parameters = []
        
        # Get function signature
        sig = inspect.signature(route.endpoint)
        type_hints = get_type_hints(route.endpoint)
        
        for param_name, param in sig.parameters.items():
            # Skip special parameters
            if param_name in ("self", "cls", "request", "response"):
                continue
            
            # Determine parameter type and extract metadata
            param_info = self._extract_parameter_info(
                param_name, param, type_hints.get(param_name)
            )
            
            if param_info:
                parameters.append(param_info)
        
        return parameters
    
    def _extract_parameter_info(
        self, 
        name: str, 
        param: inspect.Parameter,
        type_hint: Any
    ) -> Optional[ParameterInfo]:
        """
        Extract information from a single parameter.
        
        Args:
            name: Parameter name
            param: Parameter object from signature
            type_hint: Type hint for the parameter
            
        Returns:
            ParameterInfo object or None if parameter should be skipped
        """
        # Determine parameter location and metadata
        param_type = "query"  # default
        description = None
        constraints = {}
        required = param.default == inspect.Parameter.empty
        default = None if required else param.default
        
        # Check if parameter uses FastAPI parameter types
        if param.default != inspect.Parameter.empty:
            from pydantic_core import PydanticUndefined
            
            if isinstance(param.default, Query):
                param_type = "query"
                description = param.default.description
                constraints = self._extract_constraints(param.default)
                # Check if required using PydanticUndefined
                required = param.default.default is PydanticUndefined or param.default.default == ...
                default = None if required else param.default.default
            elif isinstance(param.default, Path):
                param_type = "path"
                description = param.default.description
                constraints = self._extract_constraints(param.default)
                required = True  # Path parameters are always required
                default = param.default.default if param.default.default not in (PydanticUndefined, ...) else None
            elif isinstance(param.default, Body):
                param_type = "body"
                description = param.default.description
                required = param.default.default is PydanticUndefined or param.default.default == ...
                default = None if required else param.default.default
            elif isinstance(param.default, Header):
                param_type = "header"
                description = param.default.description
                required = param.default.default is PydanticUndefined or param.default.default == ...
                default = None if required else param.default.default
        
        # Extract Python type
        python_type = self._get_type_string(type_hint)
        
        # Detect enum information
        enum_info = None
        if type_hint is not None:
            # Check for enum in type hint
            type_enum_info = self._detect_enum_in_type_hint(type_hint)
            
            # Extract enum constraints from FastAPI field
            field_enum_constraints = self._extract_enum_constraints(param.default, type_hint)
            
            # Merge enum information from both sources
            if type_enum_info or field_enum_constraints:
                enum_info = self._merge_enum_constraints(field_enum_constraints, type_enum_info)
        
        return ParameterInfo(
            name=name,
            param_type=param_type,
            python_type=python_type,
            required=required,
            default=default,
            description=description,
            constraints=constraints,
            enum_info=enum_info
        )
    
    def _extract_constraints(self, field) -> Dict[str, Any]:
        """
        Extract validation constraints from FastAPI field.
        
        Args:
            field: FastAPI parameter field (Query, Path, etc.)
            
        Returns:
            Dictionary of constraints
        """
        constraints = {}
        
        # Try to get constraints from metadata (Pydantic v2)
        if hasattr(field, 'metadata'):
            for metadata_item in field.metadata:
                if hasattr(metadata_item, 'ge') and metadata_item.ge is not None:
                    constraints['ge'] = metadata_item.ge
                if hasattr(metadata_item, 'le') and metadata_item.le is not None:
                    constraints['le'] = metadata_item.le
                if hasattr(metadata_item, 'gt') and metadata_item.gt is not None:
                    constraints['gt'] = metadata_item.gt
                if hasattr(metadata_item, 'lt') and metadata_item.lt is not None:
                    constraints['lt'] = metadata_item.lt
                if hasattr(metadata_item, 'min_length') and metadata_item.min_length is not None:
                    constraints['min_length'] = metadata_item.min_length
                if hasattr(metadata_item, 'max_length') and metadata_item.max_length is not None:
                    constraints['max_length'] = metadata_item.max_length
                if hasattr(metadata_item, 'pattern') and metadata_item.pattern is not None:
                    constraints['pattern'] = metadata_item.pattern
        
        # Fallback to direct attributes (Pydantic v1 style)
        if hasattr(field, 'ge') and field.ge is not None:
            constraints['ge'] = field.ge
        if hasattr(field, 'le') and field.le is not None:
            constraints['le'] = field.le
        if hasattr(field, 'gt') and field.gt is not None:
            constraints['gt'] = field.gt
        if hasattr(field, 'lt') and field.lt is not None:
            constraints['lt'] = field.lt
        if hasattr(field, 'min_length') and field.min_length is not None:
            constraints['min_length'] = field.min_length
        if hasattr(field, 'max_length') and field.max_length is not None:
            constraints['max_length'] = field.max_length
        if hasattr(field, 'pattern') and field.pattern is not None:
            constraints['pattern'] = field.pattern
        if hasattr(field, 'enum') and field.enum is not None:
            constraints['enum'] = list(field.enum)
        
        # Check json_schema_extra for enum constraints
        if hasattr(field, 'json_schema_extra') and field.json_schema_extra:
            if isinstance(field.json_schema_extra, dict) and 'enum' in field.json_schema_extra:
                constraints['enum'] = list(field.json_schema_extra['enum'])
        
        return constraints
    
    def _extract_enum_constraints(self, field, type_hint: Any) -> Dict[str, Any]:
        """
        Extract enum constraints from FastAPI field and type hint.
        
        Args:
            field: FastAPI parameter field (Query, Path, etc.)
            type_hint: Type hint for the parameter
            
        Returns:
            Dictionary containing enum constraint information
        """
        enum_constraints = {}
        
        # Extract enum from FastAPI field if present
        if hasattr(field, 'enum') and field.enum is not None:
            enum_constraints['field_enum'] = list(field.enum)
        
        # Check json_schema_extra for enum constraints
        if hasattr(field, 'json_schema_extra') and field.json_schema_extra:
            if isinstance(field.json_schema_extra, dict) and 'enum' in field.json_schema_extra:
                enum_constraints['field_enum'] = list(field.json_schema_extra['enum'])
        
        # Check metadata for enum constraints (Pydantic v2)
        if hasattr(field, 'metadata'):
            for metadata_item in field.metadata:
                if hasattr(metadata_item, 'enum') and metadata_item.enum is not None:
                    enum_constraints['field_enum'] = list(metadata_item.enum)
        
        return enum_constraints
    
    def _detect_enum_in_type_hint(self, type_hint: Any) -> Optional[EnumInfo]:
        """
        Detect enum information from type hint with comprehensive error handling.
        
        Args:
            type_hint: Python type hint to analyze
            
        Returns:
            EnumInfo object if enum is detected, None otherwise
        """
        if not self.enum_detector.is_enum_type(type_hint):
            return None
        
        try:
            return self.enum_detector.extract_enum_info(type_hint)
        except ValueError as e:
            logger.warning(f"Failed to extract enum info from type hint {type_hint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error extracting enum info from type hint {type_hint}: {e}")
            return None
    
    def _merge_enum_constraints(self, field_enum: Dict[str, Any], type_enum: Optional[EnumInfo]) -> Optional[EnumInfo]:
        """
        Merge enum constraints from FastAPI field and type hint with validation.
        
        Args:
            field_enum: Enum constraints from FastAPI field
            type_enum: EnumInfo from type hint analysis
            
        Returns:
            Merged EnumInfo object, prioritizing FastAPI field definitions
        """
        try:
            # If no enum information from either source, return None
            if not field_enum and not type_enum:
                return None
            
            # If only type enum info is available, use it
            if not field_enum and type_enum:
                logger.debug(f"Using type enum info for {type_enum.class_name}")
                return type_enum
            
            # If only field enum info is available, create basic EnumInfo
            if field_enum and not type_enum:
                from fastapi_report.models import EnumValue
                
                field_enum_values = field_enum.get('field_enum', [])
                if not field_enum_values:
                    logger.warning("Field enum constraint found but no values provided")
                    return None
                
                enum_values = []
                
                for value in field_enum_values:
                    try:
                        enum_values.append(EnumValue(
                            name=str(value),  # Use string representation as name
                            value=value,
                            description=None
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to create EnumValue for {value}: {e}")
                        continue
                
                if not enum_values:
                    logger.warning("No valid enum values could be created from field constraints")
                    return None
                
                return EnumInfo(
                    class_name="FieldEnum",
                    module_name=None,
                    values=enum_values,
                    enum_type="Enum",
                    description="Enum values from FastAPI field constraints"
                )
            
            # Both sources available - merge with validation
            if field_enum and type_enum:
                field_enum_values = field_enum.get('field_enum', [])
                type_enum_values = [ev.value for ev in type_enum.values]
                
                # Validate constraints compatibility
                if self.enum_detector.validate_enum_constraints(field_enum_values, type_enum_values):
                    if set(field_enum_values) == set(type_enum_values):
                        # Values match exactly, use type enum info (more complete)
                        logger.debug(f"Enum constraints match exactly for {type_enum.class_name}")
                        return type_enum
                    else:
                        # Compatible but different, prioritize FastAPI field
                        logger.info(
                            f"Using FastAPI field enum values for {type_enum.class_name}: "
                            f"field={field_enum_values}, type={type_enum_values}"
                        )
                else:
                    # Incompatible constraints - log error and use field values
                    logger.error(
                        f"Incompatible enum constraints for {type_enum.class_name}: "
                        f"field={field_enum_values}, type={type_enum_values}. "
                        f"Using FastAPI field definition as fallback."
                    )
                
                # Create merged enum info with field values
                from fastapi_report.models import EnumValue
                enum_values = []
                
                for value in field_enum_values:
                    try:
                        enum_values.append(EnumValue(
                            name=str(value),
                            value=value,
                            description=None
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to create EnumValue for {value}: {e}")
                        continue
                
                if not enum_values:
                    logger.warning(f"No valid enum values from field constraints for {type_enum.class_name}")
                    return type_enum  # Fallback to type enum
                
                # Use type enum metadata but field enum values
                return EnumInfo(
                    class_name=type_enum.class_name,
                    module_name=type_enum.module_name,
                    values=enum_values,
                    enum_type=type_enum.enum_type,
                    description=type_enum.description
                )
            
        except Exception as e:
            logger.error(f"Failed to merge enum constraints: {e}")
            # Return type enum as fallback if available
            if type_enum:
                logger.info(f"Falling back to type enum info for {type_enum.class_name}")
                return type_enum
        
        return None
    
    def _get_type_string(self, type_hint: Any) -> str:
        """
        Convert Python type hint to string representation.
        
        Args:
            type_hint: Python type hint
            
        Returns:
            String representation of the type
        """
        if type_hint is None or type_hint == inspect.Parameter.empty:
            return "Any"
        
        # Handle Optional types - both old and new syntax
        origin = get_origin(type_hint)
        
        # Handle typing.Union (old syntax)
        if origin is Union:
            args = get_args(type_hint)
            if type(None) in args:
                # This is Optional[T]
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    inner_type = non_none_args[0]
                    # Check if inner type is enum
                    if self.enum_detector.is_enum_type(inner_type):
                        return f"Optional[{self.enum_detector.get_enum_type_string(inner_type)}]"
                    return f"Optional[{self._get_type_string(inner_type)}]"
                else:
                    return f"Union[{', '.join(self._get_type_string(arg) for arg in args)}]"
            else:
                return f"Union[{', '.join(self._get_type_string(arg) for arg in args)}]"
        
        # Handle types.UnionType (new Python 3.10+ syntax: T | None)
        import types
        if hasattr(types, 'UnionType') and isinstance(type_hint, types.UnionType):
            args = get_args(type_hint)
            if type(None) in args:
                # This is Optional[T] (T | None)
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    inner_type = non_none_args[0]
                    # Check if inner type is enum
                    if self.enum_detector.is_enum_type(inner_type):
                        return f"Optional[{self.enum_detector.get_enum_type_string(inner_type)}]"
                    return f"Optional[{self._get_type_string(inner_type)}]"
                else:
                    return f"Union[{', '.join(self._get_type_string(arg) for arg in args)}]"
            else:
                return f"Union[{', '.join(self._get_type_string(arg) for arg in args)}]"
        
        # Handle enum types
        if self.enum_detector.is_enum_type(type_hint):
            return self.enum_detector.get_enum_type_string(type_hint)
        
        # Handle generic types
        if origin is not None:
            args = get_args(type_hint)
            if args:
                args_str = ', '.join(self._get_type_string(arg) for arg in args)
                return f"{origin.__name__}[{args_str}]"
            return origin.__name__
        
        # Handle basic types
        if hasattr(type_hint, '__name__'):
            return type_hint.__name__
        
        return str(type_hint)
    
    def extract_response_models(
        self, 
        route: APIRoute,
        operation: Dict[str, Any]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Extract response schemas from route with enum discovery.
        
        Args:
            route: FastAPI route to analyze
            operation: OpenAPI operation object
            
        Returns:
            Dictionary mapping status codes to response schemas with enum information
        """
        responses = {}
        
        # Get responses from OpenAPI schema
        openapi_responses = operation.get("responses", {})
        
        for status_code, response_data in openapi_responses.items():
            try:
                status_int = int(status_code)
                response_info = {
                    "description": response_data.get("description", ""),
                    "content": response_data.get("content", {})
                }
                
                # Discover enums in response schemas
                content = response_data.get("content", {})
                for media_type, media_info in content.items():
                    schema = media_info.get("schema", {})
                    if schema:
                        enum_info = self._discover_enums_in_schema(schema)
                        if enum_info:
                            if "enum_info" not in response_info:
                                response_info["enum_info"] = {}
                            response_info["enum_info"][media_type] = enum_info
                
                responses[status_int] = response_info
            except ValueError:
                # Skip non-numeric status codes (like 'default')
                continue
        
        return responses
    
    def _extract_request_body_with_enums(self, operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract request body information with enum discovery.
        
        Args:
            operation: OpenAPI operation object
            
        Returns:
            Request body information with enum metadata, or None if no request body
        """
        request_body = operation.get("requestBody")
        if not request_body:
            return None
        
        # Create a copy to avoid modifying the original
        request_body_info = dict(request_body)
        
        # Discover enums in request body schemas
        content = request_body.get("content", {})
        for media_type, media_info in content.items():
            schema = media_info.get("schema", {})
            if schema:
                enum_info = self._discover_enums_in_schema(schema)
                if enum_info:
                    if "enum_info" not in request_body_info:
                        request_body_info["enum_info"] = {}
                    request_body_info["enum_info"][media_type] = enum_info
        
        return request_body_info
    
    def _discover_enums_in_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively discover enum information in OpenAPI schema with error handling.
        
        Args:
            schema: OpenAPI schema object to analyze
            
        Returns:
            Dictionary containing discovered enum information
        """
        if not isinstance(schema, dict):
            logger.warning(f"Expected dict schema, got {type(schema)}")
            return {}
        
        enum_info = {}
        
        try:
            # Check if this schema itself defines an enum
            if "enum" in schema:
                enum_values = schema["enum"]
                if not isinstance(enum_values, list):
                    logger.warning(f"Schema enum values should be a list, got {type(enum_values)}")
                else:
                    enum_info["direct_enum"] = {
                        "values": enum_values,
                        "type": schema.get("type", "string")
                    }
            
            # Handle object properties
            if schema.get("type") == "object" and "properties" in schema:
                try:
                    properties_enum_info = {}
                    properties = schema["properties"]
                    
                    if not isinstance(properties, dict):
                        logger.warning(f"Schema properties should be a dict, got {type(properties)}")
                    else:
                        for prop_name, prop_schema in properties.items():
                            try:
                                prop_enum_info = self._discover_enums_in_schema(prop_schema)
                                if prop_enum_info:
                                    properties_enum_info[prop_name] = prop_enum_info
                            except Exception as e:
                                logger.warning(f"Failed to discover enums in property {prop_name}: {e}")
                                continue
                    
                    if properties_enum_info:
                        enum_info["properties"] = properties_enum_info
                        
                except Exception as e:
                    logger.warning(f"Failed to process object properties: {e}")
            
            # Handle array items
            if schema.get("type") == "array" and "items" in schema:
                try:
                    items_enum_info = self._discover_enums_in_schema(schema["items"])
                    if items_enum_info:
                        enum_info["items"] = items_enum_info
                except Exception as e:
                    logger.warning(f"Failed to discover enums in array items: {e}")
            
            # Handle oneOf, anyOf, allOf schemas
            for schema_type in ["oneOf", "anyOf", "allOf"]:
                if schema_type in schema:
                    try:
                        schema_list = schema[schema_type]
                        if not isinstance(schema_list, list):
                            logger.warning(f"Schema {schema_type} should be a list, got {type(schema_list)}")
                            continue
                            
                        schema_list_enum_info = {}
                        for i, sub_schema in enumerate(schema_list):
                            try:
                                sub_enum_info = self._discover_enums_in_schema(sub_schema)
                                if sub_enum_info:
                                    schema_list_enum_info[f"{schema_type}_{i}"] = sub_enum_info
                            except Exception as e:
                                logger.warning(f"Failed to discover enums in {schema_type}[{i}]: {e}")
                                continue
                        
                        if schema_list_enum_info:
                            enum_info[schema_type] = schema_list_enum_info
                            
                    except Exception as e:
                        logger.warning(f"Failed to process {schema_type} schemas: {e}")
            
            # Handle $ref schemas by resolving references
            if "$ref" in schema:
                try:
                    ref_enum_info = self._discover_enums_in_ref_schema(schema["$ref"])
                    if ref_enum_info:
                        enum_info["ref"] = ref_enum_info
                except Exception as e:
                    logger.warning(f"Failed to resolve schema reference {schema.get('$ref')}: {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error discovering enums in schema: {e}")
            return {}
        
        return enum_info
    
    def _discover_enums_in_ref_schema(self, ref: str) -> Dict[str, Any]:
        """
        Discover enums in referenced schema with error handling.
        
        Args:
            ref: Schema reference (e.g., "#/components/schemas/UserStatus")
            
        Returns:
            Dictionary containing discovered enum information
        """
        try:
            # Get the OpenAPI schema to resolve references
            openapi_schema = self.get_openapi_schema()
            
            if not openapi_schema:
                logger.warning("No OpenAPI schema available for reference resolution")
                return {}
            
            # Parse the reference path
            if not isinstance(ref, str) or not ref.startswith("#/"):
                logger.warning(f"Invalid schema reference format: {ref}")
                return {}
            
            ref_path = ref[2:].split("/")  # Remove "#/" and split
            
            # Navigate to the referenced schema
            current = openapi_schema
            for path_part in ref_path:
                if isinstance(current, dict) and path_part in current:
                    current = current[path_part]
                else:
                    # Reference not found
                    logger.warning(f"Schema reference not found: {ref} (failed at {path_part})")
                    return {}
            
            # Recursively discover enums in the referenced schema
            if isinstance(current, dict):
                return self._discover_enums_in_schema(current)
            else:
                logger.warning(f"Referenced schema is not a dict: {ref}")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to resolve schema reference {ref}: {e}")
            return {}
    
    def _discover_enums_in_pydantic_model(self, model_class) -> Dict[str, Any]:
        """
        Discover enum fields in Pydantic models with comprehensive error handling.
        
        Args:
            model_class: Pydantic model class to analyze
            
        Returns:
            Dictionary containing discovered enum information
        """
        enum_info = {}
        
        try:
            # Check if this is a Pydantic model
            if not hasattr(model_class, 'model_fields') and not hasattr(model_class, '__fields__'):
                logger.debug(f"Class {model_class} is not a Pydantic model")
                return enum_info
            
            model_name = getattr(model_class, '__name__', str(model_class))
            logger.debug(f"Discovering enums in Pydantic model: {model_name}")
            
            # Handle Pydantic v2
            if hasattr(model_class, 'model_fields'):
                try:
                    fields = model_class.model_fields
                    if not isinstance(fields, dict):
                        logger.warning(f"Model fields should be a dict for {model_name}")
                        return enum_info
                        
                    for field_name, field_info in fields.items():
                        try:
                            # Get the field annotation/type
                            field_type = field_info.annotation if hasattr(field_info, 'annotation') else None
                            
                            if field_type and self.enum_detector.is_enum_type(field_type):
                                try:
                                    field_enum_info = self.enum_detector.extract_enum_info(field_type)
                                    enum_info[field_name] = {
                                        "enum_info": field_enum_info.to_dict(),
                                        "field_type": "pydantic_v2"
                                    }
                                    logger.debug(f"Found enum field {field_name} in {model_name}")
                                except Exception as e:
                                    logger.warning(f"Failed to extract enum info for field {field_name} in {model_name}: {e}")
                                    continue
                            
                            # Recursively check nested models and generic types
                            elif field_type:
                                try:
                                    nested_enum_info = self._discover_enums_in_type(field_type)
                                    if nested_enum_info:
                                        enum_info[field_name] = nested_enum_info
                                        logger.debug(f"Found nested enum in field {field_name} of {model_name}")
                                except Exception as e:
                                    logger.warning(f"Failed to discover nested enums in field {field_name} of {model_name}: {e}")
                                    continue
                                    
                        except Exception as e:
                            logger.warning(f"Error processing field {field_name} in {model_name}: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Failed to process Pydantic v2 fields for {model_name}: {e}")
            
            # Handle Pydantic v1 (fallback)
            elif hasattr(model_class, '__fields__'):
                try:
                    fields = model_class.__fields__
                    if not isinstance(fields, dict):
                        logger.warning(f"Model fields should be a dict for {model_name}")
                        return enum_info
                        
                    for field_name, field_info in fields.items():
                        try:
                            field_type = field_info.type_
                            
                            if self.enum_detector.is_enum_type(field_type):
                                try:
                                    field_enum_info = self.enum_detector.extract_enum_info(field_type)
                                    enum_info[field_name] = {
                                        "enum_info": field_enum_info.to_dict(),
                                        "field_type": "pydantic_v1"
                                    }
                                    logger.debug(f"Found enum field {field_name} in {model_name}")
                                except Exception as e:
                                    logger.warning(f"Failed to extract enum info for field {field_name} in {model_name}: {e}")
                                    continue
                            
                            # Recursively check nested models and generic types
                            elif field_type:
                                try:
                                    nested_enum_info = self._discover_enums_in_type(field_type)
                                    if nested_enum_info:
                                        enum_info[field_name] = nested_enum_info
                                        logger.debug(f"Found nested enum in field {field_name} of {model_name}")
                                except Exception as e:
                                    logger.warning(f"Failed to discover nested enums in field {field_name} of {model_name}: {e}")
                                    continue
                                    
                        except Exception as e:
                            logger.warning(f"Error processing field {field_name} in {model_name}: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Failed to process Pydantic v1 fields for {model_name}: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error discovering enums in Pydantic model {getattr(model_class, '__name__', str(model_class))}: {e}")
            return {}
        
        return enum_info
    
    def _discover_enums_in_route_models(self, route: APIRoute) -> Dict[str, Any]:
        """
        Discover enum information in Pydantic models used by the route.
        
        Args:
            route: FastAPI route to analyze
            
        Returns:
            Dictionary containing discovered enum information from Pydantic models
        """
        enum_info = {}
        
        try:
            # Get function signature and type hints
            sig = inspect.signature(route.endpoint)
            type_hints = get_type_hints(route.endpoint)
            
            # Check parameters for Pydantic models
            for param_name, param in sig.parameters.items():
                if param_name in ("self", "cls", "request", "response"):
                    continue
                
                param_type = type_hints.get(param_name)
                if param_type:
                    # Check if this is a Pydantic model
                    if (hasattr(param_type, 'model_fields') or hasattr(param_type, '__fields__')):
                        model_enum_info = self._discover_enums_in_pydantic_model(param_type)
                        if model_enum_info:
                            enum_info[f"parameter_{param_name}"] = {
                                "model_name": getattr(param_type, '__name__', str(param_type)),
                                "enum_fields": model_enum_info
                            }
            
            # Check return type annotation for response models
            return_annotation = sig.return_annotation
            if return_annotation and return_annotation != inspect.Signature.empty:
                # Handle Union types (like Union[Model, None])
                origin = get_origin(return_annotation)
                if origin is Union:
                    args = get_args(return_annotation)
                    for arg in args:
                        if arg is not type(None) and (hasattr(arg, 'model_fields') or hasattr(arg, '__fields__')):
                            model_enum_info = self._discover_enums_in_pydantic_model(arg)
                            if model_enum_info:
                                enum_info[f"return_type_{arg.__name__}"] = {
                                    "model_name": arg.__name__,
                                    "enum_fields": model_enum_info
                                }
                elif hasattr(return_annotation, 'model_fields') or hasattr(return_annotation, '__fields__'):
                    model_enum_info = self._discover_enums_in_pydantic_model(return_annotation)
                    if model_enum_info:
                        enum_info[f"return_type_{return_annotation.__name__}"] = {
                            "model_name": return_annotation.__name__,
                            "enum_fields": model_enum_info
                        }
            
            # Also check for response_model in route definition
            if hasattr(route, 'response_model') and route.response_model:
                response_model = route.response_model
                if hasattr(response_model, 'model_fields') or hasattr(response_model, '__fields__'):
                    model_enum_info = self._discover_enums_in_pydantic_model(response_model)
                    if model_enum_info:
                        enum_info[f"response_model_{response_model.__name__}"] = {
                            "model_name": response_model.__name__,
                            "enum_fields": model_enum_info
                        }
        
        except Exception:
            # If anything goes wrong with route introspection, return empty dict
            pass
        
        return enum_info
    
    def _discover_enums_in_type(self, type_hint: Any) -> Dict[str, Any]:
        """
        Discover enum information in any type, including generic types.
        
        Args:
            type_hint: Type hint to analyze
            
        Returns:
            Dictionary containing discovered enum information
        """
        # Check if it's directly an enum
        if self.enum_detector.is_enum_type(type_hint):
            try:
                enum_info = self.enum_detector.extract_enum_info(type_hint)
                return {
                    "enum_info": enum_info.to_dict(),
                    "field_type": "direct_enum"
                }
            except ValueError:
                return {}
        
        # Check if it's a Pydantic model
        if hasattr(type_hint, 'model_fields') or hasattr(type_hint, '__fields__'):
            nested_enum_info = self._discover_enums_in_pydantic_model(type_hint)
            if nested_enum_info:
                return {
                    "nested": nested_enum_info,
                    "field_type": "nested_model"
                }
        
        # Handle generic types (List, Optional, Union, etc.)
        origin = get_origin(type_hint)
        if origin is not None:
            args = get_args(type_hint)
            
            # Handle List[Model] or List[Enum]
            if origin in (list, List):
                if args:
                    item_type = args[0]
                    item_enum_info = self._discover_enums_in_type(item_type)
                    if item_enum_info:
                        return {
                            "list_item": item_enum_info,
                            "field_type": "list"
                        }
            
            # Handle Optional[Model] or Optional[Enum]
            elif origin is Union:
                # Check if this is Optional[T] (Union[T, None])
                if type(None) in args:
                    non_none_args = [arg for arg in args if arg is not type(None)]
                    if len(non_none_args) == 1:
                        inner_type = non_none_args[0]
                        inner_enum_info = self._discover_enums_in_type(inner_type)
                        if inner_enum_info:
                            return {
                                "optional": inner_enum_info,
                                "field_type": "optional"
                            }
                
                # Handle other Union types
                union_enum_info = {}
                for i, arg in enumerate(args):
                    if arg is not type(None):
                        arg_enum_info = self._discover_enums_in_type(arg)
                        if arg_enum_info:
                            union_enum_info[f"union_{i}"] = arg_enum_info
                
                if union_enum_info:
                    return {
                        "union": union_enum_info,
                        "field_type": "union"
                    }
        
        return {}
