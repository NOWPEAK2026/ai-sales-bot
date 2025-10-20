"""
データベースモジュール
検索履歴と結果を保存
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class SearchHistory(Base):
    """検索履歴テーブル"""
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    search_conditions = Column(String(500))
    num_companies = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    results = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

# グローバルなデータベースインスタンス
_db_instance = None

def init_db(db_url: str = "sqlite:///./sales_bot.db"):
    """データベースを初期化"""
    global _db_instance
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    _db_instance = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def _get_session():
    """セッションを取得"""
    if _db_instance is None:
        init_db()
    return _db_instance()

def create_search(conditions: str, num_companies: int):
    """新しい検索を作成"""
    session = _get_session()
    try:
        search = SearchHistory(
            search_conditions=conditions,
            num_companies=num_companies,
            status="pending"
        )
        session.add(search)
        session.commit()
        session.refresh(search)
        return search.id
    finally:
        session.close()

def update_search_status(search_id: int, status: str, results=None, error_message=None):
    """検索ステータスを更新"""
    session = _get_session()
    try:
        search = session.query(SearchHistory).filter(SearchHistory.id == search_id).first()
        if search:
            search.status = status
            if results:
                search.results = results
            if error_message:
                search.error_message = error_message
            session.commit()
    finally:
        session.close()

def get_search(search_id: int):
    """検索を取得"""
    session = _get_session()
    try:
        search = session.query(SearchHistory).filter(SearchHistory.id == search_id).first()
        if search:
            return {
                'id': search.id,
                'conditions': search.search_conditions,
                'num_companies': search.num_companies,
                'status': search.status,
                'results': search.results,
                'error_message': search.error_message,
                'created_at': search.created_at.isoformat() if search.created_at else None
            }
        return None
    finally:
        session.close()

def get_all_searches(limit: int = 50):
    """すべての検索を取得"""
    session = _get_session()
    try:
        searches = session.query(SearchHistory).order_by(SearchHistory.created_at.desc()).limit(limit).all()
        return [
            {
                'id': s.id,
                'conditions': s.search_conditions,
                'num_companies': s.num_companies,
                'status': s.status,
                'results': s.results,
                'error_message': s.error_message,
                'created_at': s.created_at.isoformat() if s.created_at else None
            }
            for s in searches
        ]
    finally:
        session.close()

