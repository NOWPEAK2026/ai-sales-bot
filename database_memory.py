"""
メモリ内データストア（Vercel Serverless Functions用）
"""
from datetime import datetime
from typing import List, Dict, Optional

# メモリ内データストア
_searches = {}
_search_counter = 0


def init_db():
    """データベースの初期化（何もしない）"""
    pass


def create_search(conditions: str, num_companies: int) -> int:
    """新しい検索を作成"""
    global _search_counter
    _search_counter += 1
    
    search_id = _search_counter
    _searches[search_id] = {
        'id': search_id,
        'conditions': conditions,
        'num_companies': num_companies,
        'status': 'pending',
        'results': None,
        'error_message': None,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    return search_id


def get_search(search_id: int) -> Optional[Dict]:
    """検索情報を取得"""
    return _searches.get(search_id)


def update_search_status(search_id: int, status: str, 
                        results: Optional[List[Dict]] = None, 
                        error_message: Optional[str] = None):
    """検索ステータスを更新"""
    if search_id in _searches:
        _searches[search_id]['status'] = status
        _searches[search_id]['updated_at'] = datetime.now().isoformat()
        
        if results is not None:
            _searches[search_id]['results'] = results
        
        if error_message is not None:
            _searches[search_id]['error_message'] = error_message


def list_searches(limit: int = 10) -> List[Dict]:
    """検索一覧を取得"""
    all_searches = sorted(_searches.values(), 
                         key=lambda x: x['created_at'], 
                         reverse=True)
    return all_searches[:limit]


def get_all_searches(limit: int = 10) -> List[Dict]:
    """検索一覧を取得（別名）"""
    return list_searches(limit)

