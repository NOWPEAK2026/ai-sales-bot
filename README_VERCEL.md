# Vercelデプロイ手順

## 📋 前提条件

- Gitアカウント（GitHub、GitLab、Bitbucketのいずれか）
- Vercelアカウント（https://vercel.com/signup）

---

## 🚀 デプロイ手順

### 1. Gitリポジトリの作成

まず、プロジェクトをGitリポジトリとして初期化します：

```bash
cd /Users/hirotoito/ai-sales-bot

# Gitリポジトリを初期化
git init

# .gitignoreファイルを作成
echo "__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.vscode
.DS_Store
*.db
*.db-journal
output/
*.log
.env
requirements_local.txt
requirements_web.txt
app.py.bak
start_web.sh" > .gitignore

# ファイルを追加
git add .

# コミット
git commit -m "Initial commit for Vercel deployment"
```

### 2. GitHubにリポジトリをプッシュ

```bash
# GitHubに新しいリポジトリを作成（Webブラウザで https://github.com/new を開いて作成）

# リモートリポジトリを追加（YOUR_USERNAMEとYOUR_REPOを置き換えてください）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# プッシュ
git branch -M main
git push -u origin main
```

### 3. Vercelでデプロイ

1. https://vercel.com にログイン
2. 「New Project」をクリック
3. GitHubリポジトリを選択
4. プロジェクト設定：
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: （空欄のまま）
   - **Output Directory**: （空欄のまま）
5. 環境変数を設定（オプション）：
   - `USE_MEMORY_DB` = `true`
6. 「Deploy」をクリック

---

## 🌐 デプロイ後

デプロイが完了すると、Vercelが自動的にURLを生成します：
- 例：`https://your-project.vercel.app`

このURLを共有することで、誰でもアプリケーションを使用できます！

---

## ⚠️ 重要な注意事項

### 1. メモリストア使用時の制限

Vercel Serverless Functions環境では、以下の制限があります：

- **データの永続化なし**: サーバーが再起動されると検索履歴が消えます
- **関数タイムアウト**: 無料プランでは10秒、Pro プランでは60秒まで
- **同時実行**: 検索リクエストは別々のインスタンスで処理される可能性があります

### 2. 推奨：外部データベースの使用

本番環境では、以下のデータベースサービスの使用を推奨します：

#### Vercel Postgres（推奨）
```bash
# Vercelダッシュボードで「Storage」→「Create Database」→「Postgres」
# 自動的に環境変数が設定されます
```

#### Supabase（無料で使いやすい）
1. https://supabase.com でプロジェクトを作成
2. Vercelの環境変数に設定：
   - `DATABASE_URL` = `postgresql://...`
   - `USE_MEMORY_DB` = `false`

---

## 🔧 カスタムドメインの設定

1. Vercelダッシュボードで「Settings」→「Domains」
2. カスタムドメインを追加
3. DNSレコードを設定

---

## 📊 モニタリング

Vercelダッシュボードで以下を確認できます：

- デプロイメントログ
- ランタイムログ
- アクセス統計
- エラーレポート

---

## 🆘 トラブルシューティング

### エラー: "Module not found"

`requirements.txt`に必要なパッケージが記載されているか確認してください。

### タイムアウトエラー

検索する企業数を減らすか、Proプランにアップグレードしてください。

### データが消える

メモリストアを使用している場合は正常です。永続化が必要な場合は外部データベースを使用してください。

---

## 📝 更新方法

コードを更新したい場合：

```bash
# 変更をコミット
git add .
git commit -m "Update description"

# プッシュ（自動的にデプロイされます）
git push
```

Vercelは自動的に新しいデプロイメントを作成します！

---

## 💰 料金

- **Hobby（無料）**:
  - 月間100GBの帯域幅
  - 関数実行時間: 10秒
  - 十分な数のデプロイメント

- **Pro（月$20）**:
  - より多くの帯域幅
  - 関数実行時間: 60秒
  - 優先サポート

---

## 🎉 完了！

おめでとうございます！アプリケーションが全世界に公開されました🌍

