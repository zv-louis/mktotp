# mktotp

A simple CUI-based TOTP secret management tool and local MCP server for multi-factor authentication (MFA)

English | [日本語](README_ja.md)

<!-- TOC tocDepth:2..3 chapterDepth:2..6 -->

- [mktotp](#mktotp)
  - [1. Overview](#1-overview)
  - [2. Features](#2-features)
  - [3. Runtime Environment](#3-runtime-environment)
  - [4. Installation/Usage](#4-installationusage)
    - [4-1. Install as a uv tool](#4-1-install-as-a-uv-tool)
      - [4-1-1. Installation](#4-1-1-installation)
    - [4-2. Using uvx](#4-2-using-uvx)
      - [4-2-1. Running with the uvx command](#4-2-1-running-with-the-uvx-command)
      - [4-2-2. Registering as an MCP server](#4-2-2-registering-as-an-mcp-server)
    - [4-3. Registering as an MCP server via the Claude plugin](#4-3-registering-as-an-mcp-server-via-the-claude-plugin)
  - [5. CUI Tool Command Options](#5-cui-tool-command-options)
    - [5-1. Common Options](#5-1-common-options)
    - [5-2. `add` Command](#5-2-add-command)
      - [5-2-1. Adding from a QR code image file](#5-2-1-adding-from-a-qr-code-image-file)
      - [5-2-2. Registering a TOTP secret directly (CUI tool only)](#5-2-2-registering-a-totp-secret-directly-cui-tool-only)
    - [5-3. `get` Command](#5-3-get-command)
    - [5-4. `list` Command](#5-4-list-command)
    - [5-5. `remove` Command](#5-5-remove-command)
    - [5-6. `rename` Command](#5-6-rename-command)
    - [5-7. `mcp` Command](#5-7-mcp-command)
  - [6. File Storage Location](#6-file-storage-location)
  - [7. Security Notes](#7-security-notes)
  - [8. License](#8-license)

<!-- /TOC -->

## 1. Overview

mktotp is a command-line tool for managing TOTP (Time-based One-Time Password) secrets and generating authentication tokens for multi-factor authentication services.  
It also works as a local MCP server, so you can operate it from MCP-compatible Agent tools.

## 2. Features

- Register TOTP secrets from QR code image files in PNG, JPEG, BMP, TIFF, or SVG format
- Generate TOTP tokens for registered secrets
- List all registered secrets
- Remove and rename secrets
- Can be operated from MCP-compatible Agent tools when running as a local MCP server  
  While running as an MCP server, mktotp is designed so that secret strings are not sent to the LLM.

## 3. Runtime Environment

This project uses uv as the package manager.  

For how to install uv, see the following page.

- [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)

## 4. Installation/Usage

### 4-1. Install as a uv tool

Install mktotp into a uv environment and use it.  
Use this method when you use mktotp as a CLI tool.  

#### 4-1-1. Installation

```bash
# Install from PyPI
uv tool install mktotp
```

After installation, you can run the `mktotp` command directly.  

```bash
mktotp --help
```

### 4-2. Using uvx

Run mktotp directly from PyPI with uvx, without installing it.

#### 4-2-1. Running with the uvx command

Start mktotp with the uvx command.

```bash
uvx mktotp --help
# Add @latest to always use the latest version
uvx mktotp@latest --help
```

#### 4-2-2. Registering as an MCP server

By registering mktotp as an MCP server, you can also operate `mktotp` from Agent tools.  
For how to register an MCP server, refer to the manual of the Agent tool you use.  

```jsonc
{
  // Example configuration for registering as an MCP server
  //
  // (Note)
  // Registration keys differ depending on the Agent tool.
  "mcpServers": {
    // Configuration for starting mktotp as an MCP server using uvx
    "mktotp-uv": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "mktotp@latest",
        "mcp",
        "--mcp-server"
      ],
      "env": {}
    }
  }
}
```

### 4-3. Registering as an MCP server via the Claude plugin

mktotp can be installed as a Claude plugin.  

```bash
# Add the marketplace
/plugin marketplace add zv-louis/zv-plugin-marketplace
# Install from the marketplace
/plugin install mktotp-mcp@zv-plugins
```

## 5. CUI Tool Command Options

### 5-1. Common Options

- `-v, --verbose LEVEL`: Set the output verbosity (0: normal, 1: verbose, 2: debug)
- `-s, --secrets-file FILE`: Path to the JSON file where secrets are stored

### 5-2. `add` Command

Add a new secret.  
Specify either `-f` (QR code image) or `-ss` (secret string).  
If neither is given, the command fails with an error.  
If both are given, `-f` takes precedence and `-ss` is ignored.  

- `-nn, --new-name`: Name for the secret (required)

If a secret with the same name is already registered, it is overwritten.  

#### 5-2-1. Adding from a QR code image file

Add a new secret from a QR code image.  

```bash
mktotp add -nn <new_name> -f <QR_code_image_file>
```

- `-f, --qrcode-file`: Path to the image file containing the QR code  
  PNG, JPEG, BMP, TIFF, and SVG are supported (for TIFF, only the `.tiff` extension is accepted)

The account and issuer are taken from the QR code.  
If the image contains multiple QR codes, all of them are registered.  
The second and later secrets get a `_2`, `_3` ... suffix (e.g. `<new_name>_2`).  

#### 5-2-2. Registering a TOTP secret directly (CUI tool only)

Add a new secret by specifying the secret string directly.  

```bash
mktotp add -nn <new_name> -ss <secret_string> [-i <issuer>] [-a <account>]
```

- `-ss, --secret-string`: Secret string in Base32 format
- `-i, --issuer`: Issuer. Defaults to the secret name
- `-a, --account`: Account. Defaults to the secret name

Whitespace in the secret string (such as groups of 4 characters) and trailing `=` padding are removed before saving.  
An invalid Base32 string results in an error.  
The error message shows only the positions of the invalid characters, counted from the start of the input (whitespace included). It never shows the secret itself.  

> The string given with `-ss` may remain in your shell history and the process list.

### 5-3. `get` Command

Generate a TOTP token for the specified secret name.

```bash
mktotp get -n <secret_name>
```

- `-n, --name`: Name of the secret to operate on (required)

### 5-4. `list` Command

Display all registered secrets.

```bash
mktotp list
```

### 5-5. `remove` Command

Remove the specified secret.

```bash
mktotp remove -n <secret_name>
```

- `-n, --name`: Name of the secret to remove (required)

### 5-6. `rename` Command

Rename a registered secret.

```bash
mktotp rename -n <current_name> -nn <new_name>
```

- `-n, --name`: Current secret name (required)
- `-nn, --new-name`: New secret name (required)

### 5-7. `mcp` Command

Start mktotp as a local MCP server.  
You can operate mktotp from Agent tools.

```bash
mktotp mcp --mcp-server
```

If the `--mcp-server` option is not specified, it outputs the MCP tool list.

```bash
mktotp mcp
```

## 6. File Storage Location

By default, secrets are stored in the following location.

```text
~/.mktotp/data/secrets.json
```

You can specify a different location with the `-s` option.

## 7. Security Notes

- Secret files contain sensitive information, so protect them with permissions that prevent anyone but the owner from reading or writing them. When saving, mktotp automatically sets permissions that allow only the owner to read and write (600 on Unix-like systems).  
- When creating backups, we recommend using encrypted storage.  
- Remove unnecessary secrets with the `remove` command.

## 8. License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.
