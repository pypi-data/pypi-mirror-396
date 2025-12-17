from .lesb import lesbRequest
from pydantic import BaseModel
from mcp.shared.exceptions import McpError
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server
from mcp.server import Server
from typing import Sequence
from enum import Enum
import json

from pydantic import BaseModel


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                    handlers=[
                        logging.FileHandler('ssp.log', encoding='utf-8')])
logger = logging.getLogger(__name__)


class SSPTools(str, Enum):
    QUERY_PERAGE_AND_CBXX = "queryPerAgeAndCbxx"


class QueryPerAgeAndCbxxResult(BaseModel):
    _lesb__errcode_: str
    errflag: str
    errtext: str
    perinfo: str


class SSPServer:
    def queryPerAgeAndCbxx(self, ip: str, sfzhm: str, rsxtid: str) -> QueryPerAgeAndCbxxResult:
        """Get current time in specified timezone"""
        response = lesbRequest(ip, 'SiServiceCenter',
                               'queryPerAgeAndCbxx', {'sfzhm': sfzhm, 'rsxtid': rsxtid})

        return QueryPerAgeAndCbxxResult(**response)


async def serve(ip: str | None = None) -> None:
    logger.info(f"Using ip: {ip}")

    server = Server("mcp-ssp")
    ssp_server = SSPServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available time tools."""
        return [
            Tool(
                name=SSPTools.QUERY_PERAGE_AND_CBXX.value,
                description="Get a person's age and social insurance enrollment information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sfzhm": {
                            "type": "string",
                            "description": f"ID Number. (e.g., '37010119760201001X').",
                        },
                        "rsxtid": {
                            "type": "string",
                            "description": f"Region Code. (e.g., '3751').",
                        }
                    },
                    "required": ["sfzhm", "rsxtid"],
                },
            ),

        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls for time queries."""
        try:
            match name:
                case SSPTools.QUERY_PERAGE_AND_CBXX.value:
                    sfzhm = arguments.get("sfzhm")
                    rsxtid = arguments.get("rsxtid")

                    if not ip:
                        raise ValueError("Missing required argument: ip")
                    if not sfzhm:
                        raise ValueError("Missing required argument: sfzhm")
                    if not rsxtid:
                        raise ValueError("Missing required argument: rsxtid")

                    result = ssp_server.queryPerAgeAndCbxx(ip, sfzhm, rsxtid)

                case _:
                    raise ValueError(f"Unknown tool: {name}")

            return [
                TextContent(type="text", text=json.dumps(
                    result.model_dump(), indent=2))
            ]
        except Exception as e:
            raise ValueError(
                f"Error processing mcp-server-time query: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)
    return None
