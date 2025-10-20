"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 環境変数を設定
os.environ['USE_MEMORY_DB'] = 'true'

try:
    # FastAPIアプリをインポート
    from app import app
    from mangum import Mangum
    
    # Vercel用ハンドラー
    handler = Mangum(app, lifespan="off")
except Exception as e:
    print(f"Error loading app: {e}")
    import traceback
    traceback.print_exc()
    
    # フォールバックハンドラー
    def handler(event, context):
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }

