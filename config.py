"""
設定ファイル
API キーや検索設定などを管理
"""

# Google検索API設定（オプション - より高精度な検索を行う場合）
GOOGLE_API_KEY = ""  # Google Custom Search API キー
GOOGLE_CSE_ID = ""   # Google Custom Search Engine ID

# 検索設定
MAX_SEARCH_RESULTS = 10  # 各検索での最大結果数
SEARCH_TIMEOUT = 30      # 検索タイムアウト（秒）

# SNS検索設定
FACEBOOK_SEARCH_ENABLED = True
TWITTER_SEARCH_ENABLED = True

# 出力設定
OUTPUT_DIR = "output"
OUTPUT_FILENAME = "sales_leads_{timestamp}.csv"

# ユーザーエージェント
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# リクエスト間隔（秒） - サーバーに負荷をかけないため
REQUEST_DELAY = 2

