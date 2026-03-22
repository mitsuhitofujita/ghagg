# 実行環境

## Python

| 項目 | 値 |
|---|---|
| バージョン | Python 3.14.3 |
| 必須バージョン（pyproject.toml） | `>=3.14` |
| パッケージマネージャ | uv 0.10.12 |
| ビルドバックエンド | uv_build `>=0.10.12,<0.11.0` |
| 外部依存パッケージ | なし（標準ライブラリのみ） |

## GitHub CLI

| 項目 | 値 |
|---|---|
| バージョン | gh 2.88.1 (2026-03-12) |
| 認証方式 | keyring |
| Git 操作プロトコル | HTTPS |

## コマンド実行方法

```bash
# PR データ取得
uv run ghagg fetch <label> <owner/repo> --since <YYYY-MM-DD> --until <YYYY-MM-DD>

# メンバー別集計
uv run ghagg aggregate <label>
```

`uv run` により仮想環境の作成・依存解決が自動で行われる。`gh` CLI に認証を委譲しているため、別途 GitHub トークンの設定は不要。
