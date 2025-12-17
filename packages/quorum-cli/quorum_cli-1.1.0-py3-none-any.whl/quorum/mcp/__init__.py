"""MCP server for Quorum multi-agent discussions."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from quorum.config import get_settings
from quorum.ipc import VALID_METHODS
from quorum.providers import list_all_models_sync
from quorum.team import FourPhaseConsensusTeam

# Method descriptions for the resource
METHOD_INFO = {
    "standard": {
        "name": "Standard",
        "description": "Balanced 5-phase discussion",
        "best_for": "General questions, balanced analysis",
        "phases": ["Answer", "Critique", "Discuss", "Position", "Synthesis"],
    },
    "oxford": {
        "name": "Oxford",
        "description": "Formal debate with FOR/AGAINST teams",
        "best_for": "Controversial topics, policy debates",
        "requires": "Even number of models (2, 4, 6...)",
        "phases": ["Opening", "Rebuttal", "Closing", "Judgement"],
    },
    "advocate": {
        "name": "Advocate",
        "description": "Devil's advocate challenges the group",
        "best_for": "Risk analysis, finding flaws",
        "requires": "3+ models",
        "phases": ["Initial Position", "Cross-Examination", "Verdict"],
    },
    "socratic": {
        "name": "Socratic",
        "description": "Deep inquiry through questioning",
        "best_for": "Deep understanding, exploring fundamentals",
        "phases": ["Thesis", "Inquiry", "Aporia"],
    },
    "delphi": {
        "name": "Delphi",
        "description": "Iterative consensus for estimates",
        "best_for": "Forecasts, time estimates, quantitative predictions",
        "requires": "3+ models",
        "phases": ["Round 1", "Round 2", "Round 3", "Aggregation"],
    },
    "brainstorm": {
        "name": "Brainstorm",
        "description": "Creative ideation",
        "best_for": "Generating ideas, creative solutions",
        "phases": ["Diverge", "Build", "Converge", "Synthesis"],
    },
    "tradeoff": {
        "name": "Tradeoff",
        "description": "Structured comparison of alternatives",
        "best_for": "A vs B decisions, multi-criteria analysis",
        "phases": ["Frame", "Criteria", "Evaluate", "Decide"],
    },
}

server = Server("quorum")


# ─────────────────────────────────────────────────────────────
# Resources
# ─────────────────────────────────────────────────────────────


@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available Quorum resources."""
    return [
        types.Resource(
            uri="quorum://models",
            name="Available Models",
            description="AI models configured for Quorum discussions",
            mimeType="application/json",
        ),
        types.Resource(
            uri="quorum://methods",
            name="Discussion Methods",
            description="The 7 discussion methods available in Quorum",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a Quorum resource."""
    if uri == "quorum://models":
        models = list_all_models_sync()
        return json.dumps(models, indent=2)

    if uri == "quorum://methods":
        return json.dumps(METHOD_INFO, indent=2)

    raise ValueError(f"Unknown resource: {uri}")


# ─────────────────────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────────────────────


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available Quorum tools."""
    return [
        types.Tool(
            name="quorum_discuss",
            description="Run a multi-model AI discussion using Quorum. After the discussion completes, present the synthesis to the user in a clear, readable format.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question or topic to discuss",
                    },
                    "models": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Model IDs to participate (e.g., ['gpt-4o', 'claude-sonnet'])",
                    },
                    "method": {
                        "type": "string",
                        "enum": list(VALID_METHODS),
                        "default": "standard",
                        "description": "Discussion method to use",
                    },
                    "full_output": {
                        "type": "boolean",
                        "default": False,
                        "description": "Return full discussion (all phases). Default: false (only synthesis)",
                    },
                },
                "required": ["question", "models"],
            },
        ),
        types.Tool(
            name="quorum_list_models",
            description="List all available AI models configured for Quorum",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle tool calls."""
    if name == "quorum_list_models":
        return await _handle_list_models()

    if name == "quorum_discuss":
        return await _handle_discuss(arguments)

    raise ValueError(f"Unknown tool: {name}")


async def _handle_list_models() -> list[types.TextContent]:
    """List all available models."""
    from dataclasses import asdict

    models = list_all_models_sync()
    # Convert ModelInfo dataclasses to dicts for JSON serialization
    serializable = {
        provider: [asdict(m) for m in model_list]
        for provider, model_list in models.items()
    }
    return [types.TextContent(type="text", text=json.dumps(serializable, indent=2))]


async def _handle_discuss(args: dict[str, Any]) -> list[types.TextContent]:
    """Run a Quorum discussion."""
    question = args["question"]
    model_ids = args["models"]
    method = args.get("method", "standard")
    full_output = args.get("full_output", False)

    team = FourPhaseConsensusTeam(
        model_ids=model_ids,
        method_override=method,
    )

    # Collect messages
    synthesis = None
    all_messages = []

    async for msg in team.run_stream(question):
        if hasattr(msg, "__dict__"):
            msg_dict = {
                "type": type(msg).__name__,
                **msg.__dict__,
            }
            all_messages.append(msg_dict)

            # Capture synthesis for compact output
            if type(msg).__name__ == "SynthesisResult":
                synthesis = msg_dict

    # Return full output or just synthesis
    if full_output:
        return [types.TextContent(type="text", text=json.dumps(all_messages, indent=2))]

    # Compact: return only synthesis
    if synthesis:
        # Clean up synthesis for readability
        compact_result = {
            "consensus": synthesis.get("consensus"),
            "synthesis": synthesis.get("synthesis"),
            "differences": synthesis.get("differences"),
            "method": synthesis.get("method"),
            "models": model_ids,
        }
        return [types.TextContent(type="text", text=json.dumps(compact_result, indent=2))]

    # Fallback if no synthesis (shouldn't happen)
    return [types.TextContent(type="text", text=json.dumps(all_messages, indent=2))]


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────


async def _run_server() -> None:
    """Run the MCP server with stdio transport."""
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="quorum",
                server_version="1.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main() -> None:
    """Run the Quorum MCP server."""
    # Verify config exists
    settings = get_settings()
    if not settings.available_providers:
        print(
            "No providers configured. Run 'quorum' first to configure.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Run server
    asyncio.run(_run_server())


if __name__ == "__main__":
    main()
