import click
import os

from mcp.server.fastmcp import Context, FastMCP
from llama_cloud_services import LlamaExtract, LlamaParse
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from typing import Awaitable, Callable, Optional
from dotenv import load_dotenv

load_dotenv()
mcp = FastMCP("llama-index-server")


def make_index_tool(
    index_name: str, project_id: Optional[str], org_id: Optional[str]
) -> Callable[[Context, str], Awaitable[str]]:
    async def tool(ctx: Context, query: str) -> str:
        try:
            await ctx.info(f"Querying index: {index_name} with query: {query}")
            index = LlamaCloudIndex(
                name=index_name,
                project_id=project_id,
                organization_id=org_id,
            )
            response = await index.as_retriever().aretrieve(query)
            return str(response)
        except Exception as e:
            await ctx.error(f"Error querying index: {str(e)}")
            return f"Error querying index: {str(e)}"

    return tool


def make_extract_tool(
    agent_name: str, project_id: Optional[str], org_id: Optional[str]
) -> Callable[[Context, str], Awaitable[str]]:
    async def tool(ctx: Context, file_path: str) -> str:
        """Extract data using a LlamaExtract Agent from the given file."""
        try:
            await ctx.info(
                f"Extracting data using agent: {agent_name} with file path: {file_path}"
            )
            llama_extract = LlamaExtract(
                organization_id=org_id,
                project_id=project_id,
            )
            extract_agent = llama_extract.get_agent(name=agent_name)
            result = await extract_agent.aextract(file_path)
            return str(result)
        except Exception as e:
            await ctx.error(f"Error extracting data: {str(e)}")
            return f"Error extracting data: {str(e)}"

    return tool


def make_parse_document_tool() -> Callable[[Context, str, str], Awaitable[str]]:
    async def tool(ctx: Context, file_path: str, parse_mode: str = "parse_page_with_llm") -> str:
        """Parse a document and extract text + image understanding.
        
        Args:
            file_path: Path to the document file (PDF, DOCX, etc.)
            parse_mode: Parsing mode to use. Options:
                
                PAGE-LEVEL MODES (process one page at a time):
                - "parse_page_without_llm": No AI. Fastest and cheapest. Plain text extraction only. 
                  Best for simple text-only documents.
                - "parse_page_with_llm": Default LLM mode (DEFAULT). OCR + LLM layout reconstruction. 
                  Good balance for docs with text, images, and tables.
                - "parse_page_with_lvm": Vision model mode. Sends page screenshots to vision model. 
                  Best for visually complex docs like diagrams, charts, design-heavy reports.
                - "parse_page_with_agent": Premium agentic mode. Highest quality. 
                  Combines OCR + vision + agentic reasoning. Best for complex docs with tables, 
                  images, scanned content, equations, diagrams.
                - "parse_page_with_layout_agent": Layout-preserving mode. Maintains exact positioning. 
                  Best for documents requiring precise visual citations or dense newspaper-like layouts.
                
                DOCUMENT-LEVEL MODES (process entire document at once):
                - "parse_document_with_llm": Multi-page continuity with LLM. 
                  Best for long tables or sections spanning multiple pages.
                - "parse_document_with_agent": Multi-page continuity with agentic reasoning. 
                  Best for complex documents with visual elements spanning multiple pages.
        """
        valid_modes = [
            "parse_page_without_llm",
            "parse_page_with_llm",
            "parse_page_with_lvm",
            "parse_page_with_agent",
            "parse_page_with_layout_agent",
            "parse_document_with_llm",
            "parse_document_with_agent",
        ]
        if parse_mode not in valid_modes:
            return f"Invalid parse_mode '{parse_mode}'. Valid options: {valid_modes}"
        
        try:
            await ctx.info(f"Parsing document: {file_path} with mode: {parse_mode}")
            parser = LlamaParse(
                result_type="markdown",
                parse_mode=parse_mode,
                verbose=False
            )
            result = await parser.aload_data(file_path)
            
            full_text = "\n\n---\n\n".join([doc.text for doc in result])
            await ctx.info(f"Parsed {len(result)} pages, {len(full_text)} characters")
            
            # Append parsing mode info for user awareness
            mode_info = f"""

---
**📄 Parsing Info:**
- **Mode used:** `{parse_mode}`
- **Pages parsed:** {len(result)}
- **Characters extracted:** {len(full_text):,}

**Other available modes (re-run if needed):**
- `parse_page_without_llm` - Fastest/cheapest, no AI
- `parse_page_with_llm` - Default LLM (default), good for mixed content
- `parse_page_with_lvm` - Vision model, best for diagrams/charts
- `parse_page_with_agent` - Premium, best quality
- `parse_page_with_layout_agent` - Precise layout preservation
- `parse_document_with_llm` - Multi-page continuity
- `parse_document_with_agent` - Multi-page + agentic reasoning
"""
            return full_text + mode_info
        except Exception as e:
            await ctx.error(f"Error parsing document: {str(e)}")
            return f"Error parsing document: {str(e)}"

    return tool


@click.command()
@click.option(
    "--index",
    "indexes",
    multiple=True,
    required=False,
    type=str,
    help="Index definition in the format name:description. Can be used multiple times.",
)
@click.option(
    "--extract-agent",
    "extract_agents",
    multiple=True,
    required=False,
    type=str,
    help="Extract agent definition in the format name:description. Can be used multiple times.",
)
@click.option(
    "--project-id", required=False, type=str, help="Project ID for LlamaCloud"
)
@click.option(
    "--org-id", required=False, type=str, help="Organization ID for LlamaCloud"
)
@click.option(
    "--transport",
    default="stdio",
    type=click.Choice(["stdio", "sse", "streamable-http"]),
    help='Transport to run the MCP server on. One of "stdio", "sse", "streamable-http".',
)
@click.option("--api-key", required=False, type=str, help="API key for LlamaCloud")
def main(
    indexes: Optional[list[str]],
    extract_agents: Optional[list[str]],
    project_id: Optional[str],
    org_id: Optional[str],
    transport: str,
    api_key: Optional[str],
) -> None:
    api_key = api_key or os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        raise click.BadParameter(
            "API key not found. Please provide an API key or set the LLAMA_CLOUD_API_KEY environment variable."
        )
    else:
        os.environ["LLAMA_CLOUD_API_KEY"] = api_key

    # Parse indexes into (name, description) tuples
    index_info = []
    if indexes:
        for idx in indexes:
            if ":" not in idx:
                raise click.BadParameter(
                    f"Index '{idx}' must be in the format name:description"
                )
            name, description = idx.split(":", 1)
            index_info.append((name, description))

    # Parse extract agents into (name, description) tuples if provided
    extract_agent_info = []
    if extract_agents:
        for agent in extract_agents:
            if ":" not in agent:
                raise click.BadParameter(
                    f"Extract agent '{agent}' must be in the format name:description"
                )
            name, description = agent.split(":", 1)
            extract_agent_info.append((name, description))

    # Dynamically register a tool for each index
    for name, description in index_info:
        tool_func = make_index_tool(name, project_id, org_id)
        mcp.tool(name=f"query_{name}", description=description)(tool_func)

    # Dynamically register a tool for each extract agent, if any
    for name, description in extract_agent_info:
        tool_func = make_extract_tool(name, project_id, org_id)
        mcp.tool(name=f"extract_{name}", description=description)(tool_func)

    # Register the parse_document tool
    parse_tool = make_parse_document_tool()
    mcp.tool(
        name="parse_document",
        description="""Parse a document (PDF, DOCX, etc.) and extract text with image understanding.

Accepts file_path and optional parse_mode parameter.

PARSE MODES (from cheapest/fastest to highest quality):
• parse_page_without_llm - No AI, plain text only. Fastest/cheapest.
• parse_page_with_llm - Default LLM mode. Good for mixed content.
• parse_page_with_lvm - Vision model. Best for diagrams/charts.
• parse_page_with_agent - Premium (DEFAULT). Best quality for complex docs.
• parse_page_with_layout_agent - Precise layout preservation.
• parse_document_with_llm - Multi-page continuity.
• parse_document_with_agent - Multi-page + agentic reasoning.

Returns markdown with text and image descriptions.""",
    )(parse_tool)

    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
