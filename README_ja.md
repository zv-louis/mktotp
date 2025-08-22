# mktotp

多要素認証(2FA)用のシンプルなCUIベースのTOTPシークレット管理ツールとローカルMCPサーバ

[English](README.md) | 日本語

<!-- TOC tocDepth:2..3 chapterDepth:2..6 -->

- [mktotp](#mktotp)
  - [概要](#概要)
  - [機能](#機能)
  - [実行環境](#実行環境)
  - [モジュールパッケージの作成](#モジュールパッケージの作成)
  - [使用方法](#使用方法)
    - [プロジェクトから直接モジュールを実行する場合](#プロジェクトから直接モジュールを実行する場合)
    - [python環境へモジュールパッケージをインストールする場合](#python環境へモジュールパッケージをインストールする場合)
    - [MCPサーバとして登録する](#mcpサーバとして登録する)
  - [CUIツールのコマンドオプション](#cuiツールのコマンドオプション)
    - [共通オプション](#共通オプション)
    - [add コマンド](#add-コマンド)
    - [get コマンド](#get-コマンド)
    - [list コマンド](#list-コマンド)
    - [remove コマンド](#remove-コマンド)
    - [rename コマンド](#rename-コマンド)
    - [mcp コマンド](#mcp-コマンド)
  - [ファイル保存場所](#ファイル保存場所)
  - [セキュリティに関する注意](#セキュリティに関する注意)
  - [ライセンス](#ライセンス)

<!-- /TOC -->

## 概要

mktotp は、TOTP（時間ベースのワンタイムパスワード）シークレットを管理し、
二要素認証サービス用の認証トークンを生成するコマンドラインツールです。  
ローカルMCPサーバとしても機能し、一般的なAgentツールを使用して操作することができます。

## 機能

- QR コード画像ファイルを使って TOTP シークレットを登録
- QR コード画像は、PNG, JPEG, BMP, TIFF, SVG 形式に対応
- 登録されたシークレットの TOTP トークンを生成
- 登録されたすべてのシークレットを一覧表示
- シークレットの削除と名前変更
- ローカル MCP サーバとして一般的なAgentツールから操作することが可能

## 実行環境

このプロジェクトはパッケージマネージャにuvを使用しています。  
uvを使用すると実行環境を自動で再現できます。  

uvのインストールはこちら。

- [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# mktotp ディレクトリにプロジェクトがcloneされている前提
cd mktotp
# 依存関係をインストールして実行. ヘルプを表示
uv run -m mktotp --help
```

## モジュールパッケージの作成

モジュールパッケージを作成するには、uvの以下のコマンドを実行します。  
生成したパッケージはdistディレクトリに保存されます。  
生成したパッケージはpipなどでインストールすることができます。

```bash
# mktotp ディレクトリにプロジェクトがcloneされている前提
cd mktotp 
# パッケージを作成
uv build
```

## 使用方法

### プロジェクトから直接モジュールを実行する場合

uvを使用してプロジェクトディレクトリから直接実行することができます。  

プロジェクトディレクトリ外から実行する場合は、
`--directory` オプションでプロジェクトディレクトリを指定してください。

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

### python環境へモジュールパッケージをインストールする場合

ビルドしたモジュールパッケージをpipコマンドでインストールして使用することもできます.

```bash
# pip でインストールする場合は、以下のコマンドを実行
# モジュールパッケージをインストール
pip install mktotp-<version>.tar.gz
# または、wheelファイルをインストール
pip install mktotp-<version>-py3-none-any.whl

# uv を使用してインストールする場合は、以下のコマンドを実行
uv pip install mktotp-<version>.tar.gz
# または、wheelファイルをインストール
uv pip install mktotp-<version>-py3-none-any.whl
```

インストール後は、以下のようにコマンドを実行できます。

```bash
# QR コード画像から新しいシークレットを追加
python -m mktotp add -nn "登録シークレット名" -f "QR-Codeイメージファイルのパス"
# TOTP トークンを生成
python -m mktotp get -n "シークレット名"
# すべてのシークレットを一覧表示
python -m mktotp list
# シークレットを削除
python -m mktotp remove -n "シークレット名" 
# シークレットの名前を変更
python -m mktotp rename -n "現在のシークレット名" -nn "新しいシークレット名"
```

### MCPサーバとして登録する

MCPサーバとして登録することで、一般的なAgentツールからmktotpを操作することができます。

```json
{
  // MCPサーバとして登録する場合の設定例
  //
  // (注意) 
  // Agentツールによって登録キーが異なることがあるので、
  // 詳細な手順はそれぞれ使用するAgentツールのマニュアルを参照してください。
  "mcpServers" {
    // uvを使用してmktotpをMCPサーバとして起動する設定
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
    // python環境にモジュールをインストールした場合の起動設定
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

## CUIツールのコマンドオプション

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

### mcp コマンド

モジュールをローカルMCPサーバとして起動します。  
Agentツールを使用してmktotpを操作することができます。

```bash
uv run [--directory {project_dir}] -m mktotp mcp --mcp-server
```

`--mcp-server` オプションを指定しない場合は、MCPのtool一覧を出力します。

```bash
uv run [--directory {project_dir}] -m mktotp mcp
```

## ファイル保存場所

デフォルトでは、シークレットは以下の場所に保存されます：

```text
~/.mktotp/data/secrets.json
```

`-s` オプションで別の場所を指定することもできます。

## セキュリティに関する注意

- シークレットファイルは機密情報を含むため、適切な権限設定で保護してください。  
- バックアップを作成する際は、暗号化されたストレージを使用することを推奨します。  
- 不要になったシークレットは `remove` コマンドで削除してください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。  
詳細は [LICENSE](LICENSE) ファイルをご覧ください。
