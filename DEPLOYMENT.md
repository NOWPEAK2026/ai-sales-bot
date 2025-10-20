# 🚀 Vercelデプロイ - クイックスタート

## 最も簡単な方法（5分で完了）

### ステップ1: GitHubにプッシュ

1. **GitHubで新しいリポジトリを作成**
   - https://github.com/new にアクセス
   - リポジトリ名を入力（例：`ai-sales-bot`）
   - 「Create repository」をクリック

2. **ローカルからプッシュ**
   ```bash
   cd /Users/hirotoito/ai-sales-bot
   
   # GitHubのURLを設定（YOUR_USERNAMEを自分のユーザー名に変更）
   git remote add origin https://github.com/YOUR_USERNAME/ai-sales-bot.git
   
   # プッシュ
   git branch -M main
   git push -u origin main
   ```

### ステップ2: Vercelでデプロイ

1. **Vercelにログイン**
   - https://vercel.com/login にアクセス
   - GitHubアカウントでログイン

2. **プロジェクトをインポート**
   - ダッシュボードで「Add New...」→「Project」をクリック
   - GitHubからリポジトリを選択
   - 「Import」をクリック

3. **設定（そのままでOK）**
   - Framework Preset: `Other`
   - Build Command: （空欄）
   - Output Directory: （空欄）
   - Install Command: `pip install -r requirements.txt`

4. **デプロイ**
   - 「Deploy」ボタンをクリック
   - 約1-2分で完了！

### ステップ3: 完了！

デプロイが完了すると、以下のようなURLが表示されます：
```
https://your-project-name.vercel.app
```

このURLを共有すれば、誰でもアプリを使用できます！🎉

---

## 📱 代替方法：Vercel CLI

コマンドラインから直接デプロイすることもできます：

```bash
# Vercel CLIをインストール
npm install -g vercel

# ログイン
vercel login

# デプロイ
cd /Users/hirotoito/ai-sales-bot
vercel --prod
```

数回質問に答えるだけで、自動的にデプロイされます！

---

## 🔄 更新方法

コードを更新したい場合：

```bash
cd /Users/hirotoito/ai-sales-bot

# 変更を確認
git status

# 変更をコミット
git add .
git commit -m "アップデート内容の説明"

# プッシュ（自動的に再デプロイされます）
git push
```

Vercelは自動的に新しいバージョンをデプロイします！

---

## ⚡ パフォーマンス最適化

### 1. 企業数の制限

大量の企業検索（50社以上）は時間がかかる場合があります。
Vercel無料プランのタイムアウト（10秒）を避けるため：

- 推奨：10-30社まで
- 最大：50社まで

### 2. Pro プランの検討

多くのユーザーが同時に使用する場合は、Proプラン（月$20）を推奨：
- 関数タイムアウト: 60秒
- より高速な実行
- 優先サポート

---

## 🌍 カスタムドメインの設定

独自ドメインを使いたい場合：

1. Vercelダッシュボードで「Settings」→「Domains」
2. ドメインを追加（例：`sales-bot.yourdomain.com`）
3. 表示されるDNS設定を、ドメインプロバイダーで設定

---

## 🔒 環境変数の追加（オプション）

APIキーなどを追加したい場合：

1. Vercelダッシュボードで「Settings」→「Environment Variables」
2. 変数を追加：
   - Key: `API_KEY`
   - Value: `your-secret-key`
   - Environment: `Production`

---

## 📊 アクセス状況の確認

Vercelダッシュボードで以下を確認できます：

- **Analytics**: アクセス数、ページビュー
- **Logs**: エラーログ、実行ログ
- **Deployments**: デプロイ履歴

---

## 🆘 よくある質問

### Q: デプロイに失敗しました

A: Vercelダッシュボードの「Deployments」タブでログを確認してください。

### Q: 検索履歴が消えます

A: メモリストアを使用しているため、サーバー再起動時にデータが消えます。
   永続化が必要な場合は、Vercel PostgresやSupabaseを使用してください。

### Q: 無料プランで十分ですか？

A: 個人利用や小規模チーム（月間数千リクエスト程度）なら十分です。

---

## 🎯 次のステップ

1. ✅ GitHubにプッシュ
2. ✅ Vercelでデプロイ
3. ✅ URLを共有
4. （オプション）カスタムドメイン設定
5. （オプション）Vercel Postgres追加

---

## 💡 ヒント

- **自動デプロイ**: mainブランチにプッシュすると自動的にデプロイされます
- **プレビュー**: 他のブランチにプッシュすると、プレビューURLが生成されます
- **ロールバック**: 過去のデプロイメントに簡単に戻せます

---

準備完了です！GitHubにプッシュして、Vercelでデプロイしましょう！🚀

