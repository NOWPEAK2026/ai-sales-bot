"""
SNSアカウント検索モジュール
Facebook、X（旧Twitter）アカウントを検索・特定する
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, Optional
from config import USER_AGENT, REQUEST_DELAY, FACEBOOK_SEARCH_ENABLED, TWITTER_SEARCH_ENABLED


class SNSFinder:
    def __init__(self):
        self.headers = {
            'User-Agent': USER_AGENT
        }
    
    def find_sns_accounts(self, keyman_name: str, company_name: str, position: str) -> Dict[str, str]:
        """
        キーマンのSNSアカウントを検索
        
        Args:
            keyman_name: キーマンの氏名
            company_name: 企業名
            position: 役職
        
        Returns:
            SNSアカウントURLの辞書
        """
        print(f"    SNS検索中: {keyman_name} ({company_name})")
        
        sns_accounts = {
            'Facebook': 'なし',
            'X（旧Twitter）': 'なし'
        }
        
        # Facebookアカウント検索
        if FACEBOOK_SEARCH_ENABLED:
            facebook_url = self._find_facebook(keyman_name, company_name)
            if facebook_url:
                sns_accounts['Facebook'] = facebook_url
        
        # X（旧Twitter）アカウント検索
        if TWITTER_SEARCH_ENABLED:
            twitter_url = self._find_twitter(keyman_name, company_name)
            if twitter_url:
                sns_accounts['X（旧Twitter）'] = twitter_url
        
        time.sleep(REQUEST_DELAY)
        
        return sns_accounts
    
    def _find_facebook(self, name: str, company: str) -> Optional[str]:
        """
        Facebookアカウントを検索
        """
        try:
            # Google検索でFacebookプロフィールを検索
            query = f"{name} {company} site:facebook.com"
            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Facebookのリンクを抽出
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'facebook.com' in href:
                        # URLをクリーンアップ
                        facebook_url = self._extract_clean_url(href, 'facebook.com')
                        if facebook_url and self._is_valid_facebook_url(facebook_url):
                            return facebook_url
        
        except Exception as e:
            print(f"      Facebook検索エラー: {e}")
        
        return None
    
    def _find_twitter(self, name: str, company: str) -> Optional[str]:
        """
        X（旧Twitter）アカウントを検索
        """
        try:
            # Google検索でTwitterプロフィールを検索
            query = f"{name} {company} site:twitter.com OR site:x.com"
            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # TwitterまたはX.comのリンクを抽出
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'twitter.com' in href or 'x.com' in href:
                        # URLをクリーンアップ
                        twitter_url = self._extract_clean_url(href, ['twitter.com', 'x.com'])
                        if twitter_url and self._is_valid_twitter_url(twitter_url):
                            return twitter_url
        
        except Exception as e:
            print(f"      X検索エラー: {e}")
        
        return None
    
    def _extract_clean_url(self, url: str, domains) -> Optional[str]:
        """
        URLからクリーンなURLを抽出
        """
        if isinstance(domains, str):
            domains = [domains]
        
        # Google検索のリダイレクトURLから実際のURLを抽出
        if '/url?q=' in url:
            match = re.search(r'/url\?q=([^&]+)', url)
            if match:
                url = match.group(1)
        
        # URLデコード
        try:
            from urllib.parse import unquote
            url = unquote(url)
        except:
            pass
        
        # ドメインチェック
        for domain in domains:
            if domain in url:
                # クエリパラメータを削除
                clean_url = url.split('?')[0].split('#')[0]
                return clean_url
        
        return None
    
    def _is_valid_facebook_url(self, url: str) -> bool:
        """
        有効なFacebook URLかどうかを判定
        """
        # 個人プロフィールまたはページのURLパターン
        patterns = [
            r'facebook\.com/[a-zA-Z0-9._-]+/?$',
            r'facebook\.com/profile\.php\?id=\d+',
            r'facebook\.com/people/[^/]+/\d+'
        ]
        
        for pattern in patterns:
            if re.search(pattern, url):
                return True
        
        return False
    
    def _is_valid_twitter_url(self, url: str) -> bool:
        """
        有効なX（Twitter）URLかどうかを判定
        """
        # ユーザープロフィールのURLパターン
        patterns = [
            r'(twitter\.com|x\.com)/[a-zA-Z0-9_]+/?$'
        ]
        
        for pattern in patterns:
            if re.search(pattern, url):
                # statusやhashtagなどのページは除外
                if '/status/' not in url and '/hashtag/' not in url:
                    return True
        
        return False

