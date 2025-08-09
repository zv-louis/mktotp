# encoding: utf-8-sig

from argparse import ArgumentParser
from pathlib import Path

from .secrets import SecretMgr
from .qrcode_util import decode_qrcode
from .logutil import get_logger
from .cmdparam import *

# ----------------------------------------------------------------------------
def handle_add(args):
    """
    Handle the 'add' command to register a new secret from a QR code file.
    
    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """
    mgr = SecretMgr(args.secrets_file)
    mgr.load()  # Load existing secrets
    qrcode_datas = decode_qrcode(args.file)
    result = mgr.register_secret(args.new_name, qrcode_datas)
    mgr.save()
    # display the registered secrets
    for sec in result:
        print(f"Registered secret name: '{sec['name']}' - Account: {sec['account']}, Issuer: {sec['issuer']}")

# ----------------------------------------------------------------------------
def handle_get(args):
    """
    Handle the 'get' command to generate a TOTP token for a given secret name.

    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """
    mgr = SecretMgr(args.secrets_file)
    mgr.load()
    token = mgr.gen_totp_token(args.name)
    print(token)

# ----------------------------------------------------------------------------
def handle_list(args):
    """
    Handle the 'list' command to display all registered secrets.

    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """
    mgr = SecretMgr(args.secrets_file)
    mgr.load()
    secrets = mgr.list_secrets()
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
    mgr = SecretMgr(args.secrets_file)
    mgr.load()
    result = mgr.remove_secret(args.name)
    if result:
        mgr.save()
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
    mgr = SecretMgr(args.secrets_file)
    mgr.load()
    result = mgr.rename_secret(args.name, args.new_name)
    if result:
        mgr.save()
        print(f"Secret '{args.name}' renamed to '{args.new_name}' successfully.")
    else:
        print(f"Secret '{args.name}' not found or rename failed.")

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

    try:
        # Parse the command line arguments
        args = argp.parse_args()
        # Initialize the logger with the specified verbosity level
        _ = get_logger(verbose_level=args.verbose)

        # If no command is specified, show help
        if args.command is None:
            argp.print_help()
        else:
            # Execute the handler for the specified command
            if hasattr(args, 'handler'):
                args.handler(args)
            else:
                argp.print_help()

    except FileNotFoundError:
        print("Error: Secrets file not found. Please ensure the file exists or specify a valid path.")
    except PermissionError:
        print("Error: Permission denied when accessing the secrets file. Check your permissions.")
    except KeyError as e:
        print(f"Error: Token '{e}' not found in the secrets file. Please check the token name.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Exception: {e}")

# ---------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
