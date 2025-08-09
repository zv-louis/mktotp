# mktotp

A Simple CUI TOTP token generator for use with 2FA services.

English | [日本語](README_ja.md)

<!-- TOC tocDepth:2..3 chapterDepth:2..6 -->

- [mktotp](#mktotp)
  - [Description](#description)
  - [Features](#features)
  - [Installation](#installation)
    - [Using uv (Recommended)](#using-uv-recommended)
    - [Using traditional Python setup](#using-traditional-python-setup)
  - [Building Package](#building-package)
  - [Usage](#usage)
    - [Using uv](#using-uv)
    - [After pip installation](#after-pip-installation)
  - [Command Options](#command-options)
    - [Common Options](#common-options)
    - [add Command](#add-command)
    - [get Command](#get-command)
    - [list Command](#list-command)
    - [remove Command](#remove-command)
    - [rename Command](#rename-command)
  - [File Storage Location](#file-storage-location)
  - [Security Notes](#security-notes)
  - [License](#license)

<!-- /TOC -->

## Description

mktotp is a command-line tool for managing TOTP (Time-based One-Time Password) secrets and generating authentication tokens for two-factor authentication services.

## Features

- Add TOTP secrets from QR code images
- Generate TOTP tokens for registered secrets
- List all registered secrets
- Remove and rename secrets

## Installation

### Using uv (Recommended)

This project uses uv.  
Using uv allows you to automatically reproduce the execution environment.  

For uv installation, see here:  

- [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# Assuming the project is cloned in the mktotp directory
cd mktotp
# Install dependencies and run. Display help
uv run -m mktotp --help
```

### Using traditional Python setup

```bash
# Assuming the project is cloned in the mktotp directory
cd mktotp
# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
# Display help
python -m mktotp --help
```

## Building Package

To create a module package, run the following command:

```bash
# Assuming the project is cloned in the mktotp directory
cd mktotp 
# Create package
uv build
```

## Usage

Secrets are managed with arbitrary names (secret names).  

### Using uv

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

### After pip installation

If you used pip installation:

```bash
# After pip install
python -m mktotp add -nn "secret_name" -f "path/to/QR_code_image_file"
python -m mktotp get -n "secret_name"
python -m mktotp list
python -m mktotp remove -n "secret_name"
python -m mktotp rename -n "current_secret_name" -nn "new_secret_name"
```

## Command Options

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
