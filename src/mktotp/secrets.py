# encoding: utf-8-sig

import os
import sys
import json
import datetime
import pyotp
from pathlib import Path

from .logutil import get_logger
from .permutil import set_secure_permissions, check_file_permissions

# ----------------------------------------------------------------------------
# Secret Information Class
class SecretMgr:
    """
    Class to handle secret information stored in a JSON file.
    """
    
    # ----------------------------------------------------------------------------
    def __init__(self, secrets_file: str | os.PathLike = None):
        """
        Initialize the SecretDic class.

        Args:
            secrets_file (str | os.PathLike, optional): Path to the secrets JSON file. Defaults to None.
        """
        # Initialize an empty dictionary to hold secret data
        self.secret_data = {}
        self.secrets_file: Path = None

        if secrets_file is None:
            user_home = os.path.expanduser("~")
            secrets_file = Path(user_home) / ".mktotp" / "data" / "secrets.json"
            self.secrets_file = secrets_file
        else:
            self.secrets_file = Path(secrets_file)

    # ----------------------------------------------------------------------------
    def load(self):
        """
        Load secrets from the JSON file into the secret_data dictionary.
        Raises:
            FileNotFoundError: If the secrets file does not exist.
            PermissionError: If there are permission issues accessing the file.
            json.JSONDecodeError: If the file content is not valid JSON.
            ValueError: If the data format is invalid.
        Returns:
            None
        """
        try:
            # Check and fix file permissions if needed
            if self.secrets_file.exists():
                if not check_file_permissions(self.secrets_file):
                    get_logger().warning(f"Fixing file permissions on {self.secrets_file}")
                    set_secure_permissions(self.secrets_file)
            
            with open(self.secrets_file, 'r', encoding='utf-8') as file:
                raw_data = json.load(file)

            # Check if raw_data is a dictionary
            if not isinstance(raw_data, dict):
                get_logger().error(f"Invalid data format in {self.secrets_file}")
                raise ValueError("Invalid data format in secrets file")
            else:
                # get 'secret' as array
                secrets = raw_data.get('secrets', [])
                if isinstance(secrets, list):
                    for secret in secrets:
                        if isinstance(secret, dict):
                            # Use 'name' as key and 'value' as value
                            name = secret.get('name')
                            if name:
                                self.secret_data[name] = secret
                                get_logger().debug(f"Loaded secret '{name}'")
                else:
                    get_logger().error(f"Invalid 'secret' format in {self.secrets_file}")
                    raise ValueError("Invalid 'secret' format in secrets file")

        except FileNotFoundError:
            get_logger().error(f"Secrets file not found: {self.secrets_file}")
            raise
        except PermissionError:
            get_logger().error(f"Permission denied for secrets file: {self.secrets_file}")
            raise
        except FileNotFoundError:
            get_logger().error(f"Secrets file not found: {self.secrets_file}")
            raise
        except PermissionError:
            get_logger().error(f"Permission denied for secrets file: {self.secrets_file}")
            raise
        except json.JSONDecodeError:
            get_logger().error(f"Error decoding JSON from secrets file: {self.secrets_file}")
            raise
        except Exception as e:
            get_logger().error(f"Unexpected error while loading secrets: {e}")
            raise

        get_logger().info(f"Secrets loaded successfully from {self.secrets_file}")

    # ----------------------------------------------------------------------------
    def get_secret(self, key: str) -> str|None:
        """
        Get the secret value for a given key.
        If the key does not exist, returns None.

        Args:
            key (str): The key for which to retrieve the secret value.

        Returns:
            tuple[str|None, str|None] : The secret value if found, otherwise None.
        """
        secret_obj = self.secret_data.get(key, {})
        secret = secret_obj.get('secret', None)
        return secret

    # ----------------------------------------------------------------------------
    def gen_totp_token(self,
                       token_name: str) -> str:
        """
        Get the TOTP token.
        Args:
            token_name (str): The name of the token to retrieve.
        Returns:
            str: The TOTP token as a string.
        """
        token: str = ""
        secret = self.get_secret(token_name)
        if secret:
            totp_obj = pyotp.TOTP(s=secret)
            token = totp_obj.now()
        else:
            get_logger().error(f"Secret for token '{token_name}' not found.")
            raise ValueError(f"Secret for token '{token_name}' not found.")
        return token

    # ----------------------------------------------------------------------------
    def register_secret(self,
                        name: str,
                        qrc_datas: list[str]) -> list[dict[str, str]]:
        """
        Register a new secret with the given name and QR code data.

        Args:
            name (str): The name of the secret.
            qrc_datas (list[str]): List of QR code data strings.

        Raises:
            ValueError: If the name is already registered.
        """
        result = []
        cnt = 1
        for qrc_data in qrc_datas:
            try:
                totp = pyotp.parse_uri(qrc_data)  # Validate the QR code data
                if totp:
                    account  = totp.name
                    issuer   = totp.issuer
                    secret   = totp.secret
                    sec_name = name if cnt == 1 else f'{name}_{cnt}'
                    sec_data = {
                        'name': sec_name,
                        'account': account,
                        'issuer': issuer,
                        'secret': secret
                    }
                    self.secret_data[sec_name] = sec_data
                    result.append(sec_data)
                    get_logger().debug(f"Registered secret '{sec_name}' for account '{account}' with issuer '{issuer}'.")
                    # Increment the counter for the next secret
                    cnt += 1
                else:
                    get_logger().error(f"Invalid QR code data: {qrc_data}")
                    raise ValueError(f"Invalid QR code data: {qrc_data}")
            except (ValueError, Exception) as e:
                get_logger().error(f"Invalid QR code data: {qrc_data}")
                raise ValueError(f"Invalid QR code data: {qrc_data}")
        return result

    # ----------------------------------------------------------------------------
    def save(self) -> None:
        """
        Save the current secrets to the JSON file.
        Raises:
            IOError: If there is an error writing to the file.
        """
        try:
            # Ensure the directory exists with proper permissions
            self.secrets_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            
            # Create a temporary file to write the secrets
            work_path = Path(self.secrets_file).with_suffix('.tmp')
            with open(work_path, 'w', encoding='utf-8') as file:
                # Convert the secret data to a list of dictionaries
                now_ts = datetime.datetime.now().astimezone()
                # get string representation of the current time with current timezone
                last_update = now_ts.isoformat(timespec='microseconds')
                # Prepare the data to be saved
                dump_dic = {
                    'secrets': list(self.secret_data.values()),
                    'version': '1.0',
                    'last_update': last_update
                }
                json.dump(dump_dic, file, indent=4, ensure_ascii=False)
            
            # Set secure permissions on temporary file
            set_secure_permissions(work_path)
            
            # Rename the temporary file to the original secrets file
            if self.secrets_file.is_file():
                backup_path = self.secrets_file.with_suffix('.bak')
                if backup_path.is_file():
                    backup_path.unlink()
                self.secrets_file.rename(backup_path)
            work_path.rename(self.secrets_file)
            
            # Ensure the final file also has secure permissions
            set_secure_permissions(self.secrets_file)
            
            get_logger().info(f"Secrets saved successfully to {self.secrets_file}")
        except IOError as e:
            get_logger().error(f"Error saving secrets to file: {e}")
            raise IOError(f"Error saving secrets to file: {e}")

    # ----------------------------------------------------------------------------
    def remove_secret(self, name: str) -> bool:
        """
        Remove a secret by its name.

        Args:
            name (str): The name of the secret to remove.

        Returns:
            bool: True if the secret was removed, False if it was not found.
        """
        result = False
        if name in self.secret_data:
            del self.secret_data[name]
            get_logger().info(f"Secret '{name}' removed successfully.")
            result = True
        else:
            get_logger().info(f"Secret '{name}' not found.")
        return result

    # ----------------------------------------------------------------------------
    def rename_secret(self, old_name: str, new_name: str) -> bool:
        """
        Rename a secret from old_name to new_name.

        Args:
            old_name (str): The current name of the secret.
            new_name (str): The new name for the secret.

        Returns:
            bool: True if the secret was renamed, False if it was not found.
        """
        result = False
        if old_name in self.secret_data:
            secret = self.secret_data[old_name]
            secret['name'] = new_name
            self.secret_data[new_name] = secret
            del self.secret_data[old_name]
            get_logger().info(f"Secret '{old_name}' renamed to '{new_name}' successfully.")
            result = True
        else:
            get_logger().info(f"Secret '{old_name}' not found.")
        return result
    
    # ----------------------------------------------------------------------------
    def list_secrets(self) -> list[dict[str, str]]:
        """
        List all registered secrets.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing secret information.
        """
        return list(self.secret_data.values())

    # ----------------------------------------------------------------------------
    def __str__(self) -> str:
        """
        String representation of the SecretDic object.
        Returns:
            str: A string representation of the secret data.
        """
        return json.dumps(self.secret_data, indent=2, ensure_ascii=False)

    # ----------------------------------------------------------------------------
    def __repr__(self) -> str:
        """
        String representation of the SecretDic object for debugging.
        Returns:
            str: A string representation of the secret data.
        """
        return self.__str__()

