"""Agent introspection utilities for custom workflows.

This module provides utilities for discovering and inspecting agents
in custom workflow modules using AST parsing.
"""

import ast
from typing import Any, Dict, List

from fastapi import HTTPException, status

from ingenious.core.structured_logging import get_logger
from ingenious.utils.namespace_utils import (
    get_path_from_namespace_with_fallback,
    normalize_workflow_name,
)

logger = get_logger(__name__)


def get_agents_for_workflow(custom_workflow_name: str) -> Dict[str, Any]:
    """Retrieve agent information by parsing the agent.py file of the specified custom workflow.

    This approach uses Abstract Syntax Tree (AST) parsing for robust and safe static analysis.

    Args:
        custom_workflow_name: Name of the custom workflow

    Returns:
        Dict containing workflow name, discovered agents, and metadata

    Raises:
        HTTPException: If workflow not found or parsing fails
    """
    try:
        normalized_workflow_name = normalize_workflow_name(custom_workflow_name)
        models_dir_rel_path = f"models/{normalized_workflow_name}"
        models_path = get_path_from_namespace_with_fallback(models_dir_rel_path)

        if not models_path or not models_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Models directory for workflow '{custom_workflow_name}' not found.",
            )

        agent_file_path = models_path / "agent.py"
        if not agent_file_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent file not found for workflow '{custom_workflow_name}'.",
            )

        source_code = agent_file_path.read_text()
        tree = ast.parse(source_code)
        extracted_agents = _extract_agents_from_ast(tree)

        discovery_method = "ast_parsing"
        if not extracted_agents:
            discovery_method = "unparsable"
            agents_list = [
                {
                    "agent_name": "unknown",
                    "agent_description": "Agent definitions exist but could not be parsed via AST.",
                }
            ]
        else:
            required_fields = {
                "agent_name",
                "agent_model_name",
                "agent_display_name",
                "agent_description",
                "agent_type",
            }
            agents_list = [
                {key: data.get(key) or "" for key in required_fields} for data in extracted_agents
            ]

        return {
            "workflow_name": custom_workflow_name,
            "normalized_workflow_name": normalized_workflow_name,
            "discovered_from": discovery_method,
            "agent_count": len(extracted_agents),
            "agents": agents_list,
        }

    except SyntaxError as e:
        logger.error(f"Syntax error parsing agent file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid Python syntax in agent file for workflow '{custom_workflow_name}'.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while retrieving agents for '{custom_workflow_name}': {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the workflow agents.",
        )


def _extract_agents_from_ast(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract agent definitions from AST tree.

    Args:
        tree: Parsed AST tree

    Returns:
        List of agent data dictionaries
    """
    extracted_agents: List[Dict[str, Any]] = []

    class AgentVisitor(ast.NodeVisitor):
        """AST visitor to find Agent calls within a specific method."""

        def visit_Call(self, node: ast.Call) -> None:
            """Visit Call nodes to extract Agent instantiations."""
            if isinstance(node.func, ast.Name) and node.func.id == "Agent":
                agent_data: Dict[str, Any] = {}
                for keyword in node.keywords:
                    if isinstance(keyword.value, ast.Constant) and keyword.arg is not None:
                        agent_data[keyword.arg] = keyword.value.value
                if "agent_name" in agent_data:
                    extracted_agents.append(agent_data)
            self.generic_visit(node)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ProjectAgents":
            for method in node.body:
                if isinstance(method, ast.FunctionDef) and method.name == "Get_Project_Agents":
                    AgentVisitor().visit(method)
                    break
            break

    return extracted_agents
