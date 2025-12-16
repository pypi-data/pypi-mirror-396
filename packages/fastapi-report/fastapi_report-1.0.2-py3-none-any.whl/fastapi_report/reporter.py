"""
Main reporter class for discovering and documenting FastAPI endpoints.
"""
import importlib
import sys
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi_report.models import APIReport
from fastapi_report.discovery import FastAPIDiscovery, MCPDiscovery
from fastapi_report.formatters import JSONFormatter, MarkdownFormatter, HTMLFormatter


class EndpointReporter:
    """Main reporter class for discovering and documenting FastAPI endpoints."""
    
    def __init__(self, server_source: str):
        """
        Initialize reporter with a server module or URL.
        
        Args:
            server_source: Python module name or HTTP URL
        """
        self.server_source = server_source
        
        # Check if it's a URL or module name
        if server_source.startswith(('http://', 'https://')):
            self.mode = 'url'
            self.base_url = server_source.rstrip('/')
            self.app = None
            self.mcp = None
        else:
            self.mode = 'module'
            self.server_module = server_source
            self.app = self.load_server(server_source)
            self.mcp = self.load_mcp(self.app)
    
    def load_server(self, module_name: str) -> FastAPI:
        """
        Dynamically import and return FastAPI app.
        
        Args:
            module_name: Python module name to import
            
        Returns:
            FastAPI application instance
            
        Raises:
            SystemExit: If module cannot be loaded or doesn't contain FastAPI app
        """
        try:
            module = importlib.import_module(module_name)
        except (ImportError, ModuleNotFoundError) as e:
            print(f"Error: Could not import module '{module_name}': {e}", file=sys.stderr)
            sys.exit(1)
        
        # Try to find FastAPI app instance
        app = None
        for attr_name in ['app', 'application', 'api']:
            if hasattr(module, attr_name):
                attr = getattr(module, attr_name)
                if isinstance(attr, FastAPI):
                    app = attr
                    break
        
        if app is None:
            print(f"Error: No FastAPI app found in module '{module_name}'", file=sys.stderr)
            print("Expected to find 'app', 'application', or 'api' variable", file=sys.stderr)
            sys.exit(1)
        
        return app
    
    def load_mcp(self, app: FastAPI) -> Optional[Any]:
        """
        Extract MCP instance if available.
        
        Args:
            app: FastAPI application
            
        Returns:
            MCP instance or None if not available
        """
        # Try to find MCP instance in app
        if hasattr(app, 'mcp'):
            return app.mcp
        
        # Try to find in app.state
        if hasattr(app, 'state') and hasattr(app.state, 'mcp'):
            return app.state.mcp
        
        # Check module-level mcp variable
        if self.mode == 'module':
            try:
                module = importlib.import_module(self.server_module)
                if hasattr(module, 'mcp'):
                    return module.mcp
            except Exception:
                pass
        
        return None
    
    def _extract_enum_from_openapi_schema(self, schema: Dict[str, Any], openapi_spec: Dict[str, Any]) -> Optional[Any]:
        """
        Extract enum information from OpenAPI schema.
        
        Args:
            schema: OpenAPI parameter schema
            openapi_spec: Full OpenAPI specification for resolving $ref
            
        Returns:
            EnumInfo object if enum is found, None otherwise
        """
        from fastapi_report.models import EnumInfo, EnumValue
        
        # Direct enum in schema
        if 'enum' in schema:
            enum_values = []
            for value in schema['enum']:
                enum_values.append(EnumValue(name=str(value).upper(), value=value))
            
            return EnumInfo(
                class_name=schema.get('title', 'Enum'),
                module_name=None,
                values=enum_values,
                enum_type='Enum',
                description=schema.get('description')
            )
        
        # Check anyOf structure (for Optional[Enum] types)
        if 'anyOf' in schema:
            for any_of_item in schema['anyOf']:
                # Handle $ref references
                if '$ref' in any_of_item:
                    resolved_schema = self._resolve_ref(any_of_item['$ref'], openapi_spec)
                    if resolved_schema and 'enum' in resolved_schema:
                        enum_values = []
                        for value in resolved_schema['enum']:
                            enum_values.append(EnumValue(name=str(value).upper(), value=value))
                        
                        return EnumInfo(
                            class_name=resolved_schema.get('title', schema.get('title', 'Enum')),
                            module_name=None,
                            values=enum_values,
                            enum_type='StrEnum' if all(isinstance(v, str) for v in resolved_schema['enum']) else 'Enum',
                            description=resolved_schema.get('description', schema.get('description'))
                        )
                
                # Handle direct enum
                elif 'enum' in any_of_item:
                    enum_values = []
                    for value in any_of_item['enum']:
                        enum_values.append(EnumValue(name=str(value).upper(), value=value))
                    
                    return EnumInfo(
                        class_name=any_of_item.get('title', schema.get('title', 'Enum')),
                        module_name=None,
                        values=enum_values,
                        enum_type='StrEnum' if all(isinstance(v, str) for v in any_of_item['enum']) else 'Enum',
                        description=any_of_item.get('description', schema.get('description'))
                    )
        
        return None
    
    def _get_python_type_from_schema(self, schema: Dict[str, Any], openapi_spec: Dict[str, Any]) -> str:
        """
        Determine Python type string from OpenAPI schema.
        
        Args:
            schema: OpenAPI parameter schema
            openapi_spec: Full OpenAPI specification for resolving $ref
            
        Returns:
            Python type string
        """
        # Check for enum first
        enum_info = self._extract_enum_from_openapi_schema(schema, openapi_spec)
        if enum_info:
            # Check if it's optional (has null in anyOf)
            if 'anyOf' in schema:
                has_null = any(item.get('type') == 'null' for item in schema['anyOf'])
                if has_null:
                    return f"Optional[Enum[{enum_info.class_name}]]"
            return f"Enum[{enum_info.class_name}]"
        
        # Handle anyOf for optional types
        if 'anyOf' in schema:
            types = []
            has_null = False
            for item in schema['anyOf']:
                if item.get('type') == 'null':
                    has_null = True
                else:
                    item_type = item.get('type', 'any')
                    types.append(item_type)
            
            if has_null and len(types) == 1:
                return f"Optional[{types[0]}]"
            elif types:
                return ' | '.join(types)
        
        # Basic type
        return schema.get('type', 'any')
    
    def _resolve_ref(self, ref: str, openapi_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Resolve a $ref reference in OpenAPI schema.
        
        Args:
            ref: Reference string like "#/components/schemas/HealthStatus"
            openapi_spec: Full OpenAPI specification
            
        Returns:
            Resolved schema object or None if not found
        """
        if not ref.startswith('#/'):
            return None
        
        # Parse the reference path
        path_parts = ref[2:].split('/')  # Remove '#/' and split
        
        # Navigate through the spec
        current = openapi_spec
        for part in path_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current if isinstance(current, dict) else None
    
    def generate_report(self) -> APIReport:
        """
        Run discovery and create report.
        
        Returns:
            APIReport with all discovered information
        """
        if self.mode == 'url':
            return self._generate_report_from_url()
        else:
            return self._generate_report_from_module()
    
    def _generate_report_from_module(self) -> APIReport:
        """Generate report from loaded Python module."""
        # Discover REST endpoints
        fastapi_discovery = FastAPIDiscovery(self.app)
        endpoints = fastapi_discovery.discover_endpoints()
        openapi_spec = fastapi_discovery.get_openapi_schema()
        
        # Discover MCP tools
        mcp_tools = []
        if self.mcp is not None:
            try:
                mcp_discovery = MCPDiscovery(self.mcp)
                mcp_tools = mcp_discovery.discover_tools()
            except Exception as e:
                print(f"Warning: MCP tool discovery failed: {e}", file=sys.stderr)
        
        # Create report
        report = APIReport(
            server_name=openapi_spec.get('info', {}).get('title', 'API'),
            server_version=openapi_spec.get('info', {}).get('version', '1.0.0'),
            endpoints=endpoints,
            mcp_tools=mcp_tools,
            openapi_spec=openapi_spec
        )
        
        return report
    
    def _generate_report_from_url(self) -> APIReport:
        """Generate report from running server URL."""
        try:
            # Fetch OpenAPI schema from /openapi.json
            openapi_url = f"{self.base_url}/openapi.json"
            response = requests.get(openapi_url, timeout=10)
            response.raise_for_status()
            openapi_spec = response.json()
            
            # Parse endpoints from OpenAPI spec
            from fastapi_report.models import EndpointInfo, ParameterInfo
            endpoints = []
            
            for path, path_item in openapi_spec.get('paths', {}).items():
                for method, operation in path_item.items():
                    if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                        continue
                    
                    # Extract parameters
                    parameters = []
                    for param in operation.get('parameters', []):
                        schema = param.get('schema', {})
                        
                        # Extract enum information from OpenAPI schema
                        enum_info = self._extract_enum_from_openapi_schema(schema, openapi_spec)
                        
                        # Determine python type
                        python_type = self._get_python_type_from_schema(schema, openapi_spec)
                        
                        # Extract constraints including enum values
                        constraints = {}
                        if 'enum' in schema:
                            constraints['enum'] = schema['enum']
                        elif enum_info and enum_info.values:
                            constraints['enum'] = [v.value for v in enum_info.values]
                        
                        param_info = ParameterInfo(
                            name=param.get('name', ''),
                            param_type=param.get('in', 'query'),
                            python_type=python_type,
                            required=param.get('required', False),
                            default=schema.get('default'),
                            description=param.get('description'),
                            constraints=constraints,
                            enum_info=enum_info
                        )
                        parameters.append(param_info)
                    
                    # Create endpoint info
                    endpoint = EndpointInfo(
                        path=path,
                        method=method.upper(),
                        operation_id=operation.get('operationId'),
                        summary=operation.get('summary'),
                        description=operation.get('description'),
                        tags=operation.get('tags', []),
                        parameters=parameters,
                        request_body=operation.get('requestBody'),
                        responses=operation.get('responses', {}),
                        deprecated=operation.get('deprecated', False)
                    )
                    endpoints.append(endpoint)
            
            # Discover MCP tools from URL using MCP protocol
            mcp_tools = []
            try:
                mcp_discovery = MCPDiscovery(base_url=self.base_url)
                mcp_tools = mcp_discovery.discover_tools()
            except Exception as e:
                print(f"Warning: MCP tool discovery failed: {e}", file=sys.stderr)
            
            # Create report
            report = APIReport(
                server_name=openapi_spec.get('info', {}).get('title', 'API'),
                server_version=openapi_spec.get('info', {}).get('version', '1.0.0'),
                endpoints=endpoints,
                mcp_tools=mcp_tools,
                openapi_spec=openapi_spec
            )
            
            return report
            
        except requests.RequestException as e:
            print(f"Error: Could not fetch OpenAPI spec from {self.base_url}: {e}", file=sys.stderr)
            print("Make sure the server is running and accessible", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: Failed to parse OpenAPI spec: {e}", file=sys.stderr)
            sys.exit(1)
    
    def output_report(self, report: APIReport, formats: List[str], output_path: str):
        """
        Format and write report to files.
        
        Args:
            report: APIReport to output
            formats: List of format names ('json', 'md', 'html')
            output_path: Directory path for output files
        """
        # Create output directory
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Format mapping
        formatters = {
            'json': JSONFormatter(),
            'md': MarkdownFormatter(),
            'html': HTMLFormatter()
        }
        
        # Generate each format
        for format_name in formats:
            if format_name not in formatters:
                print(f"Warning: Unknown format '{format_name}', skipping", file=sys.stderr)
                continue
            
            formatter = formatters[format_name]
            
            try:
                # Format report
                output_content = formatter.format(report)
                
                # Write to file
                output_file = output_dir / f"api_documentation{formatter.get_file_extension()}"
                output_file.write_text(output_content, encoding='utf-8')
                
                print(f"✓ Generated {format_name.upper()} report: {output_file}")
            except Exception as e:
                print(f"Error generating {format_name} report: {e}", file=sys.stderr)
                sys.exit(1)
