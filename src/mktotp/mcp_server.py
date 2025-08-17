# encoding : utf-8

import asyncio
import traceback
from pathlib import Path

from fastmcp import Client, FastMCP
from fastmcp.client.transports import FastMCPTransport
from typing import Annotated, Any
from pydantic import Field

from .mcp_impl import *
from .logutil import get_logger

# FastMCP instance
mcp = FastMCP("MkTOTP")

# -------------------------------------------------------------------------------------------
# return the FastMCP instance
def get_mcp():
    return mcp

# -------------------------------------------------------------------------------------------
# run the MCP server
def run_as_mcp_server():
    """
    Run the MCP server with stdio transport.
    """
    logger = get_logger()
    try:
        logger.info("Starting MkTOTP MCP server with stdio transport")
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to start MCP server: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise

# -------------------------------------------------------------------------------------------
# display the list of tools available in the MCP server
async def list_server_tools(mcp: FastMCP):
    transport = FastMCPTransport(mcp=mcp)
    async with Client(transport=transport) as client:
        result = await client.list_tools()
        for tool in result:
            print(f"------------------------------------------------")
            print(f"'{tool.name}' : {tool.description}\n")

# -------------------------------------------------------------------------------------------
# helper for running the test
def disp_tools():
    """
    Display all available MCP tools in the server.
    This function runs the list_server_tools function in an event loop.
    """
    logger = get_logger()
    try:
        asyncio.run(list_server_tools(mcp))
        logger.info("Successfully displayed MCP tools list")
    except Exception as e:
        logger.error(f"Failed to display MCP tools: {str(e)}")
        raise

# -------------------------------------------------------------------------------------------
# mcp tool for registering a secret from QR code
@mcp.tool()
async def mktotp_register_secret(
        qr_code_image_file_path:  Annotated[str, Field(description="Path to the QR code image file.")],
        new_name: Annotated[str, Field(description="Name to assign to the new secret.")],
        secrets_file: Annotated[str | None, Field(description="Path to the secrets file. If None, the default secrets file will be used.")],
    ) -> list[dict[str, str]]:
    """
    Register a new secret from a QR code image file and return the details of the registered secret.

    Args:
        qr_code_image_file_path (str):
            Path to the QR code image file.
        new_name (str):
            Name to assign to the new secret.
        secrets_file (str | None):
            Path to the secrets file. If None, the default secrets file will be used.
    Returns:
        list[dict[str, str]]: List of dictionaries containing the details of the registered secret.
    Raises:
        ValueError: If any validation fails or operation encounters an error.
    """

    return await mktotp_register_secret_impl(
        qr_code_image_file_path=qr_code_image_file_path,
        new_name=new_name,
        secrets_file=secrets_file
    )

# -------------------------------------------------------------------------------------------
# mcp tool for generating TOTP token
@mcp.tool()
async def mktotp_generate_token(
        secret_name: Annotated[str, Field(description="Name of the secret for which to generate the token.")],
        secrets_file: Annotated[str | None, Field(description="Path to the secrets file. if None, the default secrets file will be used.")],
    ) -> str:
    """
    Generate a TOTP token for a given secret name.

    Args:
        secret_name (str):
            Name of the secret for which to generate the token.
        secrets_file (str | None):
            Path to the secrets file. If None, the default secrets file will be used.
    Returns:
        str: The generated TOTP token.
    Raises:
        ValueError: If any validation fails or operation encounters an error.
    """
    return await mktotp_generate_token_impl(
        secret_name=secret_name,
        secrets_file=secrets_file
    )

# -------------------------------------------------------------------------------------------
# mcp tool for getting secret information list
@mcp.tool()
async def mktotp_get_secret_info_list(
        secrets_file: Annotated[str | None, Field(description="Path to the secrets file. If None, the default secrets file will be used.")],
    ) -> list[dict[str, str]]:
    """
    Get a list of all secret info in the secrets file without the secret values.

    Args:
        secrets_file (str | None):
            Path to the secrets file. If None, the default secrets file will be used.
    Returns:
        list[dict[str, str]]: A list of dictionaries containing secret names and their details.
    Raises:
        ValueError: If any validation fails or operation encounters an error.
    """
    return await mktotp_get_secret_info_list_impl(
        secrets_file=secrets_file
    )


# -------------------------------------------------------------------------------------------
# mcp tool for removing secrets
@mcp.tool()
async def mktotp_remove_secrets(
        secret_names: Annotated[list[str], Field(description="List of secret names to remove.")],
        secrets_file: Annotated[str | None, Field(description="Path to the secrets file. If None, the default secrets file will be used.")],
    ) -> list[str]:
    """
    Remove secrets by their names from the secrets file.
    
    Args:
        secret_names (list[str]):
            List of secret names to remove.
        secrets_file (str | None):
            Path to the secrets file. If None, the default secrets file will be used.
    Returns:
        list[str]: A list of names of the removed secrets.
    Raises:
        ValueError: If any validation fails or operation encounters an error.
    """  
    return await mktotp_remove_secrets_impl(
        secret_names=secret_names,
        secrets_file=secrets_file
    )

# -------------------------------------------------------------------------------------------
# mcp tool for renaming a secret
@mcp.tool()
async def mktotp_rename_secret(
        old_name: Annotated[str, Field(description="Current name of the secret to rename.")],
        new_name: Annotated[str, Field(description="New name to assign to the secret.")],
        secrets_file: Annotated[str | None, Field(description="Path to the secrets file. If None, the default secrets file will be used.")],
    ) -> bool:
    """
    Rename an existing secret in the secrets file.

    Args:
        old_name (str):
            Current name of the secret to rename.
        new_name (str):
            New name to assign to the secret.
        secrets_file (str | None):
            Path to the secrets file. If None, the default secrets file will be used.
    Returns:
        bool: True if the secret was renamed successfully, False otherwise.
    Raises:
        ValueError: If any validation fails or operation encounters an error.
    """
    return await mktotp_rename_secret_impl(
        old_name=old_name,
        new_name=new_name,
        secrets_file=secrets_file
    )
