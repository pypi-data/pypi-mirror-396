"""Schema transformation utilities for custom workflows.

This module provides utilities for transforming Pydantic schemas
into Alpine.js-friendly format for dynamic UI generation.
"""

from typing import Any, Dict, List

from pydantic import BaseModel


def transform_schemas_for_alpine(
    schemas: Dict[str, Any], model_classes: Dict[str, type[BaseModel]]
) -> Dict[str, Any]:
    """Transform Pydantic JSON schemas into Alpine.js-friendly format.

    Args:
        schemas: Pydantic JSON schemas
        model_classes: Pydantic model classes

    Returns:
        Alpine.js-compatible schemas with UI metadata
    """
    alpine_schemas = {}

    for model_name, schema in schemas.items():
        model_class = model_classes.get(model_name)

        alpine_schema = {
            "model_name": model_name,
            "title": schema.get("title", model_name),
            "description": schema.get("description", ""),
            "type": schema.get("type", "object"),
            "properties": {},
            "required": schema.get("required", []),
            "ui_metadata": {
                "display_order": [],
                "field_groups": {},
                "conditional_fields": {},
                "validation_rules": {},
            },
        }

        # Process properties with Alpine.js enhancements
        if "properties" in schema:
            for field_name, field_schema in schema["properties"].items():
                alpine_field = transform_field_for_alpine(field_name, field_schema, model_class)
                alpine_schema["properties"][field_name] = alpine_field
                alpine_schema["ui_metadata"]["display_order"].append(field_name)

        # Handle discriminated unions (like bike types)
        if "$defs" in schema:
            alpine_schema["definitions"] = {}
            for def_name, def_schema in schema["$defs"].items():
                alpine_schema["definitions"][def_name] = transform_definition_for_alpine(
                    def_name, def_schema
                )

        # Add form initialization data
        alpine_schema["default_values"] = generate_default_values(alpine_schema)

        alpine_schemas[model_name] = alpine_schema

    return alpine_schemas


def transform_field_for_alpine(
    field_name: str,
    field_schema: Dict[str, Any],
    model_class: type[BaseModel] | None = None,
) -> Dict[str, Any]:
    """Transform individual field schema for Alpine.js.

    Args:
        field_name: Field name
        field_schema: Pydantic field schema
        model_class: Optional model class reference

    Returns:
        Alpine.js-compatible field schema with UI hints
    """
    alpine_field = {
        **field_schema,
        "ui_component": determine_ui_component(field_schema),
        "validation": extract_validation_rules(field_schema),
        "alpine_model": f"formData.{field_name}",
        "display_name": field_schema.get("title", field_name.replace("_", " ").title()),
    }

    # Handle special field types
    field_type = field_schema.get("type")
    field_format = field_schema.get("format")

    # Add Alpine.js specific attributes
    if field_type == "array":
        alpine_field["ui_component"] = "array"
        alpine_field["array_config"] = {
            "min_items": field_schema.get("minItems", 0),
            "max_items": field_schema.get("maxItems"),
            "item_schema": field_schema.get("items", {}),
            "add_button_text": f"Add {field_name.replace('_', ' ').title()}",
            "remove_button_text": "Remove",
        }

    elif field_type == "object":
        alpine_field["ui_component"] = "nested_object"
        alpine_field["nested_properties"] = field_schema.get("properties", {})

    elif "anyOf" in field_schema or "oneOf" in field_schema:
        alpine_field["ui_component"] = "union_select"
        alpine_field["union_options"] = extract_union_options(field_schema)

    elif field_format == "date":
        alpine_field["ui_component"] = "date_input"

    elif field_format == "email":
        alpine_field["ui_component"] = "email_input"

    elif field_type == "boolean":
        alpine_field["ui_component"] = "checkbox"

    elif field_type in ["integer", "number"]:
        alpine_field["ui_component"] = "number_input"
        alpine_field["number_config"] = {
            "min": field_schema.get("minimum"),
            "max": field_schema.get("maximum"),
            "step": 1 if field_type == "integer" else 0.01,
        }

    elif field_schema.get("enum"):
        alpine_field["ui_component"] = "select"
        alpine_field["options"] = [
            {"value": opt, "label": str(opt)} for opt in field_schema["enum"]
        ]

    else:
        alpine_field["ui_component"] = "text_input"

    return alpine_field


def determine_ui_component(field_schema: Dict[str, Any]) -> str:
    """Determine the appropriate UI component for Alpine.js rendering.

    Args:
        field_schema: Pydantic field schema

    Returns:
        UI component type (e.g., "text_input", "select", "checkbox")
    """
    field_type = field_schema.get("type")
    field_format = field_schema.get("format")

    if field_schema.get("enum"):
        return "select"
    elif field_type == "boolean":
        return "checkbox"
    elif field_type == "array":
        return "array"
    elif field_type == "object":
        return "nested_object"
    elif "anyOf" in field_schema or "oneOf" in field_schema:
        return "union_select"
    elif field_format == "date":
        return "date_input"
    elif field_format == "email":
        return "email_input"
    elif field_format == "password":
        return "password_input"
    elif field_type in ["integer", "number"]:
        return "number_input"
    elif field_type == "string" and field_schema.get("maxLength", 0) > 100:
        return "textarea"
    else:
        return "text_input"


def extract_validation_rules(field_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Extract validation rules for Alpine.js client-side validation.

    Args:
        field_schema: Pydantic field schema

    Returns:
        Validation rules for client-side validation
    """
    rules: Dict[str, Any] = {}

    if field_schema.get("minLength"):
        rules["minLength"] = field_schema["minLength"]
    if field_schema.get("maxLength"):
        rules["maxLength"] = field_schema["maxLength"]
    if field_schema.get("minimum"):
        rules["min"] = field_schema["minimum"]
    if field_schema.get("maximum"):
        rules["max"] = field_schema["maximum"]
    if field_schema.get("pattern"):
        rules["pattern"] = field_schema["pattern"]
    if field_schema.get("format"):
        rules["format"] = field_schema["format"]

    return rules


def extract_union_options(field_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract union type options for discriminated unions.

    Args:
        field_schema: Pydantic field schema

    Returns:
        Union type options with discriminator information
    """
    options: List[Dict[str, Any]] = []

    union_types = field_schema.get("anyOf", field_schema.get("oneOf", []))

    for i, union_type in enumerate(union_types):
        if "$ref" in union_type:
            # Handle reference types
            ref_name = union_type["$ref"].split("/")[-1]
            options.append(
                {
                    "value": ref_name.lower(),
                    "label": ref_name,
                    "schema_ref": union_type["$ref"],
                    "discriminator": ref_name,
                }
            )
        else:
            # Handle inline types
            title = union_type.get("title", f"Option {i + 1}")
            options.append({"value": title.lower(), "label": title, "schema": union_type})

    return options


def generate_default_values(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Generate default form values for Alpine.js initialization.

    Args:
        schema: Pydantic schema

    Returns:
        Default values for form fields
    """
    defaults: Dict[str, Any] = {}

    for field_name, field_schema in schema.get("properties", {}).items():
        field_type = field_schema.get("type")
        default_value = field_schema.get("default")

        if default_value is not None:
            defaults[field_name] = default_value
        elif field_type == "array":
            defaults[field_name] = []
        elif field_type == "object":
            defaults[field_name] = {}
        elif field_type == "boolean":
            defaults[field_name] = False
        elif field_type in ["integer", "number"]:
            defaults[field_name] = 0
        elif field_type == "string":
            defaults[field_name] = ""
        else:
            defaults[field_name] = None

    return defaults


def transform_definition_for_alpine(def_name: str, def_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Transform schema definitions for Alpine.js discriminated unions.

    Args:
        def_name: Definition name
        def_schema: Definition schema

    Returns:
        Alpine.js-compatible definition
    """
    return {
        "name": def_name,
        "title": def_schema.get("title", def_name),
        "type": def_schema.get("type", "object"),
        "properties": def_schema.get("properties", {}),
        "required": def_schema.get("required", []),
        "discriminator": extract_discriminator_info(def_schema),
    }


def extract_discriminator_info(schema: Dict[str, Any]) -> Dict[str, Any] | None:
    """Extract discriminator information for union types.

    Args:
        schema: Schema to extract discriminator from

    Returns:
        Discriminator information or None
    """
    if "discriminator" in schema:
        disc = schema["discriminator"]
        if isinstance(disc, dict):
            return disc
        else:
            return {"property_name": str(disc)}

    # Try to infer discriminator from class hierarchy
    title = schema.get("title", "")
    if title:
        return {"property_name": "type", "mapping": {title.lower(): title}}

    return None
