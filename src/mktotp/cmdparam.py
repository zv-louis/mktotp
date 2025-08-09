# encoding: utf-8-sig

import argparse

# ----------------------------------------------------------------------------
def register_sub_add(subparsers,
                     handle_add: callable,
                     parent_parser: argparse.ArgumentParser):
    """
    Register the 'add' subcommand to the argument parser.

    Args:
        arg_parser (argparse.ArgumentParser): The argument parser to register the subcommand with.
    """
    add_parser = subparsers.add_parser(
        'add',
        help='Add a new secret',
        description='Add a new secret.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[parent_parser]
    )
    add_parser.add_argument(
        '-nn',
        '--new-name',
        type=str,
        required=True,
        help='New name for the secret.'
    )
    add_parser.add_argument(
        '-f',
        '--file',
        type=str,
        required=True,
        help='Path to the file containing the QR code data.'
    )
    add_parser.set_defaults(handler=handle_add)
    return subparsers

# ----------------------------------------------------------------------------
def register_sub_get(subparsers,
                     handle_get: callable,
                     parent_parser: argparse.ArgumentParser):
        """
        Register the 'get' subcommand to the argument parser.
        Args:
            arg_parser (argparse.ArgumentParser): The argument parser to register the subcommand with.
        """
        get_parser = subparsers.add_parser(
            'get',
            help='Get a token for a secret',
            description='Get a token for a secret.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            parents=[parent_parser]
        )
        get_parser.add_argument(
            '-n',
            '--name',
            type=str,
            required=True,
            help='Name of the secret to operate on.'
        )
        get_parser.set_defaults(handler=handle_get)
        return subparsers

# ----------------------------------------------------------------------------
def register_sub_list(subparsers,
                      handle_list: callable,
                      parent_parser: argparse.ArgumentParser):
    """
    Register the 'list' subcommand to the argument parser.

    Args:
        arg_parser (argparse.ArgumentParser): The argument parser to register the subcommand with.
    """
    list_parser = subparsers.add_parser(
        'list',
        help='List all registered secrets',
        description='List all registered secrets.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[parent_parser]
    )
    # Set the function to handle the 'list' command
    list_parser.set_defaults(handler=handle_list)
    return subparsers

# ----------------------------------------------------------------------------
def register_sub_remove(subparsers,
                        handle_remove: callable,
                        parent_parser: argparse.ArgumentParser):
    """
    Register the 'remove' subcommand to the argument parser.

    Args:
        arg_parser (argparse.ArgumentParser): The argument parser to register the subcommand with.
    """
    remove_parser = subparsers.add_parser(
        'remove',
        help='Remove a secret',
        description='Remove a secret.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[parent_parser]
    )
    remove_parser.add_argument(
        '-n',
        '--name',
        type=str,
        required=True,
        help='Name of the secret to operate on.'
    )
    # Set the function to handle the 'remove' command
    remove_parser.set_defaults(handler=handle_remove)
    return subparsers

# ----------------------------------------------------------------------------
def register_sub_rename(subparsers,
                        handle_rename: callable,
                        parent_parser: argparse.ArgumentParser):
    """
    Register the 'rename' subcommand to the argument parser.

    Args:
        arg_parser (argparse.ArgumentParser): The argument parser to register the subcommand with.
    """
    rename_parser = subparsers.add_parser(
        'rename',
        help='Rename a secret name',
        description='Rename a secret name.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[parent_parser]
    )
    rename_parser.add_argument(
        '-nn',
        '--new-name',
        type=str,
        required=True,
        help='New name for the secret.'
    )
    rename_parser.add_argument(
        '-n',
        '--name',
        type=str,
        required=True,
        help='Name of the secret to operate on.'
    )
    # Set the function to handle the 'rename' command
    rename_parser.set_defaults(handler=handle_rename)
    return subparsers
