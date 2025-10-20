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

class Database:
    def __init__(self, db_url: str = "sqlite:///./sales_bot.db"):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """セッションを取得"""
        return self.SessionLocal()
    
    def create_search(self, conditions: str, num_companies: int):
        """新しい検索を作成"""
        session = self.get_session()
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
    
    def update_search_status(self, search_id: int, status: str, results=None, error_message=None):
        """検索ステータスを更新"""
        session = self.get_session()
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
    
    def get_search(self, search_id: int):
        """検索を取得"""
        session = self.get_session()
        try:
            return session.query(SearchHistory).filter(SearchHistory.id == search_id).first()
        finally:
            session.close()
    
    def get_all_searches(self, limit: int = 50):
        """すべての検索を取得"""
        session = self.get_session()
        try:
            return session.query(SearchHistory).order_by(SearchHistory.created_at.desc()).limit(limit).all()
        finally:
            session.close()

