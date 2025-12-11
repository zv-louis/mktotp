# encoding: utf-8-sig

import sys
from argparse import ArgumentParser

from .logutil import get_logger
from .func_impl import *
from .cmdparam import *

from .mcp_server import run_as_mcp_server, disp_tools

# ----------------------------------------------------------------------------
def get_strparam(str_param: str | None) -> str | None:
    """
    Helper function to return string parameter or None if empty.
    convert string 'null' to None.
    
    Args:
        str_param (str | None): The input string parameter.
    Returns:
        str | None: The original string or None if empty or 'null'.
    """
    ret_val = None
    if str_param and str_param.lower() != 'null':
        ret_val = str_param
    return ret_val

# ----------------------------------------------------------------------------
def handle_add(args):
    """
    Handle the 'add' command to register a new secret from a QR code file.
    
    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """
    result = []
    secrets_file = get_strparam(args.secrets_file) if args.secrets_file else None
    qrcode_file = get_strparam(args.qrcode_file) if args.qrcode_file else None
    if qrcode_file:
        result = register_secret(qr_code_file=args.qrcode_file,
                                 new_name=args.new_name,
                                 secrets_file=secrets_file)
    else:
        result_dic = register_secret_manually(name=args.new_name,
                                              secret=args.secret_string,
                                              issuer=args.issuer,
                                              account=args.account,
                                              secrets_file=secrets_file)
    for sec in result:
        print(f"Registered secret name: '{sec['name']}' - Account: {sec['account']}, Issuer: {sec['issuer']}")

# ----------------------------------------------------------------------------
def handle_get(args):
    """
    Handle the 'get' command to generate a TOTP token for a given secret name.

    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """
    secrets_file = get_strparam(args.secrets_file) if args.secrets_file else None
    token = gen_token(name=args.name,
                      secrets_file=secrets_file)
    if token:
        print(token)

# ----------------------------------------------------------------------------
def handle_list(args):
    """
    Handle the 'list' command to display all registered secrets.

    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """
    secrets_file = get_strparam(args.secrets_file) if args.secrets_file else None
    secrets = get_secret_list(secrets_file=secrets_file)
    if not secrets:
        print("No secrets found.")
    else:
        for sec in secrets:
            print(f"Secret name: '{sec['name']}' - Account: {sec['account']}, Issuer: {sec['issuer']}")

# ----------------------------------------------------------------------------
def handle_remove(args):
    """
    Handle the 'remove' command to delete a secret by its name.

    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """
    result = []
    secrets_file = get_strparam(args.secrets_file) if args.secrets_file else None
    names = [args.name]
    result = remove_secrets(names=names,
                            secrets_file=secrets_file)
    if result:
        print(f"Secret '{args.name}' removed successfully.")
    else:
        print(f"Secret '{args.name}' not found.")

# ----------------------------------------------------------------------------
def handle_rename(args):
    """
    Handle the 'rename' command to rename an existing secret.

    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """
    secrets_file = get_strparam(args.secrets_file) if args.secrets_file else None
    result = rename_secret(name=args.name,
                           new_name=args.new_name,
                           secrets_file=secrets_file)
    if result:
        print(f"Secret '{args.name}' renamed to '{args.new_name}' successfully.")
    else:
        print(f"Secret '{args.name}' not found or rename failed.")

# ----------------------------------------------------------------------------
def handle_mcp(args):
    """
    Handle the 'mcp' command to run the MCP server.

    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """

    run_mcp = args.mcp_server if args.mcp_server else False
    if run_mcp:
        # If the MCP server flag is set, run the MCP server
        run_as_mcp_server()
    else:
        # Otherwise, run the MCP server test
        disp_tools()

# ---------------------------------------------------------------------------------------
def main():
    argp = ArgumentParser(prog="mktotp",
                          description="Mangage TOTP secrets stored in a JSON file.")
    # Register common arguments
    common = ArgumentParser(add_help=False)
    common.add_argument(
        '-v',
        '--verbose',
        type=int,
        default=0,
        choices=[0, 1, 2],
        metavar='LEVEL',
        help='Set the verbosity level (0: normal, 1: verbose, 2: debug).'
    )
    common.add_argument(
        '-s',
        '--secrets-file',
        type=str,
        default=None,
        help='Path to the JSON file where secrets are stored.'
    )

    subparsers = argp.add_subparsers(dest='command',
                                     help='Available commands')
    # Register subcommands
    register_sub_add(subparsers, handle_add, parent_parser=common)
    register_sub_get(subparsers, handle_get, parent_parser=common)
    register_sub_list(subparsers, handle_list, parent_parser=common)
    register_sub_remove(subparsers, handle_remove, parent_parser=common)
    register_sub_rename(subparsers, handle_rename, parent_parser=common)
    register_sub_mcp(subparsers, handle_mcp, parent_parser=common)


    try:
        # Parse the command line arguments
        args = argp.parse_args()
        # If no command is specified, show help
        if args.command is None:
            argp.print_help()
        else:
            # Initialize the logger with the specified verbosity level
            _ = get_logger(verbose_level=args.verbose)
            # Execute the handler for the specified command
            if hasattr(args, 'handler'):
                args.handler(args)
            else:
                argp.print_help()

    except FileNotFoundError:
        print("Error: Secrets file not found. Please ensure the file exists or specify a valid path.", file=sys.stderr)
    except PermissionError:
        print("Error: Permission denied when accessing the secrets file. Check your permissions.", file=sys.stderr)
    except KeyError as e:
        print(f"Error: Token '{e}' not found in the secrets file. Please check the token name.", file=sys.stderr)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Exception: {e}", file=sys.stderr)

# ---------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
