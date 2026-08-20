# gbizinfo-mcp

Gビズインフォ REST API v2の19エンドポイントを、同名の19 MCP toolsとして提供します。stdio transportで動作し、APIのJSONレスポンスをそのまま返します。

## 実行

Python 3.11+、[`uv`](https://docs.astral.sh/uv/)、GビズインフォのAPIトークンが必要です。

```bash
GBIZINFO_API_TOKEN=your_token \
uvx --from git+https://github.com/koizumikento/gbizinfo-mcp.git@master gbizinfo-mcp
```

MCPクライアント設定例:

```json
{
  "mcpServers": {
    "gbizinfo": {
      "command": "uvx",
      "args": [
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

任意設定は `GBIZINFO_BASE_URL`（既定: `https://api.info.gbiz.go.jp/hojin`）と `GBIZINFO_TIMEOUT_SECONDS`（既定: `20`）です。

## ツール

- 法人検索: `hojin_search`
- 期間指定更新情報: `hojin_update_info_basic`、`hojin_update_info_certification`、`hojin_update_info_commendation`、`hojin_update_info_corporation`、`hojin_update_info_finance`、`hojin_update_info_patent`、`hojin_update_info_procurement`、`hojin_update_info_subsidy`、`hojin_update_info_workplace`
- 法人番号指定取得: `hojin_get_basic`、`hojin_get_certification`、`hojin_get_commendation`、`hojin_get_corporation`、`hojin_get_finance`、`hojin_get_patent`、`hojin_get_procurement`、`hojin_get_subsidy`、`hojin_get_workplace`

## データ出典・利用条件

本サーバーはGビズインフォの情報提供REST APIを利用します。API利用前に、公式の[APIページ](https://content.info.gbiz.go.jp/api/index.html)、[API・データダウンロード利用規約](https://help.info.gbiz.go.jp/hc/ja/articles/4999421139102-API-%E3%83%87%E3%83%BC%E3%82%BF%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89%E5%88%A9%E7%94%A8%E8%A6%8F%E7%B4%84)、[Gビズインフォ利用規約](https://help.info.gbiz.go.jp/hc/ja/articles/4795140981406-%E5%88%A9%E7%94%A8%E8%A6%8F%E7%B4%84)を確認してください。取得データの権利・利用条件は提供元に従います。

## 開発

```bash
uv sync --frozen
uv run ruff check .
uv run ty check
uv run pytest
uv build
```

## License

[MIT](LICENSE)
