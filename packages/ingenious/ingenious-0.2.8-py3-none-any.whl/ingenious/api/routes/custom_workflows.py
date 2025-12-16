"""Custom workflow introspection API routes.

This module provides endpoints for discovering and inspecting custom workflows,
their agents, and their Pydantic schemas for dynamic UI generation.

The implementation has been split into:
- custom_workflows_introspection: Agent discovery via AST parsing
- custom_workflows_schema: Schema transformation for Alpine.js
"""

import inspect
import pkgutil
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from ingenious.core.structured_logging import get_logger
from ingenious.utils.imports import import_module_with_fallback
from ingenious.utils.namespace_utils import (
    get_path_from_namespace_with_fallback,
    normalize_workflow_name,
)

# Import from split modules
from .custom_workflows_introspection import get_agents_for_workflow
from .custom_workflows_schema import transform_schemas_for_alpine

router = APIRouter()
logger = get_logger(__name__)


@router.get("/custom-workflows/agents/{custom_workflow_name}/", response_model=Dict[str, Any])
async def get_custom_workflow_agents(custom_workflow_name: str) -> Dict[str, Any]:
    """Retrieves agent information by parsing the agent.py file of the specified custom workflow.

    This approach uses Abstract Syntax Tree (AST) parsing for robust and safe static analysis.

    Args:
        custom_workflow_name: Name of the custom workflow to inspect

    Returns:
        Dict containing workflow name, discovered agents, and metadata
    """
    return get_agents_for_workflow(custom_workflow_name)


@router.get("/custom-workflows/schema/{custom_workflow_name}/", response_model=Dict[str, Any])
async def get_custom_workflow_schema(custom_workflow_name: str, request: Request) -> Dict[str, Any]:
    """Retrieves Pydantic model schemas optimized for Alpine.js dynamic UI generation.

    Returns a structured schema with UI metadata and field ordering.

    Args:
        custom_workflow_name: Name of the custom workflow
        request: FastAPI request object

    Returns:
        Dict containing transformed schemas and metadata
    """
    try:
        normalized_workflow_name = normalize_workflow_name(custom_workflow_name)
        models_dir_rel_path = f"models/{normalized_workflow_name}"
        models_path = get_path_from_namespace_with_fallback(models_dir_rel_path)

        if not models_path or not models_path.is_dir():
            # Include additional detail about the absolute path where the app is looking
            attempted_absolute_path = (
                str(models_path.resolve())
                if models_path
                else f"Unable to resolve path for '{models_dir_rel_path}'"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Models directory for workflow '{custom_workflow_name}' not found. "
                    f"Attempted relative path: '{models_dir_rel_path}', "
                    f"Resolved absolute path: {attempted_absolute_path}."
                ),
            )

        # Collect all Pydantic models first
        pydantic_models: Dict[str, Any] = {}
        model_classes: Dict[str, type[BaseModel]] = {}

        for module_info in pkgutil.iter_modules([str(models_path)]):
            if module_info.ispkg or module_info.name == "agent":
                continue

            module_import_path = f"models.{normalized_workflow_name}.{module_info.name}"
            try:
                module = import_module_with_fallback(module_import_path)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseModel) and obj is not BaseModel:
                        schema = obj.model_json_schema()
                        if schema is not None:
                            pydantic_models[name] = schema
                            model_classes[name] = obj
            except (ImportError, AttributeError) as e:
                logger.error(f"Error processing schema module {module_import_path}: {e}")
                continue

        if not pydantic_models:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No Pydantic models found for workflow '{normalized_workflow_name}'.",
            )

        # Transform schemas for Alpine.js
        alpine_schema = transform_schemas_for_alpine(pydantic_models, model_classes)

        response_data = {
            "workflow_name": custom_workflow_name,
            "schemas": alpine_schema,
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "total_models": len(pydantic_models),
                "alpine_version": "3.x",
                "features": {
                    "validation": True,
                    "nested_objects": True,
                    "arrays": True,
                    "unions": True,
                    "conditional_fields": True,
                },
            },
        }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while retrieving Alpine schema for '{custom_workflow_name}': {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the workflow schema.",
        )
