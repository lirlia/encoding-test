## encoding-test

一般的に有名な文字列エンコーディングごとの HTML を GitHub Pages でホストするテスト用リポジトリです。

### 公開方法（GitHub Pages）

- `main` ブランチへの push をトリガに GitHub Actions が `public/` をデプロイします。
- リポジトリの Settings → Pages で **Build and deployment: GitHub Actions** を選ぶだけで動きます（Workflow を同梱しています）。

### ページ構成

- `public/index.html`: 入口（UTF-8）
- `public/encodings/*.html`: 文字コード別ページ（ファイル自体を各エンコーディングで生成）

