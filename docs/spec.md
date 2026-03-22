# ghagg コマンド仕様

## 概要

GitHub の PR データを GraphQL API で取得し JSON ファイルに保存する CLI ツール。
保存済みデータからメンバーごとの活動を集計する機能も備える。
`gh api graphql` を subprocess 経由で呼び出し、外部依存ゼロで動作する。

## CLI インターフェース

### fetch — PR データ取得

```
uv run ghagg fetch <label> <owner/repo> --since <YYYY-MM-DD> --until <YYYY-MM-DD> [--output-dir <dir>]
```

| 引数 | 種別 | 必須 | 説明 |
|---|---|---|---|
| `label` | 位置引数 | Yes | 出力グループ名（例: `2025`, `2026`）。年度別比較等に使用 |
| `repo` | 位置引数 | Yes | GitHub リポジトリ（`owner/repo` 形式） |
| `--since` | オプション | Yes | 開始日（YYYY-MM-DD） |
| `--until` | オプション | Yes | 終了日（YYYY-MM-DD） |
| `--output-dir` | オプション | No | 出力ディレクトリ（デフォルト: `data/json/`） |

### aggregate — メンバー別集計

```
uv run ghagg aggregate <label> [--data-dir <dir>]
```

| 引数 | 種別 | 必須 | 説明 |
|---|---|---|---|
| `label` | 位置引数 | Yes | 集計対象のラベル（例: `2025`, `2026`） |
| `--data-dir` | オプション | No | データディレクトリ（デフォルト: `data/json/`） |

`{data-dir}/{label}/` 内の全 `*.json` ファイルを読み込み、メンバーごとに以下を集計して JSON を標準出力に出力する。

- `pull_requests` — PR の作成数（`author.login`）
- `comments` — PR コメント数（`comments.nodes[].author.login`）
- `review_comments` — 行コメント数（`reviewThreads.nodes[].comments.nodes[].author.login`）
- `approvals` — アプルーブ数（`reviews.nodes[]` で `state == "APPROVED"`）

ファイル間での PR やコメントの重複排除は行わない。各ファイル内のデータをそのまま加算する。

#### 出力例

```json
[
  {
    "member": "crynobone",
    "pull_requests": 1,
    "comments": 0,
    "review_comments": 0,
    "approvals": 0
  },
  {
    "member": "taylorotwell",
    "pull_requests": 0,
    "comments": 1,
    "review_comments": 0,
    "approvals": 0
  }
]
```

## 出力パス規則（fetch）

```
{output-dir}/{label}/{owner}__{repo}__{since}__{until}.json
```

- `__`（ダブルアンダースコア）区切り — owner/repo 名にハイフンが含まれうるため
- `{label}` ディレクトリで年度・期間別にグループ化

### 例

```bash
uv run ghagg fetch 2025 laravel/laravel --since 2025-03-16 --until 2025-03-22
# → data/json/2025/laravel__laravel__2025-03-16__2025-03-22.json

uv run ghagg fetch 2026 laravel/laravel --since 2026-03-16 --until 2026-03-22
# → data/json/2026/laravel__laravel__2026-03-16__2026-03-22.json
```

## 取得データ

### PR 本体フィールド

`id`, `number`, `title`, `state`, `createdAt`, `updatedAt`, `mergedAt`, `closedAt`,
`additions`, `deletions`, `changedFiles`, `author.login`, `mergedBy.login`,
`baseRefName`, `headRefName`, `reviewDecision`

### ネストデータ

- `reviews` — レビュー（id, author.login, state, createdAt, body）
- `comments` — PR コメント（id, author.login, createdAt, body）
- `reviewThreads` — レビュースレッド（id, isResolved, comments）

## 取得戦略

### Phase 1: PR リスト + ネストデータ初回取得
- GraphQL `search` API を使用（`repository.pullRequests` は日付フィルタ非対応のため）
- PR: `first: 20` でページネーション
- ネストデータ: reviews `first: 100` / comments `first: 100` / reviewThreads `first: 50` / reviewThreads.comments `first: 30`

### Phase 2: オーバーフロー分の追加取得
- `hasNextPage: true` の接続に対し `node(id: $prId)` クエリで個別にページネーション

## 設計判断

- **外部依存ゼロ**: 標準ライブラリのみ使用（argparse, subprocess, json, pathlib, logging, datetime, collections）
- **認証**: `gh` CLI に委譲（トークン管理不要）
- **エラー処理**: gh 未インストール/未認証 → SystemExit、GraphQL エラー → RuntimeError
