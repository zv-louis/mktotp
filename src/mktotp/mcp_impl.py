# encoding : utf-8

import asyncio
import traceback
from pathlib import Path

from fastmcp import Client, FastMCP
from fastmcp.client.transports import FastMCPTransport
from typing import Annotated, Any
from pydantic import Field

from .func_impl import *
from .logutil import get_logger

# -------------------------------------------------------------------------------------------
# Common error handling helper for MCP tools
async def handle_operation(operation: str, func, **kwargs):
    """
    Common error handler for MCP operations with detailed logging.

    Args:
        operation (str): Name of the operation being performed
        func: The function to execute
        **kwargs: Arguments to pass to the function
    """
    logger = get_logger()
    try:
        # Log operation start
        logger.info(f"MCP operation started: {operation}")
        logger.debug(f"Operation parameters: {kwargs}")
        # Execute the operation
        result = func(**kwargs)
        # Log successful completion
        logger.info(f"MCP operation completed successfully: {operation}")
        return result
    except FileNotFoundError as e:
        error_msg = f"File not found in {operation}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except PermissionError as e:
        error_msg = f"Permission denied in {operation}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except KeyError as e:
        error_msg = f"Key not found in {operation}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except ValueError as e:
        error_msg = f"Value error in {operation}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error in {operation}: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise ValueError(error_msg)

# -------------------------------------------------------------------------------------------
# Input validation helper
def validate_file_path(file_path: str | None, operation: str, required: bool = False) -> None:
    """
    Validate file path for MCP operations.

    Args:
        file_path (str | None): Path to validate
        operation (str): Operation name for error messages
        required (bool): Whether the file path is required
    """
    if required and not file_path:
        raise ValueError(f"File path is required for {operation}")

    if file_path:
        path = Path(file_path)
        if required and not path.exists():
            raise FileNotFoundError(f"File not found for {operation}: {file_path}")

        # Check if parent directory exists for new files
        if not path.exists() and not path.parent.exists():
            raise FileNotFoundError(f"Parent directory not found for {operation}: {path.parent}")

# -------------------------------------------------------------------------------------------------------
# Validate secret name for MCP operations
def validate_secret_name(name: str, operation: str) -> None:
    """
    Validate secret name for MCP operations.

    Args:
        name (str): Secret name to validate
        operation (str): Operation name for error messages
    """
    if not name or not name.strip():
        raise ValueError(f"Secret name cannot be empty for {operation}")

    if len(name.strip()) > 100:  # Reasonable limit
        raise ValueError(f"Secret name too long for {operation} (max 100 characters)")



# -------------------------------------------------------------------------------------------
# mcp tool for registering a secret from QR code
async def mktotp_register_secret_impl(
        qr_code_image_file_path:  Annotated[str, Field(description="Path to the QR code image file.")],
        new_name: Annotated[str, Field(description="Name to assign to the new secret.")],
        secrets_file: Annotated[str, Field(description="Path to the secrets file. If empty string, the default secrets file will be used.")],
    ) -> list[dict[str, str]]:
    """
    Register a new secret from a QR code image file and return the details of the registered secret.

    Args:
        qr_code_image_file_path (str):
            Path to the QR code image file.
        new_name (str):
            Name to assign to the new secret.
        secrets_file (str):
            Path to the secrets file. If empty string, the default secrets file will be used.
    Returns:
        list[dict[str, str]]: List of dictionaries containing the details of the registered secret.
    Raises:
        ValueError: If any validation fails or operation encounters an error.
    """
    # Input validation
    logger = get_logger()
    validate_file_path(qr_code_image_file_path, "register_secret", required=True)
    validate_secret_name(new_name, "register_secret")
    if secrets_file and secrets_file.strip():
        validate_file_path(secrets_file, "register_secret", required=False)

    logger.info(f"Registering secret '{new_name}' from QR code: {qr_code_image_file_path}")
    return await handle_operation(
        "register_secret",
        register_secret,
        qr_code_file=qr_code_image_file_path,
        new_name=new_name,
        secrets_file=secrets_file
    )

# -------------------------------------------------------------------------------------------
# mcp tool for generating TOTP token
async def mktotp_generate_token_impl(
        secret_name: Annotated[str, Field(description="Name of the secret for which to generate the token.")],
        secrets_file: Annotated[str, Field(description="Path to the secrets file. If empty string, the default secrets file will be used.")],
    ) -> str:
    """
    Generate a TOTP token for a given secret name.

    Args:
        secret_name (str):
            Name of the secret for which to generate the token.
        secrets_file (str):
            Path to the secrets file. If empty string, the default secrets file will be used.
    Returns:
        str: The generated TOTP token.
    Raises:
        ValueError: If any validation fails or operation encounters an error.
    """
    # Input validation
    logger = get_logger()
    validate_secret_name(secret_name, "generate_token")
    if secrets_file and secrets_file.strip():
        validate_file_path(secrets_file, "generate_token", required=True)

    logger.info(f"Generating TOTP token for secret: {secret_name}")

    return await handle_operation(
        "generate_token",
        gen_token,
        name=secret_name,
        secrets_file=secrets_file
    )

# -------------------------------------------------------------------------------------------
# mcp tool for getting secret information list
async def mktotp_get_secret_info_list_impl(
        secrets_file: Annotated[str, Field(description="Path to the secrets file. If empty string, the default secrets file will be used.")],
    ) -> list[dict[str, str]]:
    """
    Get a list of all secret info in the secrets file without the secret values.

    Args:
        secrets_file (str):
            Path to the secrets file. If empty string, the default secrets file will be used.
    Returns:
        list[dict[str, str]]: A list of dictionaries containing secret names and their details.
    Raises:
        ValueError: If any validation fails or operation encounters an error.
    """

    logger = get_logger()
    # Input validation
    if secrets_file and secrets_file.strip():
        validate_file_path(secrets_file, "get_secret_info_list", required=True)

    logger.info("Retrieving secret information list")

    return await handle_operation(
        "get_secret_info_list",
        get_secret_list,
        secrets_file=secrets_file
    )  


# -------------------------------------------------------------------------------------------
# mcp tool for removing secrets
async def mktotp_remove_secrets_impl(
        secret_names: Annotated[list[str], Field(description="List of secret names to remove.")],
        secrets_file: Annotated[str, Field(description="Path to the secrets file. If empty string, the default secrets file will be used.")],
    ) -> list[str]:
    """
    Remove secrets by their names from the secrets file.
    
    Args:
        secret_names (list[str]):
            List of secret names to remove.
        secrets_file (str):
            Path to the secrets file. If empty string, the default secrets file will be used.
    Returns:
        list[str]: A list of names of the removed secrets.
    Raises:
        ValueError: If any validation fails or operation encounters an error.
    """
    logger = get_logger()
    # Input validation
    if not secret_names:
        raise ValueError("At least one secret name must be provided for removal")

    for name in secret_names:
        validate_secret_name(name, "remove_secrets")

    if secrets_file and secrets_file.strip():
        validate_file_path(secrets_file, "remove_secrets", required=True)

    logger.info(f"Removing {len(secret_names)} secret(s): {', '.join(secret_names)}")

    return await handle_operation(
        "remove_secrets",
        remove_secrets,
        names=secret_names,
        secrets_file=secrets_file
    )

# -------------------------------------------------------------------------------------------
# mcp tool for renaming a secret
async def mktotp_rename_secret_impl(
        old_name: Annotated[str, Field(description="Current name of the secret to rename.")],
        new_name: Annotated[str, Field(description="New name to assign to the secret.")],
        secrets_file: Annotated[str, Field(description="Path to the secrets file. If empty string, the default secrets file will be used.")],
    ) -> bool:
    """
    Rename an existing secret in the secrets file.

    Args:
        old_name (str):
            Current name of the secret to rename.
        new_name (str):
            New name to assign to the secret.
        secrets_file (str):
            Path to the secrets file. If empty string, the default secrets file will be used.
    Returns:
        bool: True if the secret was renamed successfully, False otherwise.
    Raises:
        ValueError: If any validation fails or operation encounters an error.
    """
    logger = get_logger()
    # Input validation
    validate_secret_name(old_name, "rename_secret")
    validate_secret_name(new_name, "rename_secret")

    if old_name == new_name:
        raise ValueError("Old name and new name cannot be the same")
    if secrets_file and secrets_file.strip():
        validate_file_path(secrets_file, "rename_secret", required=True)

    logger.info(f"Renaming secret from '{old_name}' to '{new_name}'")

    return await handle_operation(
        "rename_secret",
        rename_secret,
        name=old_name,
        new_name=new_name,
        secrets_file=secrets_file
    )

