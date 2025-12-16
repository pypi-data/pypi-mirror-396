"""Enum formatting utilities for consistent enum display across all output formats."""
import logging
from typing import Dict, Any, List
from fastapi_report.models import EnumInfo, EnumValue

# Configure logger for enum formatting
logger = logging.getLogger(__name__)


class EnumFormatter:
    """Utility class for formatting enum information across different output formats."""
    
    def format_enum_for_json(self, enum_info: EnumInfo) -> Dict[str, Any]:
        """
        Format enum information for JSON output with error handling.
        
        Args:
            enum_info: EnumInfo object containing enum metadata
            
        Returns:
            Dictionary suitable for JSON serialization with enum details
        """
        if not enum_info:
            logger.debug("No enum info provided for JSON formatting")
            return {}
        
        try:
            formatted_enum = {
                "class_name": getattr(enum_info, 'class_name', 'Unknown'),
                "enum_type": getattr(enum_info, 'enum_type', 'Enum'),
                "values": []
            }
            
            # Add module name if available
            if hasattr(enum_info, 'module_name') and enum_info.module_name:
                formatted_enum["module_name"] = enum_info.module_name
            
            # Add description if available
            if hasattr(enum_info, 'description') and enum_info.description:
                formatted_enum["description"] = enum_info.description
            
            # Format enum values with error handling
            if hasattr(enum_info, 'values') and enum_info.values:
                for enum_value in enum_info.values:
                    try:
                        value_dict = {
                            "name": getattr(enum_value, 'name', str(enum_value)),
                            "value": getattr(enum_value, 'value', enum_value)
                        }
                        
                        # Ensure value is JSON serializable
                        try:
                            import json
                            json.dumps(value_dict["value"])
                        except (TypeError, ValueError):
                            logger.warning(f"Enum value {value_dict['value']} is not JSON serializable, converting to string")
                            value_dict["value"] = str(value_dict["value"])
                        
                        if hasattr(enum_value, 'description') and enum_value.description:
                            value_dict["description"] = enum_value.description
                            
                        formatted_enum["values"].append(value_dict)
                        
                    except Exception as e:
                        logger.warning(f"Failed to format enum value {enum_value}: {e}")
                        # Add a fallback entry
                        formatted_enum["values"].append({
                            "name": str(enum_value),
                            "value": str(enum_value),
                            "description": f"Failed to format: {str(e)}"
                        })
            else:
                logger.warning(f"Enum {formatted_enum['class_name']} has no values")
            
            return formatted_enum
            
        except Exception as e:
            logger.error(f"Failed to format enum for JSON: {e}")
            return {
                "class_name": "FormatError",
                "enum_type": "Enum",
                "values": [],
                "error": str(e)
            }
    
    def format_enum_for_markdown(self, enum_info: EnumInfo) -> str:
        """
        Format enum information for Markdown output with error handling.
        
        Args:
            enum_info: EnumInfo object containing enum metadata
            
        Returns:
            Markdown formatted string with enum details
        """
        if not enum_info:
            logger.debug("No enum info provided for Markdown formatting")
            return ""
        
        try:
            if not hasattr(enum_info, 'values') or not enum_info.values:
                logger.debug(f"Enum {getattr(enum_info, 'class_name', 'Unknown')} has no values")
                return ""
            
            lines = []
            
            # Enum header with class name and type
            class_name = getattr(enum_info, 'class_name', 'Unknown')
            enum_type = getattr(enum_info, 'enum_type', 'Enum')
            
            # Escape markdown special characters in class name
            safe_class_name = class_name.replace('_', '\\_').replace('*', '\\*')
            enum_header = f"**{safe_class_name}** ({enum_type})"
            
            if hasattr(enum_info, 'module_name') and enum_info.module_name:
                # Escape backticks and other markdown characters in module name
                safe_module_name = enum_info.module_name.replace('`', '\\`')
                enum_header += f" from `{safe_module_name}`"
            lines.append(enum_header)
            
            # Enum description if available
            if hasattr(enum_info, 'description') and enum_info.description:
                # Escape markdown characters in description
                safe_description = enum_info.description.replace('*', '\\*').replace('_', '\\_')
                lines.append(f"*{safe_description}*")
            
            # Format enum values as a list
            lines.append("Possible values:")
            for enum_value in enum_info.values:
                try:
                    name = getattr(enum_value, 'name', str(enum_value))
                    value = getattr(enum_value, 'value', enum_value)
                    
                    # Escape markdown characters in name and value
                    safe_name = str(name).replace('`', '\\`')
                    safe_value = str(value).replace('`', '\\`')
                    
                    value_line = f"- `{safe_name}` = `{safe_value}`"
                    
                    if hasattr(enum_value, 'description') and enum_value.description:
                        # Escape markdown characters in description
                        safe_desc = enum_value.description.replace('*', '\\*').replace('_', '\\_')
                        value_line += f" - {safe_desc}"
                    lines.append(value_line)
                    
                except Exception as e:
                    logger.warning(f"Failed to format enum value {enum_value} for Markdown: {e}")
                    lines.append(f"- `{str(enum_value)}` - (formatting error)")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Failed to format enum for Markdown: {e}")
            return f"**Enum Formatting Error**: {str(e)}"
    
    def format_enum_for_html(self, enum_info: EnumInfo) -> str:
        """
        Format enum information for HTML output with error handling.
        
        Args:
            enum_info: EnumInfo object containing enum metadata
            
        Returns:
            HTML formatted string with enum details and styling
        """
        if not enum_info:
            logger.debug("No enum info provided for HTML formatting")
            return ""
        
        try:
            if not hasattr(enum_info, 'values') or not enum_info.values:
                logger.debug(f"Enum {getattr(enum_info, 'class_name', 'Unknown')} has no values")
                return ""
            
            html_parts = []
            
            # Enum container with styling
            html_parts.append('<div class="enum-info">')
            
            # Enum header with HTML escaping
            class_name = getattr(enum_info, 'class_name', 'Unknown')
            enum_type = getattr(enum_info, 'enum_type', 'Enum')
            
            # HTML escape the class name and type
            safe_class_name = self._html_escape(class_name)
            safe_enum_type = self._html_escape(enum_type)
            
            enum_header = f'<span class="enum-class">{safe_class_name}</span>'
            enum_header += f' <span class="enum-type">({safe_enum_type})</span>'
            
            if hasattr(enum_info, 'module_name') and enum_info.module_name:
                safe_module_name = self._html_escape(enum_info.module_name)
                enum_header += f' <span class="enum-module">from {safe_module_name}</span>'
            html_parts.append(f'<div class="enum-header">{enum_header}</div>')
            
            # Enum description if available
            if hasattr(enum_info, 'description') and enum_info.description:
                safe_description = self._html_escape(enum_info.description)
                html_parts.append(f'<div class="enum-description">{safe_description}</div>')
            
            # Enum values list
            html_parts.append('<div class="enum-values">')
            html_parts.append('<strong>Possible values:</strong>')
            html_parts.append('<ul class="enum-values-list">')
            
            for enum_value in enum_info.values:
                try:
                    name = getattr(enum_value, 'name', str(enum_value))
                    value = getattr(enum_value, 'value', enum_value)
                    
                    # HTML escape the name and value
                    safe_name = self._html_escape(str(name))
                    safe_value = self._html_escape(str(value))
                    
                    value_html = f'<li><code class="enum-name">{safe_name}</code> = <code class="enum-value">{safe_value}</code>'
                    
                    if hasattr(enum_value, 'description') and enum_value.description:
                        safe_desc = self._html_escape(enum_value.description)
                        value_html += f' <span class="enum-value-desc">- {safe_desc}</span>'
                    value_html += '</li>'
                    html_parts.append(value_html)
                    
                except Exception as e:
                    logger.warning(f"Failed to format enum value {enum_value} for HTML: {e}")
                    safe_fallback = self._html_escape(str(enum_value))
                    html_parts.append(f'<li><code>{safe_fallback}</code> - (formatting error)</li>')
            
            html_parts.append('</ul>')
            html_parts.append('</div>')  # Close enum-values
            html_parts.append('</div>')  # Close enum-info
            
            return "\n".join(html_parts)
            
        except Exception as e:
            logger.error(f"Failed to format enum for HTML: {e}")
            safe_error = self._html_escape(str(e))
            return f'<div class="enum-error"><strong>Enum Formatting Error:</strong> {safe_error}</div>'
    
    def format_enum_values_list(self, values: List[EnumValue]) -> str:
        """
        Format enum values as a simple comma-separated list with error handling.
        
        Args:
            values: List of EnumValue objects
            
        Returns:
            Comma-separated string of enum values
        """
        if not values:
            logger.debug("No enum values provided for list formatting")
            return ""
        
        try:
            # Create list of formatted values
            formatted_values = []
            for enum_value in values:
                try:
                    # Use the actual value, not the name, for the list
                    value = getattr(enum_value, 'value', enum_value)
                    formatted_values.append(str(value))
                except Exception as e:
                    logger.warning(f"Failed to format enum value {enum_value}: {e}")
                    formatted_values.append(str(enum_value))
            
            return ", ".join(formatted_values)
            
        except Exception as e:
            logger.error(f"Failed to format enum values list: {e}")
            return "Error formatting enum values"
    
    def _html_escape(self, text: str) -> str:
        """
        Escape HTML special characters.
        
        Args:
            text: Text to escape
            
        Returns:
            HTML-escaped text
        """
        if not isinstance(text, str):
            text = str(text)
        
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    
    def get_enum_css_styles(self) -> str:
        """
        Get CSS styles for enum formatting in HTML output.
        
        Returns:
            CSS string with enum-specific styling
        """
        return """
        .enum-info {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 12px;
            margin: 8px 0;
            font-size: 14px;
        }
        
        .enum-header {
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .enum-class {
            color: #495057;
            font-weight: bold;
        }
        
        .enum-type {
            color: #6c757d;
            font-style: italic;
            font-size: 12px;
        }
        
        .enum-module {
            color: #6c757d;
            font-size: 12px;
            font-family: 'Courier New', monospace;
        }
        
        .enum-description {
            color: #6c757d;
            font-style: italic;
            margin-bottom: 8px;
        }
        
        .enum-values {
            margin-top: 8px;
        }
        
        .enum-values-list {
            margin: 4px 0 0 20px;
            padding: 0;
        }
        
        .enum-values-list li {
            margin: 2px 0;
        }
        
        .enum-name {
            background: #e9ecef;
            color: #495057;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            font-weight: bold;
        }
        
        .enum-value {
            background: #d1ecf1;
            color: #0c5460;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        
        .enum-value-desc {
            color: #6c757d;
            font-size: 12px;
        }
        """