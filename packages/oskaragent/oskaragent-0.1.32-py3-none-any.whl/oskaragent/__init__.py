"""oskaragent agent package.

Exports:
- `oskaragent`: main agent class
- `AgentConfig`: configuration class for the agent
- Tool utilities and contexts from `.agent_tools` for convenience
"""

from __future__ import annotations

from .agent import Oskar
from .agent_config import AgentConfig
from .converters import (
    convert_csv_to_markdown_table,
    convert_docx_to_markdown,
    convert_pptx_to_markdown,
    convert_markdown_to_html,
    convert_markdown_to_html_block,
    convert_markdown_to_pdf,
    convert_pdf_to_markdown,
    convert_dict_to_markdown,
    convert_json_to_markdown,
    convert_json_to_csv,

    decode_file_from_str,
    encode_file,
)


__all__ = [
    "Oskar",
    "AgentConfig",

    # converters
    "convert_csv_to_markdown_table",
    "convert_dict_to_markdown",
    "convert_docx_to_markdown",
    "convert_markdown_to_html",
    "convert_markdown_to_html_block",
    "convert_markdown_to_pdf",
    "convert_pdf_to_markdown",
    "convert_pptx_to_markdown",
    "convert_json_to_markdown",
    "convert_json_to_csv",

    # encoders
    "decode_file_from_str",
    "encode_file",
]