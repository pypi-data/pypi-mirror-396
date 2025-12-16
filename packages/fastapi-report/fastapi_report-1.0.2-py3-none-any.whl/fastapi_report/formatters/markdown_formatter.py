"""Markdown formatter for API reports."""
import logging
from fastapi_report.models import APIReport, EndpointInfo, ParameterInfo, MCPToolInfo
from .base import BaseFormatter
from .enum_formatter import EnumFormatter

# Configure logger for Markdown formatting
logger = logging.getLogger(__name__)


class MarkdownFormatter(BaseFormatter):
    """Formats API reports as Markdown documentation."""
    
    def __init__(self):
        """Initialize the markdown formatter with enum formatting support."""
        self.enum_formatter = EnumFormatter()
    
    def format(self, report: APIReport) -> str:
        """
        Convert report to Markdown documentation.
        
        Args:
            report: APIReport to format
            
        Returns:
            Markdown formatted string
        """
        lines = []
        
        # Title and metadata
        lines.append(f"# {report.server_name} API Documentation")
        lines.append("")
        lines.append(f"**Version:** {report.server_version}")
        lines.append(f"**Generated:** {report.generated_at}")
        lines.append("")
        
        # Table of contents
        lines.append("## Table of Contents")
        lines.append("")
        lines.append("- [REST Endpoints](#rest-endpoints)")
        if report.mcp_tools:
            lines.append("- [MCP Tools](#mcp-tools)")
        lines.append("")
        
        # REST Endpoints section
        lines.append("## REST Endpoints")
        lines.append("")
        
        if not report.endpoints:
            lines.append("*No endpoints found.*")
            lines.append("")
        else:
            for endpoint in report.endpoints:
                lines.extend(self.format_endpoint(endpoint))
                lines.append("")
        
        # MCP Tools section
        if report.mcp_tools:
            lines.append("## MCP Tools")
            lines.append("")
            lines.append(f"**Total Tools:** {len(report.mcp_tools)}")
            lines.append("")
            
            # Tool summary list
            lines.append("### Available Tools")
            lines.append("")
            for tool in report.mcp_tools:
                # Extract first line of description
                desc_first_line = tool.description.split('\n')[0] if tool.description else "No description"
                lines.append(f"- **[{tool.name}](#{tool.name.replace('_', '-')})** - {desc_first_line}")
            lines.append("")
            
            # Detailed tool documentation
            lines.append("### Tool Details")
            lines.append("")
            for tool in report.mcp_tools:
                lines.extend(self.format_mcp_tool(tool))
                lines.append("")
        
        return "\n".join(lines)
    
    def format_endpoint(self, endpoint: EndpointInfo) -> list:
        """
        Format single endpoint as Markdown section.
        
        Args:
            endpoint: EndpointInfo to format
            
        Returns:
            List of markdown lines
        """
        lines = []
        
        # Endpoint header
        lines.append(f"### `{endpoint.method} {endpoint.path}`")
        lines.append("")
        
        if endpoint.summary:
            lines.append(f"**Summary:** {endpoint.summary}")
            lines.append("")
        
        if endpoint.description:
            lines.append(endpoint.description)
            lines.append("")
        
        if endpoint.tags:
            lines.append(f"**Tags:** {', '.join(endpoint.tags)}")
            lines.append("")
        
        if endpoint.deprecated:
            lines.append("⚠️ **DEPRECATED**")
            lines.append("")
        
        # Parameters
        if endpoint.parameters:
            lines.append("**Parameters:**")
            lines.append("")
            lines.extend(self.format_parameters_table(endpoint.parameters))
            lines.append("")
        
        # Request body
        if endpoint.request_body:
            lines.append("**Request Body:**")
            lines.append("")
            lines.append("```json")
            lines.append(str(endpoint.request_body))
            lines.append("```")
            lines.append("")
        
        # Responses
        if endpoint.responses:
            lines.append("**Responses:**")
            lines.append("")
            for status_code, response_data in sorted(endpoint.responses.items()):
                desc = response_data.get('description', '')
                lines.append(f"- **{status_code}**: {desc}")
            lines.append("")
        
        return lines
    
    def format_parameters_table(self, params: list) -> list:
        """
        Format parameters as Markdown table with enhanced enum support.
        
        Args:
            params: List of ParameterInfo objects
            
        Returns:
            List of markdown table lines
        """
        lines = []
        
        # Table header
        lines.append("| Name | Type | In | Required | Default | Enum | Description |")
        lines.append("|------|------|----|---------|---------| ---- | ------------|")
        
        # Table rows
        for param in params:
            name = param.name
            ptype = param.python_type
            location = param.param_type
            required = "✓" if param.required else "✗"
            default = str(param.default) if param.default is not None else "-"
            desc = param.description or "-"
            enum_column = "-"
            
            # Enhanced enum handling
            if param.enum_info:
                # If the type doesn't already show enum information, enhance it
                if "Enum[" not in ptype:
                    # Check if it's an optional type
                    if ptype.startswith("Optional[") or " | " in ptype or "Union[" in ptype:
                        # For optional types, show as Optional[Enum[ClassName]]
                        ptype = f"Optional[Enum[{param.enum_info.class_name}]]"
                    else:
                        # For non-optional types, show as Enum[ClassName]
                        ptype = f"Enum[{param.enum_info.class_name}]"
                
                # Create enum column content
                if param.enum_info.values:
                    values_list = []
                    for enum_value in param.enum_info.values:
                        values_list.append(f"`{enum_value.value}`")
                    enum_column = ", ".join(values_list)
                
                # Keep description clean - just the original description
                if not param.description:
                    desc = "-"
            else:
                # Add non-enum constraints to description
                if param.constraints:
                    constraint_strs = []
                    for key, value in param.constraints.items():
                        constraint_strs.append(f"{key}={value}")
                    if constraint_strs:
                        desc += f" ({', '.join(constraint_strs)})"
            
            lines.append(f"| {name} | {ptype} | {location} | {required} | {default} | {enum_column} | {desc} |")
        
        # Add detailed enum information after the table
        enum_params = [p for p in params if p.enum_info]
        if enum_params:
            lines.append("")
            lines.append("**Enum Details:**")
            lines.append("")
            for param in enum_params:
                if param.enum_info:
                    enum_details = self.enum_formatter.format_enum_for_markdown(param.enum_info)
                    if enum_details:
                        lines.append(f"**{param.name}** parameter:")
                        lines.append("")
                        lines.extend(enum_details.split('\n'))
                        lines.append("")
        
        return lines
    
    def format_mcp_tool(self, tool: MCPToolInfo) -> list:
        """
        Format MCP tool as Markdown section.
        
        Args:
            tool: MCPToolInfo to format
            
        Returns:
            List of markdown lines
        """
        lines = []
        
        # Use tool name as anchor
        lines.append(f"#### {tool.name}")
        lines.append("")
        
        if tool.mapped_endpoint:
            lines.append(f"**Mapped Endpoint:** `{tool.mapped_endpoint}`")
            lines.append("")
        
        if tool.description:
            # Show first paragraph prominently
            desc_parts = tool.description.split('\n\n')
            lines.append(desc_parts[0])
            lines.append("")
            
            # Show rest in details if there's more
            if len(desc_parts) > 1:
                lines.append("<details>")
                lines.append("<summary>Show full description</summary>")
                lines.append("")
                for part in desc_parts[1:]:
                    lines.append(part)
                    lines.append("")
                lines.append("</details>")
                lines.append("")
        
        if tool.input_schema and tool.input_schema.get('properties'):
            lines.append("**Parameters:**")
            lines.append("")
            
            # Show parameters in a table
            properties = tool.input_schema.get('properties', {})
            required = tool.input_schema.get('required', [])
            
            if properties:
                lines.append("| Parameter | Type | Required | Enum | Description |")
                lines.append("|-----------|------|----------|------|-------------|")
                
                for param_name, param_schema in properties.items():
                    param_type = param_schema.get('type', 'any')
                    is_required = "✓" if param_name in required else "✗"
                    param_desc = param_schema.get('description', '-')
                    enum_column = "-"
                    
                    # Handle enum values
                    if 'enum' in param_schema:
                        enum_values_list = []
                        for enum_value in param_schema['enum']:
                            enum_values_list.append(f"`{enum_value}`")
                        enum_column = ", ".join(enum_values_list)
                        param_type = "Enum"
                    
                    # Handle anyOf types (for Optional[Enum] cases)
                    elif 'anyOf' in param_schema:
                        types = []
                        enum_values = None
                        has_null = False
                        
                        for any_of_item in param_schema['anyOf']:
                            if any_of_item.get('type') == 'null':
                                has_null = True
                            elif 'enum' in any_of_item:
                                enum_values = any_of_item['enum']
                                types.append('enum')
                            else:
                                types.append(any_of_item.get('type', 'any'))
                        
                        if enum_values:
                            enum_values_list = []
                            for enum_value in enum_values:
                                enum_values_list.append(f"`{enum_value}`")
                            enum_column = ", ".join(enum_values_list)
                            
                            if has_null:
                                param_type = "Optional[Enum]"
                            else:
                                param_type = "Enum"
                        else:
                            param_type = ' | '.join(set(types))
                    
                    lines.append(f"| {param_name} | {param_type} | {is_required} | {enum_column} | {param_desc} |")
                
                lines.append("")
            
            # Collapsible full schema
            lines.append("<details>")
            lines.append("<summary>Show full JSON schema</summary>")
            lines.append("")
            lines.append("```json")
            import json
            lines.append(json.dumps(tool.input_schema, indent=2))
            lines.append("```")
            lines.append("</details>")
            lines.append("")
        
        return lines
    
    def get_file_extension(self) -> str:
        """Return Markdown file extension."""
        return ".md"
