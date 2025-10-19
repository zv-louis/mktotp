# mktotp

A simple CUI-based TOTP secret management tool and local MCP server for multi-factor authentication (2FA)

English | [日本語](README_ja.md)

<!-- TOC tocDepth:2..3 chapterDepth:2..6 -->

- [1. Overview](#1-overview)
- [2. Features](#2-features)
- [3. Runtime Environment](#3-runtime-environment)
- [4. Installation/Usage](#4-installationusage)
- [5. Registering as MCP Server](#5-registering-as-mcp-server)
- [6. CUI Tool Command Options](#6-cui-tool-command-options)
  - [6-1. Common Options](#6-1-common-options)
  - [6-2. `add` Command](#6-2-add-command)
  - [6-3. `get` Command](#6-3-get-command)
  - [6-4. `list` Command](#6-4-list-command)
  - [6-5. `remove` Command](#6-5-remove-command)
  - [6-6. `rename` Command](#6-6-rename-command)
  - [6-7. `mcp` Command](#6-7-mcp-command)
- [7. File Storage Location](#7-file-storage-location)
- [8. Security Notes](#8-security-notes)
- [9. License](#9-license)

<!-- /TOC -->

## 1. Overview

mktotp is a command-line tool for managing TOTP (Time-based One-Time Password) secrets and generating authentication tokens for two-factor authentication services.  
It also functions as a local MCP server, allowing operation through common Agent tools.

## 2. Features

- Register TOTP secrets from QR code image files  
  (QR code images support PNG, JPEG, BMP, TIFF, and SVG formats)
- Generate TOTP tokens for registered secrets
- List all registered secrets
- Remove and rename secrets
- Can be operated from general Agent tools when running as a local MCP server.  
  (Of course, mktotp is taking care that secret strings are not sent to the LLM)

## 3. Runtime Environment

This project uses uv as the package manager.  

For uv installation, see here:

- [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)

## 4. Installation/Usage

Install and use in a uv environment.

```bash
# Install directly from git repository
uv tool install git+{mktotp_repository_URL}
```

After installation, you can use the `mktotp` command directly as a tool.

```bash
mktotp --help
```

## 5. Registering as MCP Server

By registering as an MCP server, you can operate mktotp from common Agent tools.  
Please refer to the manual of the Agent tool you are using for the procedure to register an MCP server.

```json
{
  // Example configuration for registering as MCP server
  //
  // (Note) 
  // Registration keys may differ depending on the Agent tool.
  // Please refer to the manual of the Agent tool you are using for detailed procedures.
  "mcpServers" {
    // Configuration for starting mktotp as MCP server using uv
    "mktotp-uv": {
      "type": "stdio",
      "command": "mktotp",
      "args": [
          "mcp",
          "--mcp-server"
      ],
      "env": {},
    }
  }
}
```

## 6. CUI Tool Command Options

### 6-1. Common Options

- `-v, --verbose LEVEL`: Set output information detail level (0: normal, 1: verbose, 2: debug)
- `-s, --secrets-file FILE`: Path to the JSON file where secrets are stored

### 6-2. `add` Command

#### 6-2-1. Adding from QR code image file

Add a new secret from QR code image.

```bash
mktotp add -nn <new_name> -f <QR_code_image_file>
```

- `-nn, --new-name`: New name for the secret (required)
- `-f, --file`: Path to the file containing QR code data (required)

#### 6-2-2. Registering TOTP secret directly (CUI tool only)

Add a new secret by directly specifying the secret string.

```bash
mktotp add -nn <new_name> -ss <secret_string>
```

### 6-3. `get` Command

Generate a TOTP token for the specified secret name.

```bash
mktotp get -n <secret_name>
```

- `-n, --name`: Name of the secret to operate on (required)

### 6-4. `list` Command

Display all registered secrets.

```bash
mktotp list
```

### 6-5. `remove` Command

Remove the specified secret.

```bash
mktotp remove -n <secret_name>
```

- `-n, --name`: Name of the secret to remove (required)

### 6-6. `rename` Command

Rename a registerd secret.

```bash
mktotp rename -n <current_name> -nn <new_name>
```

- `-n, --name`: Current secret name (required)
- `-nn, --new-name`: New secret name (required)

### 6-7. `mcp` Command

Start the module as a local MCP server.  
You can operate mktotp using Agent tools.

```bash
mktotp mcp --mcp-server
```

If the `--mcp-server` option is not specified, it will output the MCP tool list.

```bash
mktotp mcp
```

## 7. File Storage Location

By default, secrets are stored in the following location:

```text
~/.mktotp/data/secrets.json
```

You can specify a different location with the `-s` option.

## 8. Security Notes

- Secret files contain sensitive information, so protect them with appropriate permission settings.  
- When creating backups, we recommend using encrypted storage.  
- Remove unnecessary secrets with the `remove` command.

## 9. License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.
