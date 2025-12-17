"""MCP Server implementation for AMSL schema resources and validation."""

from enum import StrEnum
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any
import jsonschema
import mcp.server.models as models
from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions
import mcp.types as types
import httpx
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Schema paths
SCHEMAS_ROOT = "https://orion.s3.iism.kit.edu/amsl-content/p/schemas/"

SCHEMAS = {
    "collection": "This json schemas defines the yaml structure for AMSL *.collection.yaml files. These files describe collections of documents used for a RAG system.",
    "assessment": "This json schema defines the yaml structure for AMSL *.assessment.yaml files. These files describe assessments which can be addedd to modules.",
    "module": "This json schema defines the yaml structure for AMSL *.module.yaml files. These files describe modules which containts contents like lectures and sessions in which the contents are covered. Sessions are covered by a chatbot, an llm agent. Modules can also have optional pre- and post-assessments.",
    "llm_agent": "This json schema defines the yaml structure for AMSL *.agent.yaml files. These files describe agents by steps and logics similar to a graph structure. Agents can be used in sessions to cover the content.",
    "global": "This json schema defines the yaml structure for AMSL *.global.yaml files. These files contain global configurations.",
    "constants": "This json schema defines the yaml structure for AMSL *.constants.yaml files. These files define constant values used across the system, mostly for repeatable prompts.",
}


def pretty_print_schema_types() -> str:
    """Return a pretty-printed string of available schema types."""
    return ", ".join([f'"{stype}"' for stype in SCHEMAS.keys()])


# Create server instance
server = FastMCP(
    name="amsl-schemas-mcp",
    instructions="Provides AMSL schema resources and validation. Always, when asked for AMSL schemas or validation, use the tools provided. Known schemas are "
    + pretty_print_schema_types(),
)

# Schema cache
_schema_cache: dict[str, dict[str, Any]] = {}


async def load_schema(schema_type: str) -> dict[str, Any]:
    """Load a schema from file with caching.

    Args:
        schema_type: The type of schema to load (e.g., 'collection', 'assessment')

    Returns:
        The schema as a dictionary

    Raises:
        httpx.HTTPError: If the schema cannot be fetched
    """
    # Return cached schema if available
    if schema_type in _schema_cache:
        logger.debug(f"Returning cached schema for '{schema_type}'")
        return _schema_cache[schema_type]

    # Fetch and cache the schema
    url = f"{SCHEMAS_ROOT}{schema_type}.json"
    logger.debug(f"Fetching schema from {url}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        schema = response.json()
        _schema_cache[schema_type] = schema
        logger.debug(f"Cached schema for '{schema_type}'")
        return schema


@server.tool(
    name="List-AMSL-Schema-Types",
    description="List all available AMSL schema types.",
)
async def list_amsl_schema_types() -> dict[str, str]:
    """List all available AMSL schema types."""
    return SCHEMAS


@server.tool(
    name="Get-AMSL-Schema",
    description="Get the AMSL schema for a specified type. Valid types are: "
    + pretty_print_schema_types(),
)
async def get_amsl_schema(schema_type: str) -> dict[str, Any]:
    """Get the AMSL schema for the specified type."""

    if schema_type not in SCHEMAS.keys():
        raise ValueError(
            f"Invalid schema type '{schema_type}'. Valid types are: {pretty_print_schema_types()}"
        )

    schema = await load_schema(schema_type)
    return schema


@server.tool(
    name="Validate-AMSL-Schema",
    description="Validate data against an AMSL schema by type. Valid types are: "
    + pretty_print_schema_types(),
)
async def validate_amsl_schema(
    data: dict[str, Any],
    schema_type: str,
) -> dict[str, Any]:
    """Validate data against the AMSL schema for the specified type."""

    if schema_type not in SCHEMAS.keys():
        raise ValueError(
            f"Invalid schema type '{schema_type}'. Valid types are: {pretty_print_schema_types()}"
        )

    schema = await load_schema(schema_type)
    try:
        jsonschema.validate(instance=data, schema=schema)
        return {"valid": True, "message": "Data is valid."}
    except jsonschema.ValidationError as e:
        return {"valid": False, "message": str(e)}


def main() -> None:
    """Entry point for the console script."""
    server.run()


if __name__ == "__main__":
    main()
