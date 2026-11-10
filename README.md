# gbizinfo-mcp

Gビズインフォ REST API v2の現行18エンドポイントを、MCP・CLI・Pythonから利用できます。MCPはstdioで動作し、APIのJSONレスポンスをそのまま返します。

[MCP登録](#mcpクライアントに登録する) · [CLI](#cliで使う) · [Pythonライブラリ](#pythonライブラリとして使う)

## MCPクライアントに登録する

Python 3.11以上、[uv](https://docs.astral.sh/uv/) と Git、Gビズインフォで発行したAPIトークンが必要です。 設定例の `your_token` は手元で差し替えてください。

### Codex

```sh
codex mcp add gbizinfo --env "GBIZINFO_API_TOKEN=your_token" -- uvx --python 3.12 --from git+https://github.com/koizumikento/gbizinfo-mcp.git@master gbizinfo-mcp
codex mcp list
```

新しいセッションの `/mcp` で接続を確認します。デスクトップ版では設定の「MCP servers」でSTDIOを選び、下のJSONと同じコマンド・引数を入力して保存し、再起動します。 環境変数も設定してください。 [OpenAI公式のMCP設定](https://learn.chatgpt.com/docs/extend/mcp)

### Claude Desktop / Cursor

- Claude Desktop（Windows） `%APPDATA%/Claude/claude_desktop_config.json`
- Claude Desktop（macOS） `~/Library/Application Support/Claude/claude_desktop_config.json`
- Cursor `.cursor/mcp.json`（プロジェクト内）

既存の `mcpServers` に項目を追加し、保存後にクライアントを再起動します。`uvx` が見つからない場合は `command` に実行ファイルの絶対パスを指定してください。

```json
{
  "mcpServers": {
    "gbizinfo": {
      "command": "uvx",
      "args": [
        "--python",
        "3.12",
        "--from",
        "git+https://github.com/koizumikento/gbizinfo-mcp.git@master",
        "gbizinfo-mcp"
      ],
      "env": {
        "GBIZINFO_API_TOKEN": "your_token"
      }
    }
  }
}
```

## CLIで使う

CLIとPythonを実行するシェルでトークンを設定します。

```powershell
$env:GBIZINFO_API_TOKEN = "your_token"
```

macOSやLinuxでは `export GBIZINFO_API_TOKEN="your_token"` を使います。

クローンせずに実行できます。結果は標準出力に出ます。

引数はJSONオブジェクトで渡します。例の法人番号は照会したい13桁の番号に置き換えてください。次の例はPowerShell 7.3以降またはmacOS・Linuxのシェルで実行できます。

```sh
uvx --python 3.12 --from git+https://github.com/koizumikento/gbizinfo-mcp.git@master gbizinfo-mcp hojin_get_basic --args '{"corporate_number":"1234567890123"}'
```

## Pythonライブラリとして使う

自分のPythonプロジェクト（`pyproject.toml` があるディレクトリ）で依存関係に追加します。[CLIで使う](#cliで使う)と同様に、実行するシェルで `GBIZINFO_API_TOKEN` を設定してください。

```sh
uv add "git+https://github.com/koizumikento/gbizinfo-mcp.git@master"
```

次のコードを `example.py` に保存し、同じディレクトリで `uv run python example.py` を実行します。

`create_toolset()` で作ったクライアントで、MCPと同名の非同期メソッドを呼び出せます。

```python
import asyncio

from gbizinfo_mcp import create_toolset

gbizinfo = create_toolset()
print(asyncio.run(gbizinfo.hojin_get_basic(corporate_number="1234567890123")))
```

## ツール

- 法人検索: `hojin_search`
- 期間指定更新情報: `hojin_update_info_basic`、`hojin_update_info_certification`、`hojin_update_info_commendation`、`hojin_update_info_finance`、`hojin_update_info_patent`、`hojin_update_info_procurement`、`hojin_update_info_subsidy`、`hojin_update_info_workplace`
- 法人番号指定取得: `hojin_get_basic`、`hojin_get_certification`、`hojin_get_commendation`、`hojin_get_corporation`、`hojin_get_finance`、`hojin_get_patent`、`hojin_get_procurement`、`hojin_get_subsidy`、`hojin_get_workplace`

法人ごとの事業所情報は `hojin_get_corporation` で照会できます。一括取得には公式サイトのデータダウンロードを使ってください。`hojin_update_info_corporation` を呼ぶと、期間指定のAPIには接続せず、代わりの取得方法を案内します。[公式のお知らせ](https://help.info.gbiz.go.jp/hc/ja/articles/5543677736734)

## データ出典・利用条件

本サーバーはGビズインフォの情報提供REST APIを利用します。API利用前に、公式の[APIページ](https://content.info.gbiz.go.jp/api/index.html)、[API・データダウンロード利用規約](https://help.info.gbiz.go.jp/hc/ja/articles/4999421139102-API-%E3%83%87%E3%83%BC%E3%82%BF%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89%E5%88%A9%E7%94%A8%E8%A6%8F%E7%B4%84)、[Gビズインフォ利用規約](https://help.info.gbiz.go.jp/hc/ja/articles/4795140981406-%E5%88%A9%E7%94%A8%E8%A6%8F%E7%B4%84)を確認してください。取得データの権利・利用条件は提供元に従います。

## 開発

SitesのWorkerで実行する場合は [Sites用adapterと配備手順](docs/sites.md) を参照してください。

```bash
uv sync --frozen
uv run ruff check .
uv run ty check
uv run pytest
uv build
```

## License

[MIT](LICENSE)
