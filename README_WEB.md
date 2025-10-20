# AI営業アポイント自動化BOT - Webサービス版

## 🌐 概要

コマンドラインツールをWebアプリケーションに拡張したバージョンです。
ブラウザから簡単に使用でき、複数ユーザーでの利用や検索履歴の管理が可能です。

## ✨ Webサービスの特徴

### 1. **モダンなWebインターフェース**
- 直感的で美しいUI/UX
- レスポンシブデザイン（スマホ・タブレット対応）
- リアルタイムで検索進捗を表示

### 2. **非同期処理**
- バックグラウンドで検索を実行
- 検索中もページを離れずに他の作業が可能
- 複数の検索を同時に実行可能

### 3. **検索履歴管理**
- 過去の検索結果を保存
- いつでも過去の結果を参照可能
- データベースで永続化

### 4. **簡単エクスポート**
- ワンクリックでCSV/TSV/JSONダウンロード
- クリップボードへの直接コピー
- Excelに直接貼り付け可能

### 5. **RESTful API**
- プログラムから利用可能なAPI
- 自動生成されたAPIドキュメント
- 他システムとの連携が容易

## 🏗️ アーキテクチャ

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │ HTTP/REST API
┌──────▼──────┐
│   FastAPI   │
│  (Backend)  │
└──────┬──────┘
       │
    ┌──▼──┐
    │ DB  │ ← 検索履歴・結果を保存
    └─────┘

バックグラウンドタスク:
- 企業検索
- 役員・責任者特定
```

## 📦 技術スタック

- **バックエンド**: FastAPI (Python)
- **データベース**: SQLite (開発用) / PostgreSQL (本番推奨)
- **フロントエンド**: HTML5 + CSS3 + Vanilla JavaScript
- **非同期処理**: FastAPI BackgroundTasks
- **API文書**: Swagger UI (自動生成)

## 🚀 セットアップ

### 1. 依存パッケージのインストール

```bash
cd ai-sales-bot
pip install -r requirements_web.txt
```

### 2. サーバーの起動

```bash
python app.py
```

または

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 3. ブラウザでアクセス

- **メインアプリ**: http://localhost:8000
- **API文書**: http://localhost:8000/docs
- **代替API文書**: http://localhost:8000/redoc

## 📖 使い方

### Webインターフェースから

1. ブラウザで http://localhost:8000 を開く
2. 検索条件を入力
   - 企業リストアップ条件
   - 企業数
   - キーマン数/企業
3. 「検索を開始」ボタンをクリック
4. 検索の進捗がリアルタイムで表示される
5. 完了したら結果が表示される
6. エクスポートボタンで結果をダウンロード

### APIから

#### 検索を開始

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "conditions": "SaaS スタートアップ 東京",
    "num_companies": 5,
    "max_keymen": 5
  }'
```

レスポンス:
```json
{
  "search_id": 1,
  "message": "検索を開始しました。しばらくお待ちください。"
}
```

#### 検索ステータスを確認

```bash
curl "http://localhost:8000/api/search/1"
```

レスポンス:
```json
{
  "search_id": 1,
  "status": "completed",
  "results": [...],
  "created_at": "2025-10-20T14:30:00"
}
```

#### 結果をエクスポート

```bash
# CSV形式でダウンロード
curl "http://localhost:8000/api/export/1/csv" -o results.csv

# TSV形式でダウンロード
curl "http://localhost:8000/api/export/1/tsv" -o results.tsv

# JSON形式でダウンロード
curl "http://localhost:8000/api/export/1/json" -o results.json
```

#### 検索履歴を取得

```bash
curl "http://localhost:8000/api/history?limit=20"
```

## 🎨 UIのカスタマイズ

`templates/index.html` のCSSセクションを編集することで、デザインをカスタマイズできます。

### カラーテーマの変更

```css
/* グラデーション背景 */
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* プライマリカラー */
.btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

## 🔒 セキュリティ

### 本番環境での推奨設定

1. **HTTPS通信**
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 443 --ssl-keyfile key.pem --ssl-certfile cert.pem
   ```

2. **CORS設定**
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

3. **認証の追加**
   - OAuth2
   - JWT トークン
   - API キー

4. **レート制限**
   ```bash
   pip install slowapi
   ```

## 🗄️ データベース

### SQLiteからPostgreSQLへの移行

本番環境ではPostgreSQLの使用を推奨します。

1. PostgreSQLをインストール

2. `database.py` を更新:
   ```python
   DATABASE_URL = "postgresql://user:password@localhost/sales_bot"
   ```

3. 依存関係を追加:
   ```bash
   pip install psycopg2-binary
   ```

## 📊 モニタリング

### ログ設定

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### ヘルスチェック

```bash
curl http://localhost:8000/health
```

## 🐳 Dockerでのデプロイ

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_web.txt .
RUN pip install --no-cache-dir -r requirements_web.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./:/app
    environment:
      - DATABASE_URL=postgresql://user:pass@db/sales_bot
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=sales_bot
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

起動:
```bash
docker-compose up -d
```

## 🌍 本番デプロイ

### おすすめのデプロイ先

1. **Heroku**
   - 簡単デプロイ
   - 無料プランあり

2. **Railway**
   - モダンなUI
   - GitHubと連携

3. **AWS / GCP / Azure**
   - スケーラブル
   - 本格的な運用

4. **Vercel / Netlify**
   - フロントエンドに最適
   - バックエンドは別サーバー

### Herokuへのデプロイ例

1. `Procfile` を作成:
   ```
   web: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

2. デプロイ:
   ```bash
   heroku create your-app-name
   git push heroku main
   heroku open
   ```

## 🔧 トラブルシューティング

### ポート8000が使用中の場合

```bash
# 別のポートを使用
uvicorn app:app --port 8080
```

### データベースエラー

```bash
# データベースファイルを削除して再作成
rm sales_bot.db
python app.py
```

### パッケージエラー

```bash
# 依存関係を再インストール
pip install --upgrade -r requirements_web.txt
```

## 📈 今後の拡張案

- [ ] ユーザー認証・ログイン機能
- [ ] チーム機能（複数ユーザーでの共有）
- [ ] 検索結果のフィルタリング・ソート
- [ ] グラフ・チャートでの可視化
- [ ] メール通知機能
- [ ] Slack/Teams連携
- [ ] AI分析・レコメンデーション
- [ ] 自動営業メール作成

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. ログを確認
2. APIドキュメント（/docs）を参照
3. データベースの状態を確認

## 📄 ライセンス

このプロジェクトは教育・研究目的で作成されています。

