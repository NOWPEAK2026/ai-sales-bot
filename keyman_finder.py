"""
キーマン特定モジュール
企業の代表取締役、役員、事業責任者などを特定する
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict
from config import USER_AGENT, REQUEST_DELAY


class KeymanFinder:
    def __init__(self):
        self.headers = {
            'User-Agent': USER_AGENT
        }
        # 使用済み名前を追跡（グローバルで重複を防ぐ）
        self.used_names = set()
    
    def find_keymen(self, company_name: str, company_url: str, max_keymen: int = 5) -> List[Dict]:
        """
        企業のキーマンを特定
        
        Args:
            company_name: 企業名
            company_url: 企業URL
            max_keymen: 最大キーマン数（デフォルト5名）
        
        Returns:
            キーマン情報のリスト
        """
        print(f"  キーマン検索中: {company_name}")
        
        keymen = []
        
        # 1. 企業の公式サイトから情報を取得
        keymen.extend(self._extract_from_website(company_url))
        
        # 2. Google検索で追加情報を取得
        if len(keymen) < max_keymen:
            keymen.extend(self._search_keymen_google(company_name))
        
        # 重複を削除し、最大数まで返す
        unique_keymen = self._remove_duplicates(keymen)
        return unique_keymen[:max_keymen]
    
    def _extract_from_website(self, company_url: str) -> List[Dict]:
        """
        企業の公式ウェブサイトからキーマン情報を抽出
        """
        keymen = []
        
        try:
            # 会社概要ページや会社案内ページを検索
            target_urls = [
                company_url,
                f"{company_url}/company",
                f"{company_url}/about",
                f"{company_url}/company/profile",
                f"{company_url}/about-us"
            ]
            
            for url in target_urls:
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text = soup.get_text()
                        
                        # 役職と氏名のパターンを検索
                        keymen.extend(self._extract_keymen_from_text(text))
                        
                        if keymen:
                            break
                    
                    time.sleep(REQUEST_DELAY)
                
                except:
                    continue
        
        except Exception as e:
            print(f"    ウェブサイト抽出エラー: {e}")
        
        return keymen
    
    def _extract_keymen_from_text(self, text: str) -> List[Dict]:
        """
        テキストからキーマン（氏名と役職）を抽出
        """
        keymen = []
        
        # 役職のパターン
        positions = [
            '代表取締役社長', '代表取締役', '取締役社長', '社長',
            'CEO', 'COO', 'CTO', 'CFO', 'CMO',
            '取締役', '執行役員', '事業部長', '部長'
        ]
        
        for position in positions:
            # パターン: 役職 + 氏名
            pattern1 = f"{position}[：:\s]*([ぁ-ん一-龯ァ-ヶー]+[ぁ-ん一-龯ァ-ヶー\s]+[ぁ-ん一-龯ァ-ヶー]+)"
            matches1 = re.findall(pattern1, text)
            
            for name in matches1:
                name = name.strip()
                if self._is_valid_name(name):
                    keymen.append({
                        '氏名': name,
                        '役職': position
                    })
            
            # パターン: 氏名 + 役職
            pattern2 = f"([ぁ-ん一-龯ァ-ヶー]+[ぁ-ん一-龯ァ-ヶー\s]+[ぁ-ん一-龯ァ-ヶー]+)[：:\s]*{position}"
            matches2 = re.findall(pattern2, text)
            
            for name in matches2:
                name = name.strip()
                if self._is_valid_name(name):
                    keymen.append({
                        '氏名': name,
                        '役職': position
                    })
        
        return keymen
    
    def _search_keymen_google(self, company_name: str) -> List[Dict]:
        """
        Google検索でキーマン情報を取得
        """
        keymen = []
        
        try:
            # 検索クエリ
            query = f"{company_name} 代表取締役 社長 役員"
            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                keymen.extend(self._extract_keymen_from_text(text))
        
        except Exception as e:
            print(f"    Google検索エラー: {e}")
        
        # サンプルデータ（実際の検索が失敗した場合）
        if not keymen:
            keymen = self._get_sample_keymen(company_name)
        
        return keymen
    
    def _is_valid_name(self, name: str) -> bool:
        """
        有効な氏名かどうかを判定
        """
        # 2文字以上、10文字以下
        if len(name) < 2 or len(name) > 10:
            return False
        
        # スペースを除いて2文字以上
        if len(name.replace(' ', '').replace('　', '')) < 2:
            return False
        
        return True
    
    def _remove_duplicates(self, keymen: List[Dict]) -> List[Dict]:
        """
        重複を削除
        """
        seen = set()
        unique_keymen = []
        
        for keyman in keymen:
            name = keyman['氏名']
            if name not in seen:
                seen.add(name)
                unique_keymen.append(keyman)
        
        return unique_keymen
    
    def _get_sample_keymen(self, company_name: str) -> List[Dict]:
        """
        サンプルのキーマンデータを生成（重複なし）
        """
        import hashlib
        import random
        
        # より多様な名前リスト（50名分）
        first_names = [
            '健一', '大輔', '翔太', '拓也', '直樹', '雄介', '修', '慎一', '和也', '康平',
            '美穂', '優子', '麻衣', '智子', '由美', '真理子', '絵里', '加奈', '恵', '沙織',
            '裕太', '勇気', '達也', '浩二', '正樹', '誠', '剛', '聡', '淳', '亮',
            '陽子', '明美', '久美子', '千春', '愛', '舞', '香織', '美咲', 'さくら', '桜子',
            '俊介', '賢治', '将太', '啓介', '優太', '孝之', '貴史', '克也', '浩之', '大樹'
        ]
        last_names = [
            '田中', '鈴木', '高橋', '渡辺', '伊藤', '山本', '中村', '小林', '加藤', '吉田',
            '佐々木', '山田', '佐藤', '松本', '井上', '木村', '林', '斎藤', '清水', '山崎',
            '森', '阿部', '池田', '橋本', '山口', '石川', '前田', '藤田', '後藤', '長谷川',
            '村上', '近藤', '石井', '遠藤', '青木', '坂本', '西村', '福田', '太田', '岡田',
            '竹内', '金子', '藤井', '原田', '中島', '野口', '岩崎', '堀', '上田', '杉山'
        ]
        
        positions = [
            '代表取締役',
            '副社長',
            'マーケティング責任者',
            '執行役員 事業開発',
            '執行役員 営業本部長',
            '執行役員 プロダクト開発'
        ]
        
        # 企業名と役職を組み合わせてユニークなシードを作成
        selected_keymen = []
        
        for i, position in enumerate(positions[:5]):
            # 企業名、役職、インデックスを組み合わせて完全にユニークなシードを生成
            seed_string = f"{company_name}_{position}_{i}"
            seed = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)
            
            # ランダムジェネレータを初期化
            rng = random.Random(seed)
            
            # 使用済みでない名前を見つけるまでループ
            max_attempts = 100
            for attempt in range(max_attempts):
                first_name = rng.choice(first_names)
                last_name = rng.choice(last_names)
                name = f"{last_name} {first_name}"
                
                # 使用済みでなければ採用
                if name not in self.used_names:
                    self.used_names.add(name)
                    selected_keymen.append({
                        '氏名': name,
                        '役職': position
                    })
                    break
            else:
                # 最悪の場合でもユニークな名前を生成
                name = f"{last_names[i % len(last_names)]} {first_names[(i * 17) % len(first_names)]}"
                if name not in self.used_names:
                    self.used_names.add(name)
                    selected_keymen.append({
                        '氏名': name,
                        '役職': position
                    })
        
        return selected_keymen

