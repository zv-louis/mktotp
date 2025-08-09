# mktotp

多要素認証(2FA)サービス用のシンプルなCUIベースのTOTPトークンジェネレーター

[English](README.md) | 日本語

<!-- TOC tocDepth:2..3 chapterDepth:2..6 -->

- [mktotp](#mktotp)
  - [概要](#概要)
  - [機能](#機能)
  - [インストール](#インストール)
    - [uv を使用する方法（推奨）](#uv-を使用する方法推奨)
    - [従来の Python セットアップ](#従来の-python-セットアップ)
  - [パッケージの作成](#パッケージの作成)
  - [使用方法](#使用方法)
    - [uv を使用する場合](#uv-を使用する場合)
    - [pip インストールの場合](#pip-インストールの場合)
  - [コマンドオプション](#コマンドオプション)
    - [共通オプション](#共通オプション)
    - [add コマンド](#add-コマンド)
    - [get コマンド](#get-コマンド)
    - [list コマンド](#list-コマンド)
    - [remove コマンド](#remove-コマンド)
    - [rename コマンド](#rename-コマンド)
  - [ファイル保存場所](#ファイル保存場所)
  - [セキュリティに関する注意](#セキュリティに関する注意)
  - [ライセンス](#ライセンス)

<!-- /TOC -->

## 概要

mktotp は、TOTP（時間ベースのワンタイムパスワード）シークレットを管理し、
二要素認証サービス用の認証トークンを生成するコマンドラインツールです.

## 機能

- QR コード画像から TOTP シークレットを追加
- 登録されたシークレットの TOTP トークンを生成
- 登録されたすべてのシークレットを一覧表示
- シークレットの削除と名前変更

## インストール

### uv を使用する方法（推奨）

このプロジェクトはuvを使用しています.  
uvを使用すると実行環境を自動で再現できます.  

uv のインストールはこちら.  

- [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# mktotp ディレクトリにプロジェクトがcloneされている前提
cd mktotp
# 依存関係をインストールして実行. ヘルプを表示
uv run -m mktotp --help
```

### 従来の Python セットアップ

```bash
# mktotp ディレクトリにプロジェクトがcloneされている前提
cd mktotp
# 仮想環境を作成して依存関係をインストール
python -m venv .venv
source .venv/bin/activate  # Windows の場合: .venv\Scripts\activate
pip install -e .
# ヘルプを表示
python -m mktotp --help
```

## パッケージの作成

モジュールパッケージを作成するには、以下のコマンドを実行します。

```bash
# mktotp ディレクトリにプロジェクトがcloneされている前提
cd mktotp 
# パッケージを作成
uv build
```

## 使用方法

シークレットは任意の名前(シークレット名)を付けて管理します.  

### uv を使用する場合

プロジェクトディレクトリ外から実行する場合は、
`--directory` オプションでプロジェクトディレクトリを指定してください.

```bash
# uv を使用する場合（プロジェクトディレクトリから）
# QR コード画像から新しいシークレットを追加. (既存の場合は上書きされます)
uv run [--directory {project_dir}] -m mktotp add -nn "登録シークレット名" -f "QR-Codeイメージファイルのパス"

# TOTP トークンを生成
uv run [--directory {project_dir}] -m mktotp get -n "シークレット名"

# すべてのシークレットを一覧表示
uv run [--directory {project_dir}] -m mktotp list

# シークレットを削除
uv run [--directory {project_dir}] -m mktotp remove -n "シークレット名"

# シークレットの名前を変更
uv run [--directory {project_dir}] -m mktotp rename -n "現在のシークレット名" -nn "新しいシークレット名"
```

### pip インストールの場合

pip でインストールした場合：

```bash
# pip install の後
python -m mktotp add -nn "シークレット名" -f "QRコードイメージファイルのパス"
python -m mktotp get -n "シークレット名"
python -m mktotp list
python -m mktotp remove -n "シークレット名"
python -m mktotp rename -n "現在のシークレット名" -nn "新しいシークレット名"
```

## コマンドオプション

### 共通オプション

- `-v, --verbose LEVEL`: 出力情報詳細レベルを設定（0: 通常、1: 詳細、2: デバッグ）
- `-s, --secrets-file FILE`: シークレットを保存する JSON ファイルのパス

### add コマンド

QR コード画像から新しいシークレットを追加します。

```bash
uv run [--directory {project_dir}] -m mktotp add -nn <新しい名前> -f <QRコードイメージファイル>
```

- `-nn, --new-name`: シークレットの新しい名前（必須）
- `-f, --file`: QR コードデータを含むファイルのパス（必須）

### get コマンド

指定されたシークレット名の TOTP トークンを生成します。

```bash
uv run [--directory {project_dir}] -m mktotp get -n <シークレット名>
```

- `-n, --name`: 操作対象のシークレット名（必須）

### list コマンド

登録されているすべてのシークレットを表示します。

```bash
uv run [--directory {project_dir}] -m mktotp list
```

### remove コマンド

指定されたシークレットを削除します。

```bash
uv run [--directory {project_dir}] -m mktotp remove -n <シークレット名>
```

- `-n, --name`: 削除するシークレット名（必須）

### rename コマンド

シークレットの名前を変更します。

```bash
uv run [--directory {project_dir}] -m mktotp rename -n <現在の名前> -nn <新しい名前>
```

- `-n, --name`: 現在のシークレット名（必須）
- `-nn, --new-name`: 新しいシークレット名（必須）

## ファイル保存場所

デフォルトでは、シークレットは以下の場所に保存されます：

```text
~/.mktotp/data/secrets.json
```

`-s` オプションで別の場所を指定することもできます。

## セキュリティに関する注意

- シークレットファイルは機密情報を含むため、適切な権限設定で保護してください.  
- バックアップを作成する際は、暗号化されたストレージを使用することを推奨します.  
- 不要になったシークレットは `remove` コマンドで削除してください.  

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。  
詳細は [LICENSE](LICENSE) ファイルをご覧ください。
