# encoding: utf-8-sig

import argparse
import pytest
from unittest.mock import MagicMock

from mktotp.cmdparam import (
    register_sub_add,
    register_sub_get,
    register_sub_list,
    register_sub_remove,
    register_sub_rename,
    register_sub_mcp
)


class TestCmdParam:
    """Test class for command parameter functions"""

    @pytest.fixture
    def mock_handler(self):
        """Create a mock handler function"""
        return MagicMock()

    @pytest.fixture
    def parent_parser(self):
        """Create a parent parser for testing"""
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-v', '--verbose', type=int, default=0)
        parser.add_argument('-s', '--secrets-file', type=str, default=None)
        return parser

    @pytest.fixture
    def main_parser(self, parent_parser):
        """Create a main parser with subparsers"""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        return parser, subparsers

    def test_register_sub_add(self, main_parser, mock_handler, parent_parser):
        """Test register_sub_add function"""
        parser, subparsers = main_parser
        
        register_sub_add(subparsers, mock_handler, parent_parser)
        
        # Test that 'add' subcommand was registered
        args = parser.parse_args(['add', '-nn', 'test_name', '-f', 'test_file.png'])
        
        assert args.command == 'add'
        assert args.new_name == 'test_name'
        assert args.file == 'test_file.png'
        assert hasattr(args, 'handler')
        assert args.handler == mock_handler

    def test_register_sub_add_missing_required_args(self, main_parser, mock_handler, parent_parser):
        """Test register_sub_add with missing required arguments"""
        parser, subparsers = main_parser
        
        register_sub_add(subparsers, mock_handler, parent_parser)
        
        # Test missing new_name
        with pytest.raises(SystemExit):
            parser.parse_args(['add', '-f', 'test_file.png'])
        
        # Test missing file
        with pytest.raises(SystemExit):
            parser.parse_args(['add', '-nn', 'test_name'])

    def test_register_sub_get(self, main_parser, mock_handler, parent_parser):
        """Test register_sub_get function"""
        parser, subparsers = main_parser
        
        register_sub_get(subparsers, mock_handler, parent_parser)
        
        # Test that 'get' subcommand was registered
        args = parser.parse_args(['get', '-n', 'test_secret'])
        
        assert args.command == 'get'
        assert args.name == 'test_secret'
        assert hasattr(args, 'handler')
        assert args.handler == mock_handler

    def test_register_sub_get_missing_required_arg(self, main_parser, mock_handler, parent_parser):
        """Test register_sub_get with missing required argument"""
        parser, subparsers = main_parser
        
        register_sub_get(subparsers, mock_handler, parent_parser)
        
        # Test missing name
        with pytest.raises(SystemExit):
            parser.parse_args(['get'])

    def test_register_sub_list(self, main_parser, mock_handler, parent_parser):
        """Test register_sub_list function"""
        parser, subparsers = main_parser
        
        register_sub_list(subparsers, mock_handler, parent_parser)
        
        # Test that 'list' subcommand was registered
        args = parser.parse_args(['list'])
        
        assert args.command == 'list'
        assert hasattr(args, 'handler')
        assert args.handler == mock_handler

    def test_register_sub_remove(self, main_parser, mock_handler, parent_parser):
        """Test register_sub_remove function"""
        parser, subparsers = main_parser
        
        register_sub_remove(subparsers, mock_handler, parent_parser)
        
        # Test that 'remove' subcommand was registered
        args = parser.parse_args(['remove', '-n', 'secret_to_remove'])
        
        assert args.command == 'remove'
        assert args.name == 'secret_to_remove'
        assert hasattr(args, 'handler')
        assert args.handler == mock_handler

    def test_register_sub_remove_missing_required_arg(self, main_parser, mock_handler, parent_parser):
        """Test register_sub_remove with missing required argument"""
        parser, subparsers = main_parser
        
        register_sub_remove(subparsers, mock_handler, parent_parser)
        
        # Test missing name
        with pytest.raises(SystemExit):
            parser.parse_args(['remove'])

    def test_register_sub_rename(self, main_parser, mock_handler, parent_parser):
        """Test register_sub_rename function"""
        parser, subparsers = main_parser
        
        register_sub_rename(subparsers, mock_handler, parent_parser)
        
        # Test that 'rename' subcommand was registered
        args = parser.parse_args(['rename', '-n', 'old_name', '-nn', 'new_name'])
        
        assert args.command == 'rename'
        assert args.name == 'old_name'
        assert args.new_name == 'new_name'
        assert hasattr(args, 'handler')
        assert args.handler == mock_handler

    def test_register_sub_rename_missing_required_args(self, main_parser, mock_handler, parent_parser):
        """Test register_sub_rename with missing required arguments"""
        parser, subparsers = main_parser
        
        register_sub_rename(subparsers, mock_handler, parent_parser)
        
        # Test missing name
        with pytest.raises(SystemExit):
            parser.parse_args(['rename', '-nn', 'new_name'])
        
        # Test missing new_name
        with pytest.raises(SystemExit):
            parser.parse_args(['rename', '-n', 'old_name'])

    def test_register_sub_mcp(self, main_parser, mock_handler, parent_parser):
        """Test register_sub_mcp function"""
        parser, subparsers = main_parser
        
        register_sub_mcp(subparsers, mock_handler, parent_parser)
        
        # Test that 'mcp' subcommand was registered
        args = parser.parse_args(['mcp'])
        
        assert args.command == 'mcp'
        assert hasattr(args, 'handler')
        assert args.handler == mock_handler
        assert args.mcp_server is False  # Default value

    def test_register_sub_mcp_with_server_flag(self, main_parser, mock_handler, parent_parser):
        """Test register_sub_mcp with server flag"""
        parser, subparsers = main_parser
        
        register_sub_mcp(subparsers, mock_handler, parent_parser)
        
        # Test with server flag
        args = parser.parse_args(['mcp', '--mcp-server'])
        
        assert args.command == 'mcp'
        assert args.mcp_server is True

    def test_parent_parser_inheritance(self, main_parser, mock_handler, parent_parser):
        """Test that parent parser arguments are inherited"""
        parser, subparsers = main_parser
        
        register_sub_add(subparsers, mock_handler, parent_parser)
        
        # Test that parent arguments are available
        args = parser.parse_args(['add', '-nn', 'test', '-f', 'test.png', '-v', '2', '-s', 'custom.json'])
        
        assert args.verbose == 2
        assert args.secrets_file == 'custom.json'

    def test_all_subcommands_registration(self, main_parser, mock_handler, parent_parser):
        """Test registering all subcommands together"""
        parser, subparsers = main_parser
        
        # Register all subcommands
        register_sub_add(subparsers, mock_handler, parent_parser)
        register_sub_get(subparsers, mock_handler, parent_parser)
        register_sub_list(subparsers, mock_handler, parent_parser)
        register_sub_remove(subparsers, mock_handler, parent_parser)
        register_sub_rename(subparsers, mock_handler, parent_parser)
        register_sub_mcp(subparsers, mock_handler, parent_parser)
        
        # Test each command
        test_cases = [
            (['add', '-nn', 'test', '-f', 'test.png'], 'add'),
            (['get', '-n', 'test'], 'get'),
            (['list'], 'list'),
            (['remove', '-n', 'test'], 'remove'),
            (['rename', '-n', 'old', '-nn', 'new'], 'rename'),
            (['mcp'], 'mcp'),
        ]
        
        for cmd_args, expected_command in test_cases:
            args = parser.parse_args(cmd_args)
            assert args.command == expected_command
            assert hasattr(args, 'handler')
            assert args.handler == mock_handler

    def test_argument_descriptions_and_help(self, main_parser, mock_handler, parent_parser):
        """Test that arguments have proper descriptions and help"""
        parser, subparsers = main_parser
        
        register_sub_add(subparsers, mock_handler, parent_parser)
        
        # Get the add subparser
        add_parser = None
        for action in parser._subparsers._actions:
            if isinstance(action, argparse._SubParsersAction):
                add_parser = action.choices.get('add')
                break
        
        assert add_parser is not None
        
        # Check that arguments have help text
        for action in add_parser._actions:
            if action.dest in ['new_name', 'file']:
                assert action.help is not None
                assert len(action.help) > 0

    def test_argument_metavar_and_types(self, main_parser, mock_handler, parent_parser):
        """Test that arguments have proper metavar and types"""
        parser, subparsers = main_parser
        
        register_sub_add(subparsers, mock_handler, parent_parser)
        
        # Test with various argument formats
        args = parser.parse_args(['add', '--new-name', 'test_secret', '--file', 'qr_code.png'])
        
        assert args.new_name == 'test_secret'
        assert args.file == 'qr_code.png'

    def test_short_and_long_argument_forms(self, main_parser, mock_handler, parent_parser):
        """Test that both short and long argument forms work"""
        parser, subparsers = main_parser
        
        register_sub_add(subparsers, mock_handler, parent_parser)
        register_sub_get(subparsers, mock_handler, parent_parser)
        register_sub_remove(subparsers, mock_handler, parent_parser)
        register_sub_rename(subparsers, mock_handler, parent_parser)
        
        # Test short forms
        args1 = parser.parse_args(['add', '-nn', 'test', '-f', 'test.png'])
        assert args1.new_name == 'test'
        assert args1.file == 'test.png'
        
        # Test long forms
        args2 = parser.parse_args(['add', '--new-name', 'test', '--file', 'test.png'])
        assert args2.new_name == 'test'
        assert args2.file == 'test.png'
        
        # Test mixed forms
        args3 = parser.parse_args(['rename', '-n', 'old', '--new-name', 'new'])
        assert args3.name == 'old'
        assert args3.new_name == 'new'

    def test_required_arguments_validation(self, main_parser, mock_handler, parent_parser):
        """Test that required arguments are properly validated"""
        parser, subparsers = main_parser
        
        register_sub_add(subparsers, mock_handler, parent_parser)
        register_sub_get(subparsers, mock_handler, parent_parser)
        register_sub_remove(subparsers, mock_handler, parent_parser)
        register_sub_rename(subparsers, mock_handler, parent_parser)
        
        # Test that SystemExit is raised for missing required arguments
        required_arg_tests = [
            (['add', '-nn', 'test'], "file is required for add"),
            (['add', '-f', 'test.png'], "new_name is required for add"),
            (['get'], "name is required for get"),
            (['remove'], "name is required for remove"),
            (['rename', '-n', 'old'], "new_name is required for rename"),
            (['rename', '-nn', 'new'], "name is required for rename"),
        ]
        
        for cmd_args, description in required_arg_tests:
            with pytest.raises(SystemExit):  # description:
                parser.parse_args(cmd_args)

    def test_mcp_server_flag_variations(self, main_parser, mock_handler, parent_parser):
        """Test MCP server flag variations"""
        parser, subparsers = main_parser
        
        register_sub_mcp(subparsers, mock_handler, parent_parser)
        
        # Test default (no flag)
        args1 = parser.parse_args(['mcp'])
        assert args1.mcp_server is False
        
        # Test with flag
        args2 = parser.parse_args(['mcp', '--mcp-server'])
        assert args2.mcp_server is True
