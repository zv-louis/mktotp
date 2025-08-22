# encoding: utf-8-sig
import os
from .secrets import SecretMgr
from .qrcode_util import decode_qrcode
from .logutil import get_logger

# ----------------------------------------------------------------------------
def register_secret(qr_code_file: str | os.PathLike,
                    new_name: str,
                    secrets_file: str | os.PathLike) -> list[dict[str, str]]:
    """
    Register a new secret from a QR code file.

    Args:
        qr_code_file (str | os.PathLike):
            Path to the QR code file.
            Supported formats are PNG, JPEG, TIFF, BMP, and SVG.
        new_name (str):
            The name to assign to the new secret.
        secrets_file (str | os.PathLike):
            Path to the secrets file.
    Returns:
        list[dict[str, str]]: A list of dictionaries containing the new secret's details.
    
    Raises:
        FileNotFoundError: If the QR code file does not exist.
        ValueError: If the QR code file is invalid or does not contain valid data.
    """
    result = []
    with SecretMgr(secrets_file) as mgr:
        mgr.load()  # Load existing secrets
        qrcode_datas = decode_qrcode(qr_code_file)
        result = mgr.register_secret(new_name, qrcode_datas)
        mgr.save()
    return result

# ----------------------------------------------------------------------------
def gen_token(name: str,
              secrets_file: str | os.PathLike) -> str:
    """
    Generate a TOTP token for a given secret name.

    Args:
        name (str):
            The name of the secret for which to generate the token.
        secrets_file (str | os.PathLike):
            Path to the secrets file.
    
    Returns:
        str: The generated TOTP token.
    Raises:
        FileNotFoundError: If the secrets file does not exist.
        ValueError: If the secret name is not found in the secrets file.
    """
    token = ""
    with SecretMgr(secrets_file) as mgr:
        mgr.load()
        token = mgr.gen_totp_token(name)
    return token

# ----------------------------------------------------------------------------
def get_secret_list(secrets_file: str | os.PathLike):
    """
    Get a list of all secrets in the secrets file.

    Args:
        secrets_file (str | os.PathLike):
            Path to the secrets file.
    
    Returns:
        list[dict[str, str]]:
            A list of dictionaries containing secret names and their details.
    Raises:
        FileNotFoundError: If the secrets file does not exist.
        ValueError: If the secrets file is invalid or cannot be read.
    """
    ret_list = []
    with SecretMgr(secrets_file) as mgr:
        mgr.load()
        ret_list = mgr.list_secrets(include_secret=False)

    return ret_list

# ----------------------------------------------------------------------------
def remove_secrets(names: list[str],
                   secrets_file: str | os.PathLike) -> list[str]:
    """
    Remove secrets by their names.

    Args:
        names (list[str]):
            List of secret names to remove.
        secrets_file (str | os.PathLike):
            Path to the secrets file.
    
    Returns:
        list[str]: A list of names of the removed secrets.
    
    Raises:
        FileNotFoundError:
            If the secrets file does not exist.
        ValueError:
            If the names are not found in the secrets file.
    """
    result = []
    with SecretMgr(secrets_file) as mgr:
        mgr.load()
        result = mgr.remove_secrets(names)
        if result:
            mgr.save()
    return result

# ----------------------------------------------------------------------------
def rename_secret(name: str,
                  new_name: str,
                  secrets_file: str | os.PathLike) -> bool:
    """
    Rename an existing secret.

    Args:
        name (str):
            The current name of the secret to rename.
        new_name (str):
            The new name to assign to the secret.
        secrets_file (str | os.PathLike):
            sPath to the secrets file.
    
    Returns:
        bool: True if the secret was renamed successfully, False otherwise.
    
    Raises:
        FileNotFoundError:
            If the secrets file does not exist.
        ValueError:
            If the secret name is not found in the secrets file.
    """
    result = False
    with SecretMgr(secrets_file) as mgr:
        mgr.load()
        result = mgr.rename_secret(name, new_name)
        if result:
            mgr.save()
    return result
