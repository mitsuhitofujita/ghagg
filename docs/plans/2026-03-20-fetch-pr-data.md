# ghagg: GitHub PR データ取得コマンド実装計画

## Context
チームのレビュー文化を可視化するため、GitHub の PR 情報を GraphQL API で取得し JSON 保存する CLI ツールを新規開発する。KISS & YAGNI を徹底し、`gh api graphql` を subprocess 経由で呼び出すシンプルなアプローチをとる。今回のスコープはデータ取得・保存のみ（集計は後のステップ）。

## プロジェクト構造

```
ghagg/
├── pyproject.toml
├── src/
│   └── ghagg/
│       ├── __init__.py
│       ├── cli.py              # argparse による CLI エントリポイント
│       ├── github_client.py    # gh api graphql の subprocess ラッパー
│       ├── queries.py          # GraphQL クエリ文字列定数
│       ├── fetcher.py          # 2フェーズ取得のオーケストレーション
│       └── storage.py          # JSON ファイル保存
├── data/
│   └── json/                   # 出力先（.gitignore 対象）
└── docs/
    └── intent.md
```

## CLI インターフェース

```
uv run ghagg owner/repo --since 2025-01-01 --until 2025-03-31
```

- `repo`（位置引数）: `owner/repo` 形式
- `--since`（必須）: 開始日 YYYY-MM-DD
- `--until`（必須）: 終了日 YYYY-MM-DD
- `--output-dir`（任意、デフォルト `data/json/`）

## GraphQL 取得戦略: 2フェーズ方式

### Phase 1: PR リスト + ネストデータ初回取得
- `search` API を使用（`repo:{owner}/{repo} is:pr created:{since}..{until}`）
  - `repository.pullRequests` は日付フィルタ非対応のため `search` を採用
- PR は `first: 20` でページネーション
- ネストデータのバッチサイズ:
  - `reviews(first: 100)` / `comments(first: 100)` / `reviewThreads(first: 50)` / `reviewThreads.comments(first: 30)`
- 各接続に `totalCount`, `pageInfo { hasNextPage endCursor }` を含める

### Phase 2: オーバーフロー分の追加取得
- `hasNextPage: true` の接続に対し、`node(id: $prId)` クエリで個別にページネーション
- reviews, comments, reviewThreads, reviewThreads.comments それぞれに対応するクエリを用意

### 取得フィールド（PR 本体）
`id`, `number`, `title`, `state`, `createdAt`, `updatedAt`, `mergedAt`, `closedAt`, `additions`, `deletions`, `changedFiles`, `author.login`, `mergedBy.login`, `baseRefName`, `headRefName`, `reviewDecision`

## モジュール責務

| モジュール | 責務 |
|---|---|
| `cli.py` | argparse 定義、日付バリデーション、fetcher/storage の呼び出し |
| `github_client.py` | `execute_graphql(query, variables) -> dict` — subprocess で `gh api graphql` を実行、JSON パース |
| `queries.py` | GraphQL クエリ文字列を定数として定義（Phase 1 + Phase 2 の各クエリ） |
| `fetcher.py` | `fetch_pull_requests(repo, since, until)` — 2フェーズ取得ロジック |
| `storage.py` | `save(data, repo, since, until, output_dir)` — JSON 保存 |

## ファイル保存規則
- パス: `data/json/{owner}__{repo}__{since}__{until}.json`
- 例: `mitsuhitofujita__ghagg__2025-01-01__2025-03-31.json`
- `__` 区切り（owner/repo 名にハイフンが含まれるため）
- `json.dump(data, f, ensure_ascii=False, indent=2)`

## 設計判断
- **外部依存ゼロ**: 標準ライブラリのみ使用（argparse, subprocess, json, pathlib, logging, datetime）
- **認証**: `gh` CLI に委譲（トークン管理不要）
- **エラー処理**: gh 未インストール/未認証 → SystemExit、GraphQL エラー → RuntimeError、レートリミット → abort（リトライなし = YAGNI）

## 実装順序

1. `uv init` でプロジェクト初期化、`pyproject.toml` 調整
2. `src/ghagg/github_client.py` — subprocess ラッパー
3. `src/ghagg/queries.py` — GraphQL クエリ定数
4. `src/ghagg/fetcher.py` — 2フェーズ取得ロジック
5. `src/ghagg/storage.py` — JSON 保存
6. `src/ghagg/cli.py` — CLI エントリポイント
7. `.gitignore` に `data/json/` 追加、`data/json/.gitkeep` 作成
8. E2E テスト: 実リポジトリに対して実行し JSON 出力を確認

## 検証方法
```bash
uv run ghagg mitsuhitofujita/ghagg --since 2025-01-01 --until 2025-12-31
# data/json/ に JSON ファイルが生成されることを確認
cat data/json/mitsuhitofujita__ghagg__2025-01-01__2025-12-31.json | python -m json.tool | head -50
```
