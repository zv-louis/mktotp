# mktotp project

TOTP（二要素認証のワンタイムパスワード）のシークレットを管理する CUI ツール兼ローカル MCP サーバー。
QR コード画像からシークレットを登録し、登録済みシークレットからトークンを生成する。
MCP 経由で操作される前提のため、シークレット文字列そのものを LLM 側へ返さないことを設計上の原則としている。

## 技術スタック

- Python 3.12 以上、パッケージ管理は uv、ビルドは hatchling
- 主な依存: `pyotp`（TOTP 生成）、`fastmcp`（MCP サーバー）、`opencv-python` / `pillow` / `cairosvg`（QR コード読み取り、SVG 対応）、`filelock`（排他制御）、`pydantic`
- テスト: pytest + pytest-asyncio（`asyncio_mode = auto`）

## ディレクトリ構成

```text
src/mktotp/
  __main__.py     CLI エントリポイント（main）とサブコマンドのハンドラ
  cmdparam.py     argparse のサブコマンド定義（add / get / list / remove / rename / mcp）
  func_impl.py    CLI と MCP で共有する業務ロジック（SecretMgr を with で開いて操作）
  secrets.py      SecretMgr: シークレット JSON の読み書き、ロック、TOTP 生成
  qrcode_util.py  QR コード画像のデコード（otpauth:// URI を取り出す）
  permutil.py     シークレットファイルの権限設定（Unix は 600、Windows は icacls）
  logutil.py      ロガー（出力は stderr。MCP の stdio を汚さないため）
  mcp_server.py   FastMCP のツール定義（薄いラッパー）
  mcp_impl.py     MCP ツールの実装、入力検証、例外を ValueError に揃える共通処理
src/mktotp_main.py  Claude プラグイン用の MCP 起動スクリプト（PEP 723 のインライン依存を持つ）
test/             モジュールごとの pytest
.claude-plugin/   Claude Code プラグインのマニフェスト
.mcp.json         プラグイン用 MCP サーバー設定（uv run src/mktotp_main.py mcp --mcp-server）
```

処理の流れは、CLI なら `__main__.py` → `func_impl.py` → `secrets.py`、MCP なら `mcp_server.py` → `mcp_impl.py` → `func_impl.py` → `secrets.py` となる。

## CLI

```bash
mktotp add -nn <name> -f <qr_image>     # QR コード画像から登録
mktotp add -nn <name> -ss <secret>      # シークレット文字列を直接登録（CLI のみ）
mktotp get -n <name>                    # トークン生成
mktotp list                             # 一覧
mktotp remove -n <name>                 # 削除
mktotp rename -n <old> -nn <new>        # 名前変更
mktotp mcp --mcp-server                 # MCP サーバーとして起動（オプションなしならツール一覧を表示）
```

共通オプションは `-v, --verbose`（0: 通常、1: 詳細、2: デバッグ）と `-s, --secrets-file`。

## MCP ツール

| ツール | 内容 |
| --- | --- |
| `mktotp_register_secret` | QR コード画像から登録 |
| `mktotp_generate_token` | トークン生成 |
| `mktotp_get_secret_info_list` | 一覧（name / account / issuer のみ。シークレット値は含めない） |
| `mktotp_remove_secrets` | 複数名を指定して削除 |
| `mktotp_rename_secret` | 名前変更 |

各ツールは `secrets_file` を必須引数に取り、空文字列なら既定のファイルを使う。
シークレット文字列の直接登録は MCP には公開していない。

## データ保存

- 既定の保存先は `~/.mktotp/data/secrets.json`（ディレクトリは 0700、ファイルは 600）
- 形式は `{"secrets": [{"name", "account", "issuer", "secret", ...}], "version": "1.0", "last_update": ...}`
- 同じ場所の `secrets.lock` を使い、`filelock` で排他制御する
- 読み込み時に権限が緩ければ自動で修正する

## 開発

```bash
uv sync                 # 依存のインストール
uv run pytest           # テスト実行
uv run mktotp --help    # ローカル実行
```

## 変更時の注意

- MCP ツールの戻り値やログにシークレット値を含めない。`list_secrets(include_secret=False)` の挙動を崩さない
- ログや print は stderr に出す。stdout は MCP の stdio 通信に使われる
- 依存を変えるときは `pyproject.toml` と `src/mktotp_main.py` のインライン依存の両方を更新する
- バージョンは `pyproject.toml` と `.claude-plugin/plugin.json` の両方にある
