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
    - [4-2. Using uvx](#4-2-using-uvx)
  - [5. Using as an MCP Server](#5-using-as-an-mcp-server)
    - [5-1. Registering the installed mktotp as a server](#5-1-registering-the-installed-mktotp-as-a-server)
    - [5-2. Registering as an MCP server via the Claude plugin](#5-2-registering-as-an-mcp-server-via-the-claude-plugin)
  - [6. CUI Tool Command Options](#6-cui-tool-command-options)
    - [6-1. Common Options](#6-1-common-options)
    - [6-2. `add` Command](#6-2-add-command)
      - [6-2-1. Adding from a QR code image file](#6-2-1-adding-from-a-qr-code-image-file)
      - [6-2-2. Registering a TOTP secret directly (CUI tool only)](#6-2-2-registering-a-totp-secret-directly-cui-tool-only)
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

mktotp is a command-line tool for managing TOTP (Time-based One-Time Password) secrets and generating authentication tokens for multi-factor authentication services.  
It also works as a local MCP server, so you can operate it from MCP-compatible Agent tools.

## 2. Features

- Register TOTP secrets from QR code image files in PNG, JPEG, BMP, TIFF, WebP, GIF, or SVG format
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
Start mktotp with the uvx command.

```bash
uvx mktotp --help
# Add @latest to always use the latest version
uvx mktotp@latest --help
```

## 5. Using as an MCP Server

By registering mktotp as an MCP server, you can also operate `mktotp` from Agent tools.  
For how to register an MCP server, refer to the manual of the Agent tool you use.  

### 5-1. Registering the installed mktotp as a server

To register the installed `mktotp` as an MCP server, register a configuration that starts it with the `mcp --mcp-server` options in your Agent tool.  
To start it with uvx without installing, use `uvx mktotp@latest`.  

```jsonc
{
  // Example configuration for registering as an MCP server
  //
  // (Note)
  // Registration keys differ depending on the Agent tool.
  "mcpServers": {
    // Configuration for starting the installed mktotp as an MCP server
    "mktotp": {
      "type": "stdio",
      "command": "mktotp",
      "args": [
        "mcp",
        "--mcp-server"
      ],
      "env": {}
    },
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

### 5-2. Registering as an MCP server via the Claude plugin

mktotp can be installed as a Claude plugin.  

```bash
# Add the marketplace
/plugin marketplace add zv-louis/zv-plugin-marketplace
# Install from the marketplace
/plugin install mktotp-mcp@zv-plugins
```

## 6. CUI Tool Command Options

### 6-1. Common Options

- `-v, --verbose LEVEL`: Set the output verbosity (0: normal, 1: verbose, 2: debug)
- `-s, --secrets-file FILE`: Path to the JSON file where secrets are stored

### 6-2. `add` Command

Add a new secret.  
Specify either `-f` (QR code image) or `-ss` (secret string).  
If neither is given, the command fails with an error.  
If both are given, `-f` takes precedence and `-ss` is ignored.  

- `-nn, --new-name`: Name for the secret (required)

If a secret with the same name is already registered, it is overwritten.  

#### 6-2-1. Adding from a QR code image file

Add a new secret from a QR code image.  

```bash
mktotp add -nn <new_name> -f <QR_code_image_file>
```

- `-f, --qrcode-file`: Path to the image file containing the QR code  
  Supported formats and extensions (case-insensitive):

  | Format | Extensions |
  | --- | --- |
  | PNG | `.png` |
  | JPEG | `.jpg`, `.jpeg` |
  | BMP | `.bmp` |
  | TIFF | `.tiff`, `.tif` |
  | WebP | `.webp` |
  | GIF | `.gif` |
  | SVG | `.svg` |

The account and issuer are taken from the QR code.  
If the image contains multiple QR codes, all of them are registered.  
The second and later secrets get a `_2`, `_3` ... suffix (e.g. `<new_name>_2`).  

#### 6-2-2. Registering a TOTP secret directly (CUI tool only)

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

Rename a registered secret.

```bash
mktotp rename -n <current_name> -nn <new_name>
```

- `-n, --name`: Current secret name (required)
- `-nn, --new-name`: New secret name (required)

### 6-7. `mcp` Command

Start mktotp as a local MCP server.  
You can operate mktotp from Agent tools.

```bash
mktotp mcp --mcp-server
```

If the `--mcp-server` option is not specified, it outputs the MCP tool list.

```bash
mktotp mcp
```

## 7. File Storage Location

By default, secrets are stored in the following location.

```text
~/.mktotp/data/secrets.json
```

You can specify a different location with the `-s` option.

## 8. Security Notes

- Secret files contain sensitive information, so protect them with permissions that prevent anyone but the owner from reading or writing them. When saving, mktotp automatically sets permissions that allow only the owner to read and write (600 on Unix-like systems).  
- When creating backups, we recommend using encrypted storage.  
- Remove unnecessary secrets with the `remove` command.

## 9. License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.
