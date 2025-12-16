"""Diagnostic and monitoring API routes.

This module provides endpoints for health checks, workflow discovery,
workflow status validation, and system diagnostics.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from typing_extensions import Annotated

from ingenious.config.settings import IngeniousSettings
from ingenious.core.structured_logging import get_logger
from ingenious.models.http_error import HTTPError
from ingenious.services import auth_dependencies
from ingenious.services import fastapi_dependencies as ingen_deps
from ingenious.utils.namespace_utils import (
    discover_workflows,
    get_workflow_metadata,
    normalize_workflow_name,
)

logger = get_logger(__name__)
router = APIRouter()


@dataclass
class ConfigValidationResult:
    """Result of configuration validation."""

    configured: bool = True
    missing_config: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add a configuration error."""
        self.missing_config.append(message)
        self.configured = False


def _validate_models_config(config: IngeniousSettings, result: ConfigValidationResult) -> None:
    """Validate model configuration."""
    if not config.models or len(config.models) == 0:
        result.add_error("models: No models configured")
        return

    model = config.models[0]
    if not getattr(model, "api_key", None):
        result.add_error("models.api_key: Missing environment configuration")
    if not getattr(model, "base_url", None):
        result.add_error("models.base_url: Missing environment configuration")


def _validate_chat_service_config(
    config: IngeniousSettings, result: ConfigValidationResult
) -> None:
    """Validate chat service configuration."""
    if not config.chat_service or config.chat_service.type != "multi_agent":
        result.add_error("chat_service.type: Must be 'multi_agent'")


def _validate_azure_search_config(
    config: IngeniousSettings, result: ConfigValidationResult
) -> None:
    """Validate Azure Search configuration."""
    if not config.azure_search_services or len(config.azure_search_services) == 0:
        result.add_error("azure_search_services: Not configured")
        return

    search_service = config.azure_search_services[0]
    if not search_service.endpoint:
        result.add_error("azure_search_services.endpoint: Missing")
    if not getattr(search_service, "key", None):
        result.add_error("azure_search_services.key: Missing environment configuration")


def _validate_local_sql_config(config: IngeniousSettings, result: ConfigValidationResult) -> None:
    """Validate local SQL configuration."""
    if not getattr(config, "local_sql_db", None):
        result.add_error("local_sql_db: Not configured")
        return

    if not config.local_sql_db.database_path:
        result.add_error("local_sql_db.database_path: Missing")
    if not config.local_sql_db.sample_csv_path:
        result.add_error("local_sql_db.sample_csv_path: Missing")


def _validate_sql_manipulation_config(
    config: IngeniousSettings, result: ConfigValidationResult
) -> None:
    """Validate SQL manipulation agent configuration."""
    has_azure_sql = getattr(config, "azure_sql_services", None) and getattr(
        config.azure_sql_services, "database_connection_string", None
    )
    has_local_sql = getattr(config, "local_sql_db", None) and getattr(
        config.local_sql_db, "database_path", None
    )

    if not has_azure_sql and not has_local_sql:
        result.add_error("database: Neither Azure SQL nor local SQLite configured")


def _validate_workflow_requirements(
    config: IngeniousSettings,
    workflow_name: str,
    requirements: Dict[str, Any],
    result: ConfigValidationResult,
) -> None:
    """Validate workflow-specific requirements."""
    required_config = requirements.get("required_config", [])

    if "azure_search_services" in required_config:
        _validate_azure_search_config(config, result)

    if "local_sql_db" in required_config:
        _validate_local_sql_config(config, result)

    if workflow_name == "sql_manipulation_agent":
        _validate_sql_manipulation_config(config, result)


@router.get(
    "/workflow-status/{workflow_name}",
    responses={
        200: {"model": dict, "description": "Workflow configuration status"},
        400: {"model": HTTPError, "description": "Bad Request"},
        404: {"model": HTTPError, "description": "Workflow Not Found"},
    },
)
async def workflow_status(
    workflow_name: str,
    request: Request,
    auth_user: Annotated[str, Depends(auth_dependencies.get_auth_user)],
) -> Dict[str, Any]:
    """Check the configuration status of a specific workflow.

    Returns information about whether the workflow is properly configured
    and what external services or configuration might be missing.
    """
    try:
        config = ingen_deps.get_config()
        normalized_workflow_name = normalize_workflow_name(workflow_name)

        available_workflows = discover_workflows(
            include_builtin=config.chat_service.enable_builtin_workflows
        )

        if normalized_workflow_name not in available_workflows:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown workflow: {workflow_name} (normalized: {normalized_workflow_name}). Available: {available_workflows}",
            )

        requirements = get_workflow_metadata(normalized_workflow_name)
        result = ConfigValidationResult()

        _validate_models_config(config, result)
        _validate_chat_service_config(config, result)
        _validate_workflow_requirements(config, workflow_name, requirements, result)

        return {
            "workflow": workflow_name,
            "description": requirements["description"],
            "category": requirements["category"],
            "configured": result.configured,
            "missing_config": result.missing_config,
            "required_config": requirements["required_config"],
            "external_services": requirements["external_services"],
            "ready": result.configured,
            "test_command": f'curl -X POST http://localhost:{config.web_configuration.port}/api/v1/chat -H "Content-Type: application/json" -d \'{{"user_prompt": "Hello", "conversation_flow": "{workflow_name}"}}\'',
            "documentation": "See docs/workflows/README.md for detailed setup instructions",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error in workflow status check",
            workflow_name=workflow_name,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/workflows",
    responses={
        200: {"model": dict, "description": "List all workflows and their status"},
        400: {"model": HTTPError, "description": "Bad Request"},
    },
)
async def list_workflows(
    request: Request,
    auth_user: Annotated[str, Depends(auth_dependencies.get_auth_user)],
) -> Dict[str, Any]:
    """List all available workflows and their configuration status.

    Supports both hyphenated (bike-insights) and underscored (bike_insights) naming formats.
    Dynamically discovers workflows from all namespaces.
    """
    try:
        config = ingen_deps.get_config()

        # Dynamically discover all available workflows
        discovered_workflows = discover_workflows(
            include_builtin=config.chat_service.enable_builtin_workflows
        )

        workflow_statuses = []
        for workflow in discovered_workflows:
            # Get status for each workflow
            status = await workflow_status(workflow, request, auth_user)

            # Add supported naming formats to the status
            hyphenated_name = workflow.replace("_", "-")
            status["supported_names"] = (
                [workflow, hyphenated_name] if workflow != hyphenated_name else [workflow]
            )

            workflow_statuses.append(status)

        # Group by category
        by_category: Dict[str, List[Dict[str, Any]]] = {}
        for status in workflow_statuses:
            category = status["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(status)

        return {
            "workflows": workflow_statuses,
            "by_category": by_category,
            "summary": {
                "total": len(discovered_workflows),
                "configured": len([w for w in workflow_statuses if w["configured"]]),
                "unconfigured": len([w for w in workflow_statuses if not w["configured"]]),
            },
            "naming_note": "Workflows support both hyphenated (bike-insights) and underscored (bike_insights) naming formats",
        }

    except Exception as e:
        logger.error("Error listing workflows", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.api_route(
    "/diagnostic",
    methods=["GET", "OPTIONS"],
    responses={
        200: {"model": dict, "description": "Diagnostic information"},
        400: {"model": HTTPError, "description": "Bad Request"},
        406: {"model": HTTPError, "description": "Not Acceptable"},
        413: {"model": HTTPError, "description": "Payload Too Large"},
    },
)
async def diagnostic(
    request: Request,
    auth_user: Annotated[str, Depends(auth_dependencies.get_auth_user)],
) -> Dict[str, Any]:
    """Retrieve diagnostic information about file storage paths.

    Returns directory paths for prompts, data, outputs, and events configured
    in the system's file storage settings.

    Args:
        request: FastAPI request object for method checking.
        auth_user: Authenticated username from dependency injection.

    Returns:
        Dictionary containing diagnostic information with storage directory paths.

    Raises:
        HTTPException: If diagnostic retrieval fails with status 500.
    """
    if request.method == "OPTIONS":
        return {"Allow": "GET, OPTIONS"}

    try:
        diagnostic = {}

        config = ingen_deps.get_config()
        revisions_storage = ingen_deps.get_file_storage_revisions(config=config)
        data_storage = ingen_deps.get_file_storage_data(config=config)

        prompt_dir = Path(await revisions_storage.get_base_path()) / Path(
            await revisions_storage.get_prompt_template_path()
        )

        data_dir = Path(await data_storage.get_base_path()) / Path(
            await data_storage.get_data_path()
        )

        output_dir = Path(await revisions_storage.get_base_path()) / Path(
            await revisions_storage.get_output_path()
        )

        events_dir = Path(await revisions_storage.get_base_path()) / Path(
            await revisions_storage.get_events_path()
        )

        diagnostic["Prompt Directory"] = prompt_dir
        diagnostic["Data Directory"] = data_dir
        diagnostic["Output Directory"] = output_dir
        diagnostic["Events Directory"] = events_dir

        return diagnostic

    except Exception as e:
        logger.error("Error in diagnostic check", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    responses={
        200: {"model": dict, "description": "System health status"},
        503: {"model": HTTPError, "description": "Service Unavailable"},
    },
)
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring system status.

    Returns basic system information and configuration status.
    Useful for load balancers, monitoring systems, and quick validation.
    """
    try:
        start_time = time.time()

        # Check basic configuration availability
        try:
            _ = ingen_deps.get_config()
            config_status = "ok"
        except Exception as e:
            logger.warning("Configuration check failed", error=str(e))
            config_status = "error"

        # Profile system is deprecated - no longer check for profiles
        profile_status = "ok"  # Always OK since profiles are no longer used

        response_time = round((time.time() - start_time) * 1000, 2)  # ms

        # Determine overall status
        overall_status = (
            "healthy" if config_status == "ok" and profile_status == "ok" else "degraded"
        )

        health_data = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": response_time,
            "components": {"configuration": config_status, "profile": profile_status},
            "version": "1.0.0",  # Could be pulled from package info
            "uptime": "available",  # Could track actual uptime if needed
        }

        # Return 503 if any critical components are down
        if overall_status == "degraded":
            raise HTTPException(status_code=503, detail=health_data)

        return health_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Health check failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            },
        )
