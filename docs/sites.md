# Sites Worker adapter

SitesのWorkerからgBizINFO REST API v2へ直接HTTPSで接続します。別Python backend、tunnel、D1、R2は不要です。既存Python library・CLI・stdioを変更せず、`sites/` に独立したstateless `POST /mcp` を追加しています。

## 契約とアクセス

- 既存Python `create_server().list_tools()` から19 toolsの名前、説明、input/output schema、annotationsを生成して `sites/worker/contract.json` に記録します。routes、都道府県変換、timeout、retry設定も既存実装から生成します。CIの `contract:check` がPythonとの一致を保証します。Python契約を変更したら `uv run python sites/export_contract.py` で再生成し、再buildしてください。
- tool成功時はupstreamのJSON objectをそのまま `structuredContent` とJSON textで返します。page、limit、metadata、出典、空結果を変形せず、次ページを自動取得しません。
- OpenAPIのint64を丸めないため、textはupstream JSONを保持し、SDKのJSON/SSE envelopeを確定後、structuredContentの数値を `JSON.parse` source contextと `JSON.rawJSON` で復元します。Nodeとisolated workerdで2^53を超える値をwire上で確認します。
- required引数・JSON schemaのprimitive type・法人番号・日付・期間・page・limit・都道府県を検証します。Workerではschema違反の型変換と未知の引数を拒否します。Python SDKの暗黙変換を利用するcallerはadvertised schemaに合わせてください。
- GET先はbuild時に固定した公式APIと19 routesのみです。任意URL/path forwardingやredirect追従はありません。Python側の `GBIZINFO_BASE_URL` / timeout設定は従来通り、Workerは公式URLと既存の既定20秒を使います。
- 429/500/502/503/504は最大2 retries（250ms、500ms）です。HTTP errorは `isError: true` とstatus、invalid JSON/rootもtool errorとして返します。Workerのerror textはsecret保護のためupstream body、reason phrase、例外の詳細を省略します。ネットワーク/timeoutは安全な再試行案内を返します。
- Sites DispatchがOAuthと接続認証を担当します。Workerは `/mcp` で `oai-authenticated-user-id` を必須にし、Sitesの既存audience/access policyを保ちます。Siteにアクセス可能なsigned-in userは、このSiteのサービス用API tokenで公開法人情報を検索できます。discoveryにはprivate dataやsecretを含めません。
- service accessの `OAI-Sites-Authorization` だけではユーザーidentityを持たず、本adapterでは401です。ユーザーを偽装する代替OAuth、backend token、emailによる権限判定は追加していません。
- identity headerを信頼する境界はSites Dispatchです。Workerを直接公開したり、ヘッダーを任意に偽造できる経路に接続しないでください。Originはendpoint hostnameに限定し、OriginなしのMCP clientは許可します。

## ローカルbuildと検証

検証にはPython 3.11+、uv、Node.js 24、npmが必要です。生成contractはGitに含め、`dist/` は含めません。API tokenなしで実行できます。配備artifactのbuildはNode/npmだけで実行できます。

```text
uv sync --frozen
uv run ruff check .
uv run ty check
uv run pytest
uv build
cd sites
npm ci
npm run contract:check
npm run build
npm test
```

公式SDK `@modelcontextprotocol/server` 2.3.1をbundleし、Worker ESM starterと同じ配備構造を作ります:

```text
sites/dist/
  .openai/hosting.json
  server/index.js   # default.fetch(request, env, ctx)
```

`.openai/hosting.json` は `capabilities: ["mcp"]`、未使用 `d1` / `r2: null` を宣言し、`static` を持ちません。repoにSite IDは含めません。manifestを変更したら再buildしてください。

testsはbuildしたESMそのものをimportします。synthetic dataのみで19 routes/queryをPythonの `GbizInfoToolset` と照合し、全discovery schema、paging/provenance、認証拒否、service-only拒否、Origin、schema/domain validation、retry exhaustion、secret非反映、不正応答を検証します。公式SDK clientで旧initialize（2025-11-25）と新版discover（2026-07-28）の両方をin-process検証します。Miniflare/workerdでもloopbackの使い捨てruntimeを起動し、outboundServiceをsynthetic応答に固定して実artifactとint64を確認します。`finally` でruntime停止と専用temporary directoryの削除を行います。本物のgBizINFO APIは利用しません。Miniflare 5は現時点の公式releaseがalphaのためexact versionで固定し、dev dependencyだけに使用します。

## Sitesへの配備（PRレビュー後）

このPR自体はSiteを作成・配備しません。登録済みSiteならそのidentity、audience、pluginを再利用してください。新規Siteはprivateで作成します。以下は公式Sites skillのworkflowで実施する手順です。

1. native Sites `create_site`、または既存Siteの `get_site` と `create_source_repository_write_credential` を使います。取得したSite IDを、`sites/` をcwdにして `node <sites-plugin-root>/scripts/set-project-id.mjs --project-id <returned-id>` でsource manifestへ保存します。既存manifestの他fieldは保ちます。
2. native Sites runtime secret管理で **GBIZINFO_API_TOKEN** を設定します。`sites/.env.example` はkey名のみです。secret値はsource、manifest、browser、CLI引数、log、promptに保存しません。
3. 上記のrepo全体の検証を完了してから、`sites/` のsource（`.openai/hosting.json`、package/lockfile、scripts、worker、tests、exporter）を選択したSite専用checkoutへコピーします。`node_modules`、`dist`、Git metadata、credential、別Siteのidentityはコピーしません。既存Siteの場合は公式source helperで先にcheckoutを開き、そのmanifest/identityを保持して必要な変更だけを適用します。新規Siteでは空の専用checkoutにsourceをコピーし、返されたIDを保存します。
4. Site専用checkoutで `npm ci` を実行します。公式source helperを `node <sites-plugin-root>/scripts/site-workflow.mjs --project-id <id>` で起動し、credentialはhidden stdinに渡します。packageのordered `commands` は `[["npm", "run", "build"]]`、`archivePath` は作業用の絶対pathです。export済みcontractを含むためPython backendや親repoなしでbuildできます。`contract:check` / `npm test` はPython repoと比較する検証なのでrepo内の `sites/` で行います。
5. helperが返すsource commit / archiveをnative `save_version_and_deploy_private`（owner-private）、またはaudienceに適したsave/deployへ渡します。宣言済みMCPとidentityを保ち、別OAuthやpluginを作り直しません。配備artifactにはbundle済みJSだけが入り、hosted Python/Node processは不要です。
6. `get_site(include_mcp_connection: true)` でMCP接続情報を確認し、必要な場合のみ返されたpluginをinstall/connectします。authenticated discoveryと許可されたread-only callを別途確認します。配備成功だけでclient接続成功と扱いません。

## 確認済み範囲と片づけ

2026-10-10に公式[Streamable HTTP仕様](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)と[TypeScript SDK HTTP entry](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/serving/http.md)、同[旧版互換ガイド](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/migration/support-2026-07-28.md)を確認しました。protocol framing/negotiationはSDKに任せ、各requestに独立したserver/transportを作ります。Sites runtime/manifest/identity契約は公式Sites skillのWorker ESM starter、site-mcp-server、identity-and-secrets referencesに合わせています。

local/mock、CI、実際のSites deployment、authenticated hosted discovery、clientの実サービス呼出しは別の証拠です。PR段階のhosted deployment・gBizINFO live呼出しは未実施です。

検証後は、このworktreeで作った `.venv`、`sites/node_modules`、Python/Worker `dist/`、test/type/cacheを削除できます。source、生成contract、lockfiles、再現用tests、PR branch/worktreeは保持します。共有cacheや他checkoutの環境を削除しないでください。
