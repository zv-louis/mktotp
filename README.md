# mktotp

A simple CUI-based TOTP secret management tool and local MCP server for multi-factor authentication (2FA)

English | [日本語](README_ja.md)

<!-- TOC tocDepth:2..3 chapterDepth:2..6 -->

- [mktotp](#mktotp)
  - [Overview](#overview)
  - [Features](#features)
  - [Runtime Environment](#runtime-environment)
  - [Building Module Package](#building-module-package)
  - [Usage](#usage)
    - [Running module directly from project](#running-module-directly-from-project)
    - [Installing module package to Python environment](#installing-module-package-to-python-environment)
    - [Registering as MCP Server](#registering-as-mcp-server)
  - [CUI Tool Command Options](#cui-tool-command-options)
    - [Common Options](#common-options)
    - [add Command](#add-command)
    - [get Command](#get-command)
    - [list Command](#list-command)
    - [remove Command](#remove-command)
    - [rename Command](#rename-command)
    - [mcp Command](#mcp-command)
  - [File Storage Location](#file-storage-location)
  - [Security Notes](#security-notes)
  - [License](#license)

<!-- /TOC -->

## Overview

mktotp is a command-line tool for managing TOTP (Time-based One-Time Password) secrets and generating authentication tokens for two-factor authentication services.  
It also functions as a local MCP server, allowing operation through common Agent tools.

## Features

- Register TOTP secrets from QR code image files
- QR code images support PNG, JPEG, BMP, TIFF, and SVG formats
- Generate TOTP tokens for registered secrets
- List all registered secrets
- Remove and rename secrets
- Can be operated from common Agent tools when functioning as a local MCP server

## Runtime Environment

This project uses uv as the package manager.  
Using uv allows you to automatically reproduce the runtime environment.  

For uv installation, see here:

- [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# Assuming the project is cloned in the mktotp directory
cd mktotp
# Install dependencies and run. Display help
uv run -m mktotp --help
```

## Building Module Package

To create a module package, run the following uv command.  
The generated package will be saved in the dist directory.  
The generated package can be installed with pip, etc.

```bash
# Assuming the project is cloned in the mktotp directory
cd mktotp 
# Create package
uv build
```

## Usage

### Running module directly from project

You can run directly from the project directory using uv.  

When running from outside the project directory,
specify the project directory with the `--directory` option.

```bash
# Using uv (from project directory)
# Add a new secret from QR code image. (Existing ones will be overwritten)
uv run [--directory {project_dir}] -m mktotp add -nn "registered_secret_name" -f "path/to/QR-Code_image_file"

# Generate TOTP token
uv run [--directory {project_dir}] -m mktotp get -n "secret_name"

# List all secrets
uv run [--directory {project_dir}] -m mktotp list

# Remove a secret
uv run [--directory {project_dir}] -m mktotp remove -n "secret_name"

# Rename a secret
uv run [--directory {project_dir}] -m mktotp rename -n "current_secret_name" -nn "new_secret_name"
```

### Installing module package to Python environment

You can also install and use the built module package with the pip command.

```bash
# To install with pip, run the following command
# Install module package
pip install mktotp-<version>.tar.gz
# Or install wheel file
pip install mktotp-<version>-py3-none-any.whl

# To install with uv, run the following command
uv pip install mktotp-<version>.tar.gz
# Or install wheel file
uv pip install mktotp-<version>-py3-none-any.whl
```

After installation, you can run commands as follows:

```bash
# Add a new secret from QR code image
python -m mktotp add -nn "registered_secret_name" -f "path/to/QR-Code_image_file"
# Generate TOTP token
python -m mktotp get -n "secret_name"
# List all secrets
python -m mktotp list
# Remove a secret
python -m mktotp remove -n "secret_name"
# Rename a secret
python -m mktotp rename -n "current_secret_name" -nn "new_secret_name"
```

### Registering as MCP Server

By registering as an MCP server, you can operate mktotp from common Agent tools.

```json
{
  // Example configuration for registering as MCP server
  //
  // (Note) 
  // Registration keys may differ depending on the Agent tool used,
  // so please refer to the manual of each Agent tool you use for detailed procedures.
  "mcpServers" {
    // Configuration for starting mktotp as MCP server using uv
    "mktotp-uv": {
      "type": "stdio",
      "command": "uv",
      "args": [
          "run",
          "--directory",
          "${path_to_this_project}",
          "-m",
          "mktotp",
          "mcp",
          "--mcp-server"
      ],
      "env": {},
    },
    // Configuration for starting when module is installed in Python environment
    "mktotp-py": {
      "type": "stdio",
      "command": "python",
      "args": [
          "-m",
          "mktotp",
          "mcp",
          "--mcp-server"
      ],
      "env": {}
    }
  }
}
```

## CUI Tool Command Options

### Common Options

- `-v, --verbose LEVEL`: Set output information detail level (0: normal, 1: verbose, 2: debug)
- `-s, --secrets-file FILE`: Path to the JSON file where secrets are stored

### add Command

Add a new secret from QR code image.

```bash
uv run [--directory {project_dir}] -m mktotp add -nn <new_name> -f <QR_code_image_file>
```

- `-nn, --new-name`: New name for the secret (required)
- `-f, --file`: Path to the file containing QR code data (required)

### get Command

Generate a TOTP token for the specified secret name.

```bash
uv run [--directory {project_dir}] -m mktotp get -n <secret_name>
```

- `-n, --name`: Name of the secret to operate on (required)

### list Command

Display all registered secrets.

```bash
uv run [--directory {project_dir}] -m mktotp list
```

### remove Command

Remove the specified secret.

```bash
uv run [--directory {project_dir}] -m mktotp remove -n <secret_name>
```

- `-n, --name`: Name of the secret to remove (required)

### rename Command

Rename a secret.

```bash
uv run [--directory {project_dir}] -m mktotp rename -n <current_name> -nn <new_name>
```

- `-n, --name`: Current secret name (required)
- `-nn, --new-name`: New secret name (required)

### mcp Command

Start the module as a local MCP server.  
You can operate mktotp using Agent tools.

```bash
uv run [--directory {project_dir}] -m mktotp mcp --mcp-server
```

If the `--mcp-server` option is not specified, it will output the MCP tool list.

```bash
uv run [--directory {project_dir}] -m mktotp mcp
```

## File Storage Location

By default, secrets are stored in the following location:

```text
~/.mktotp/data/secrets.json
```

You can specify a different location with the `-s` option.

## Security Notes

- Secret files contain sensitive information, so protect them with appropriate permission settings.
- When creating backups, we recommend using encrypted storage.
- Remove unnecessary secrets with the `remove` command.

## License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.
