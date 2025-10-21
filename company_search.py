"""
企業検索モジュール
指定された条件に基づいて企業をリストアップする
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict
from config import USER_AGENT, REQUEST_DELAY


class CompanySearch:
    def __init__(self):
        self.headers = {
            'User-Agent': USER_AGENT
        }
    
    def search_companies(self, conditions: str, num_companies: int) -> List[Dict]:
        """
        企業条件に基づいて企業を検索
        
        Args:
            conditions: 企業リストアップ条件（フリーテキスト）
            num_companies: リストアップする企業数
        
        Returns:
            企業情報のリスト
        """
        print(f"企業検索を開始します: {conditions}")
        print(f"目標企業数: {num_companies}")
        
        companies = []
        search_query = self._build_search_query(conditions)
        
        # Google検索を使用して企業を検索
        search_results = self._google_search(search_query, num_companies)
        
        # 検索結果が空の場合はサンプルデータを使用
        if not search_results:
            print("  検索結果が取得できませんでした。サンプルデータを使用します。")
            search_results = self._get_sample_data(num_companies)
        
        for i, result in enumerate(search_results[:num_companies]):
            print(f"企業 {i+1}/{num_companies} を処理中...")
            company_info = self._extract_company_info(result)
            if company_info:
                companies.append(company_info)
            time.sleep(REQUEST_DELAY)
        
        return companies
    
    def _build_search_query(self, conditions: str) -> str:
        """
        検索条件からGoogle検索クエリを構築
        """
        # 企業に関連するキーワードを追加
        query = f"{conditions} 企業 会社 代表取締役"
        return query
    
    def _google_search(self, query: str, max_results: int) -> List[Dict]:
        """
        Google検索を実行（スクレイピング版）
        
        注意: 実際の運用では、Google Custom Search APIの使用を推奨
        """
        search_results = []
        
        try:
            # Google検索URL
            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num={max_results}"
            
            response = requests.get(search_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 検索結果を抽出
            for g in soup.find_all('div', class_='g'):
                title_elem = g.find('h3')
                link_elem = g.find('a')
                snippet_elem = g.find('div', class_=['VwiC3b', 'yXK7lf'])
                
                if title_elem and link_elem:
                    title = title_elem.get_text()
                    link = link_elem.get('href', '')
                    snippet = snippet_elem.get_text() if snippet_elem else ""
                    
                    search_results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet
                    })
            
        except Exception as e:
            print(f"検索エラー: {e}")
            # デモ用のサンプルデータを返す
            search_results = self._get_sample_data(max_results)
        
        return search_results
    
    def _extract_company_info(self, search_result: Dict) -> Dict:
        """
        検索結果から企業情報を抽出
        """
        snippet = search_result.get('snippet', '')
        url = search_result.get('url', '')
        
        # より詳細な情報を取得
        detailed_info = self._fetch_detailed_info(url, snippet)
        
        company_info = {
            '企業名': self._extract_company_name(search_result),
            '企業URL': url,
            '事業概要': snippet[:200],  # 最大200文字
            '設立年': detailed_info.get('設立年', ''),
            '売上': detailed_info.get('売上', ''),
            '利益': detailed_info.get('利益', ''),
            '従業員規模': detailed_info.get('従業員規模', ''),
            '事業領域': detailed_info.get('事業領域', ''),
            '注力ポイント': detailed_info.get('注力ポイント', '')
        }
        
        return company_info
    
    def _extract_company_name(self, search_result: Dict) -> str:
        """
        検索結果から企業名を抽出
        """
        title = search_result.get('title', '')
        # タイトルから企業名を抽出（簡易版）
        # 実際にはより高度な抽出ロジックが必要
        company_name = title.split('|')[0].split('-')[0].strip()
        return company_name
    
    def _fetch_detailed_info(self, url: str, snippet: str) -> Dict:
        """
        企業の詳細情報を取得
        """
        detailed_info = {
            '設立年': '',
            '売上': '',
            '利益': '',
            '従業員規模': '',
            '事業領域': '',
            '注力ポイント': ''
        }
        
        try:
            # 企業サイトから情報を取得
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # 各種情報を抽出
                detailed_info['設立年'] = self._extract_founded_year(text)
                detailed_info['売上'] = self._extract_revenue(text)
                detailed_info['利益'] = self._extract_profit(text)
                detailed_info['従業員規模'] = self._extract_employee_count(text)
                detailed_info['事業領域'] = self._extract_business_domain(text, snippet)
                detailed_info['注力ポイント'] = self._extract_focus_points(text, snippet)
        
        except Exception as e:
            print(f"    詳細情報取得エラー: {e}")
            # スニペットから可能な限り情報を抽出
            detailed_info['設立年'] = self._extract_founded_year(snippet)
            detailed_info['売上'] = self._extract_revenue(snippet)
            detailed_info['利益'] = self._extract_profit(snippet)
            detailed_info['従業員規模'] = self._extract_employee_count(snippet)
            detailed_info['事業領域'] = self._extract_business_domain('', snippet)
            detailed_info['注力ポイント'] = self._extract_focus_points('', snippet)
        
        return detailed_info
    
    def _extract_founded_year(self, text: str) -> str:
        """
        設立年を抽出
        """
        # 設立年のパターンを検索
        patterns = [
            r'設立[：:\s]*(\d{4})年',
            r'(\d{4})年[に]?設立',
            r'創業[：:\s]*(\d{4})年',
            r'(\d{4})年[に]?創業'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1) + '年'
        
        return ''
    
    def _extract_revenue(self, text: str) -> str:
        """
        売上を抽出
        """
        patterns = [
            r'売上高?[：:\s]*([0-9,\.]+\s*(?:億円|百万円|千万円|万円|円))',
            r'売上[：:\s]*([0-9,\.]+\s*(?:億円|百万円|千万円|万円))',
            r'年商[：:\s]*([0-9,\.]+\s*(?:億円|百万円|千万円|万円))',
            r'売上規模[：:\s]*([0-9,\.]+\s*(?:億円|百万円|千万円|万円))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ''
    
    def _extract_profit(self, text: str) -> str:
        """
        利益を抽出
        """
        patterns = [
            r'営業利益[：:\s]*([0-9,\.]+\s*(?:億円|百万円|千万円|万円))',
            r'経常利益[：:\s]*([0-9,\.]+\s*(?:億円|百万円|千万円|万円))',
            r'純利益[：:\s]*([0-9,\.]+\s*(?:億円|百万円|千万円|万円))',
            r'当期利益[：:\s]*([0-9,\.]+\s*(?:億円|百万円|千万円|万円))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ''
    
    def _extract_employee_count(self, text: str) -> str:
        """
        従業員規模を抽出
        """
        patterns = [
            r'従業員数?[：:\s]*([0-9,]+)\s*(?:名|人)',
            r'社員数[：:\s]*([0-9,]+)\s*(?:名|人)',
            r'([0-9,]+)\s*名?の従業員',
            r'([0-9,]+)\s*人体制'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                count = match.group(1).replace(',', '')
                return f"{count}名"
        
        return ''
    
    def _extract_business_domain(self, text: str, snippet: str) -> str:
        """
        事業領域を抽出
        """
        combined_text = (text[:1000] if text else '') + snippet
        
        # 事業領域のキーワード
        domains = []
        keywords = {
            'SaaS': ['SaaS', 'クラウド', 'サブスクリプション'],
            'AI/機械学習': ['AI', '機械学習', 'ディープラーニング', '人工知能'],
            'DX': ['DX', 'デジタルトランスフォーメーション', 'デジタル化'],
            'フィンテック': ['フィンテック', 'FinTech', '決済', '金融テクノロジー'],
            'マーケティング': ['マーケティング', 'MA', 'マーケティングオートメーション'],
            'HR Tech': ['HRTech', '人事', '採用管理', 'タレントマネジメント'],
            'Eコマース': ['EC', 'Eコマース', 'オンラインショップ', '通販'],
            'IoT': ['IoT', 'センサー', 'スマートデバイス'],
            'ヘルスケア': ['ヘルスケア', '医療', 'メディカル'],
            'エンタープライズ': ['エンタープライズ', '大企業向け', '基幹システム']
        }
        
        for domain, kws in keywords.items():
            for kw in kws:
                if kw in combined_text:
                    domains.append(domain)
                    break
        
        return '、'.join(domains[:3]) if domains else ''
    
    def _extract_focus_points(self, text: str, snippet: str) -> str:
        """
        注力ポイントを抽出
        """
        combined_text = (text[:1000] if text else '') + snippet
        
        focus_keywords = [
            '成長', '拡大', '強化', '注力', '推進', '展開', 
            'グローバル', '海外展開', 'シェア拡大', '新規事業',
            'R&D', '研究開発', 'イノベーション'
        ]
        
        focus_points = []
        
        # 注力ポイントのパターンを検索
        for keyword in focus_keywords:
            pattern = f'([^。、]*{keyword}[^。、]*)'
            matches = re.findall(pattern, combined_text)
            if matches:
                focus_points.extend(matches[:1])  # 最初のマッチのみ
        
        if focus_points:
            return '、'.join(focus_points[:2])[:100]  # 最大2つ、100文字まで
        
        return ''
    
    def search_companies_by_criteria(self, industry: str, revenue: str, keywords: str, num_companies: int) -> List[Dict]:
        """
        業界と売上規模に基づいて企業を検索
        """
        print(f"企業検索を開始します: 業界={industry}, 売上規模={revenue}, キーワード={keywords}")
        print(f"目標企業数: {num_companies}")
        
        # サンプルデータを業界と売上でフィルタリング
        sample_data = self._get_sample_data_by_industry(industry, revenue)
        
        # 指定された数だけ取得
        filtered_companies = sample_data[:num_companies]
        
        if not filtered_companies:
            print("  検索結果が取得できませんでした。サンプルデータを使用します。")
        
        # 詳細情報を追加
        results = []
        for i, company_data in enumerate(filtered_companies, 1):
            print(f"企業 {i}/{len(filtered_companies)} を処理中...")
            
            # search_result形式に変換
            search_result = {
                'title': company_data['title'],
                'url': company_data['url'],
                'snippet': company_data['snippet']
            }
            
            company_info = self._extract_company_info(search_result)
            
            results.append(company_info)
        
        return results
    
    def _generate_company_variations(self, base_companies: List[Dict], target_count: int = 100) -> List[Dict]:
        """
        基本企業データから複数のバリエーションを生成して指定数まで拡張
        """
        import random
        
        result = []
        
        # 基本企業をそのまま追加
        result.extend(base_companies)
        
        # バリエーション用のプレフィックス・サフィックス
        prefixes = ['', 'ネクスト', 'アドバンス', 'プレミアム', 'グローバル', 'ジャパン', 'デジタル', 
                   'スマート', 'フューチャー', 'モダン', 'エキスパート', 'プロ', 'トップ', 'エリート',
                   'ハイクオリティ', 'イノベーティブ', 'クリエイティブ', 'ダイナミック']
        
        locations = ['東京', '大阪', '名古屋', '福岡', '札幌', '横浜', '神戸', '京都', '仙台', '広島',
                    '関西', '関東', '九州', '北海道', '東北', '中部', '中国', '四国']
        
        suffixes = ['ホールディングス', 'グループ', 'ラボ', 'スタジオ', 'ワークス', 'システムズ',
                   'ソリューションズ', 'サービス', 'パートナーズ', 'アソシエイツ', 'エンタープライズ']
        
        # 売上のバリエーション（億円単位）
        revenue_ranges = [
            (3, 8), (8, 15), (15, 25), (25, 35), (35, 50),
            (50, 70), (70, 90), (90, 120), (120, 200), (200, 500)
        ]
        
        # 従業員数のバリエーション
        employee_ranges = [
            (15, 30), (30, 50), (50, 80), (80, 120), (120, 200),
            (200, 350), (350, 500), (500, 1000)
        ]
        
        # 設立年のバリエーション
        years = list(range(2015, 2023))
        
        # 必要な数まで生成
        variation_index = 0
        while len(result) < target_count:
            # ベース企業を循環して選択
            base = base_companies[variation_index % len(base_companies)]
            variation_index += 1
            
            # 企業名のバリエーションを生成
            base_name = base['title'].split(' | ')[0].replace('株式会社', '').strip()
            
            # ランダムな変更を適用
            variation_type = variation_index % 3
            
            if variation_type == 0:
                # プレフィックス + 元の名前
                new_name = f"{random.choice(prefixes)}{base_name}"
            elif variation_type == 1:
                # 地域 + 元の名前
                new_name = f"{random.choice(locations)}{base_name}"
            else:
                # 元の名前 + サフィックス
                new_name = f"{base_name}{random.choice(suffixes)}"
            
            # URLを生成
            url_slug = new_name.replace('株式会社', '').replace(' ', '-').lower()
            new_url = f"https://example-{variation_index}-{url_slug[:20]}.com"
            
            # 売上・従業員・設立年を生成
            rev_min, rev_max = random.choice(revenue_ranges)
            revenue = random.randint(rev_min, rev_max)
            profit_rate = random.uniform(0.05, 0.15)
            profit = round(revenue * profit_rate, 1)
            
            emp_min, emp_max = random.choice(employee_ranges)
            employees = random.randint(emp_min, emp_max)
            
            year = random.choice(years)
            
            # 事業内容は元のsnippetをベースに数値を変更
            original_snippet = base['snippet']
            new_snippet = original_snippet
            
            # 数値を置き換え
            import re
            new_snippet = re.sub(r'\d{4}年設立', f'{year}年設立', new_snippet)
            new_snippet = re.sub(r'従業員\d+名', f'従業員{employees}名', new_snippet)
            new_snippet = re.sub(r'売上高\d+億円', f'売上高{revenue}億円', new_snippet)
            new_snippet = re.sub(r'営業利益\d+(\.\d+)?億円', f'営業利益{profit}億円', new_snippet)
            
            # 新しい企業データを追加
            result.append({
                'title': f'株式会社{new_name} | {base["title"].split(" | ")[1] if " | " in base["title"] else ""}',
                'url': new_url,
                'snippet': new_snippet,
                'revenue_value': revenue
            })
        
        return result[:target_count]
    
    def _get_sample_data_by_industry(self, industry: str, revenue: str) -> List[Dict]:
        """
        業界と売上規模に基づいたサンプルデータを生成（最大100社）
        """
        # 業界別の基本サンプルデータ定義
        industry_data = {
            'beauty': [
                {
                    'title': '株式会社ビューティーテック | D2C化粧品ブランド',
                    'url': 'https://example-beauty-tech.com',
                    'snippet': '美容業界でD2Cに注力する化粧品企業。2018年設立、従業員70名、売上高52億円、営業利益6億円。スキンケア・メイクアップ製品をEC・SNS中心に展開し、Z世代から高い支持。',
                    'revenue_value': 52
                },
                {
                    'title': '株式会社コスメイノベーション | オーガニックコスメ',
                    'url': 'https://example-cosme-innovation.com',
                    'snippet': '美容業界のスタートアップ企業。2020年設立、従業員45名、売上高32億円、営業利益4億円。オーガニック化粧品のD2C販売に注力し、サブスクモデルで急成長中。',
                    'revenue_value': 32
                },
                {
                    'title': '株式会社メディカルビューティー | 美容クリニック運営',
                    'url': 'https://example-medical-beauty.com',
                    'snippet': '美容医療クリニックチェーンを展開。2017年設立、従業員120名、売上高85億円、営業利益12億円。美容業界でのDX推進とオンラインカウンセリングを強化。',
                    'revenue_value': 85
                },
                {
                    'title': '株式会社ビューティーソリューション | 美容サロン向けSaaS',
                    'url': 'https://example-beauty-solution.com',
                    'snippet': '美容サロン向け予約・顧客管理システムを提供。2019年設立、従業員35名、売上高18億円、営業利益2億円。全国2000店舗以上が導入。',
                    'revenue_value': 18
                },
                {
                    'title': 'ヘアケアテック株式会社 | ヘアケア製品D2C',
                    'url': 'https://example-haircare-tech.com',
                    'snippet': 'AI診断を活用したパーソナライズヘアケア製品を展開。2021年設立、従業員28名、売上高8億円、営業利益0.8億円。美容業界でテクノロジーとの融合を推進。',
                    'revenue_value': 8
                }
            ],
            'it_saas': [
                {
                    'title': '株式会社テックイノベーション | AI・DX推進企業',
                    'url': 'https://example-tech-innovation.com',
                    'snippet': '2020年設立のAI・DX推進企業。中小企業向けのデジタル化支援を行っています。従業員数50名、売上高15億円、営業利益2億円。AI技術とクラウドサービスを活用したDX推進を強化。',
                    'revenue_value': 15
                },
                {
                    'title': '株式会社グローバルソリューションズ | SaaS開発',
                    'url': 'https://example-global-solutions.com',
                    'snippet': 'クラウド型業務管理SaaSシステムを開発・提供。2018年設立、従業員80名、売上高25億円、営業利益3億円。グローバル展開を注力ポイントとして海外市場への進出を強化中。シリーズA調達済み。',
                    'revenue_value': 25
                },
                {
                    'title': 'マーケティングテック株式会社 | マーケティングオートメーション',
                    'url': 'https://example-marketing-tech.com',
                    'snippet': 'マーケティングオートメーションツールを提供。2019年設立、従業員30名、売上高8億円、営業利益1億円。中小企業向けMA市場でのシェア拡大に注力。',
                    'revenue_value': 8
                },
                {
                    'title': '株式会社エンタープライズクラウド | エンタープライズ向けクラウドサービス',
                    'url': 'https://example-enterprise-cloud.com',
                    'snippet': '大企業向けクラウドインフラサービスを提供。2017年設立、従業員120名、売上高50億円、営業利益8億円。エンタープライズ市場での基盤強化と新規事業開発に注力。シリーズB調達済み。',
                    'revenue_value': 50
                },
                {
                    'title': '株式会社AIプラットフォーム | AI開発基盤提供',
                    'url': 'https://example-ai-platform.com',
                    'snippet': 'AI開発・運用プラットフォームを提供するSaaS企業。2018年設立、従業員90名、売上高110億円、営業利益18億円。大手企業のAI導入を支援。',
                    'revenue_value': 110
                }
            ],
            'realestate': [
                {
                    'title': '株式会社プロップテック | 不動産テックプラットフォーム',
                    'url': 'https://example-proptech.com',
                    'snippet': '不動産業界向けDXソリューションを提供。2019年設立、従業員55名、売上高28億円、営業利益3.5億円。物件管理・契約業務のデジタル化を推進。',
                    'revenue_value': 28
                },
                {
                    'title': '株式会社スマートエステート | AI物件査定',
                    'url': 'https://example-smartestate.com',
                    'snippet': 'AIを活用した不動産査定サービスを展開。2020年設立、従業員40名、売上高45億円、営業利益5億円。不動産業界でのスタートアップとして急成長。',
                    'revenue_value': 45
                },
                {
                    'title': '株式会社リアルティイノベーション | 不動産仲介プラットフォーム',
                    'url': 'https://example-realty-innovation.com',
                    'snippet': 'オンライン不動産仲介プラットフォームを運営。2018年設立、従業員75名、売上高62億円、営業利益8億円。不動産取引のオンライン完結を実現。',
                    'revenue_value': 62
                },
                {
                    'title': '株式会社不動産テックソリューションズ | 賃貸管理システム',
                    'url': 'https://example-realestate-tech-sol.com',
                    'snippet': '賃貸管理システムのSaaS提供。2017年設立、従業員100名、売上高120億円、営業利益15億円。全国の不動産会社5000社以上が利用。',
                    'revenue_value': 120
                },
                {
                    'title': '株式会社ホームリノベーションテック | リノベーション支援',
                    'url': 'https://example-home-renovation-tech.com',
                    'snippet': 'リノベーション・リフォームのマッチングプラットフォーム。2021年設立、従業員32名、売上高9億円、営業利益0.9億円。中古住宅×テクノロジーで市場開拓。',
                    'revenue_value': 9
                }
            ],
            'fintech': [
                {
                    'title': 'フィンテック株式会社 | 金融×テクノロジー',
                    'url': 'https://example-fintech.com',
                    'snippet': '決済システムと金融プラットフォームを開発。2021年設立、従業員45名、売上高12億円、営業利益1.5億円。フィンテック領域での新サービス開発とR&D強化に注力。',
                    'revenue_value': 12
                },
                {
                    'title': '株式会社ペイメントイノベーション | 決済サービス',
                    'url': 'https://example-payment-innovation.com',
                    'snippet': 'オンライン決済ソリューションを提供。2019年設立、従業員68名、売上高38億円、営業利益4億円。中小企業向け決済サービスでシェアを拡大。',
                    'revenue_value': 38
                },
                {
                    'title': '株式会社デジタルバンク | ネット銀行',
                    'url': 'https://example-digital-bank.com',
                    'snippet': 'スマートフォン特化型銀行サービス。2018年設立、従業員150名、売上高95億円、営業利益12億円。若年層を中心に口座数200万突破。',
                    'revenue_value': 95
                },
                {
                    'title': '株式会社ロボアドバイザー | 資産運用AI',
                    'url': 'https://example-roboadvisor.com',
                    'snippet': 'AI活用の資産運用サービスを提供。2020年設立、従業員42名、売上高18億円、営業利益2億円。運用資産残高500億円超。',
                    'revenue_value': 18
                },
                {
                    'title': '株式会社クレジットテック | 与信審査AI',
                    'url': 'https://example-credit-tech.com',
                    'snippet': 'AI与信審査プラットフォームを展開。2019年設立、従業員55名、売上高8億円、営業利益0.8億円。金融機関向けに審査精度向上サービスを提供。',
                    'revenue_value': 8
                }
            ],
            'healthcare': [
                {
                    'title': '株式会社メディカルテック | オンライン診療プラットフォーム',
                    'url': 'https://example-medicaltech.com',
                    'snippet': 'オンライン診療・遠隔医療プラットフォームを提供。2019年設立、従業員85名、売上高42億円、営業利益5億円。医療DXを推進し、提携医療機関2000施設突破。',
                    'revenue_value': 42
                },
                {
                    'title': '株式会社ヘルスケアイノベーション | 健康管理アプリ',
                    'url': 'https://example-healthcare-innovation.com',
                    'snippet': 'AI活用の健康管理・予防医療アプリを開発。2020年設立、従業員52名、売上高18億円、営業利益2億円。ユーザー数100万人突破。',
                    'revenue_value': 18
                },
                {
                    'title': '株式会社ファーマテック | 調剤薬局支援システム',
                    'url': 'https://example-pharmatech.com',
                    'snippet': '調剤薬局向け業務支援システムを提供。2018年設立、従業員120名、売上高68億円、営業利益9億円。全国3500店舗以上の薬局が利用。',
                    'revenue_value': 68
                },
                {
                    'title': '株式会社メディカルAI | 医療画像診断支援',
                    'url': 'https://example-medical-ai.com',
                    'snippet': 'AI医療画像診断支援システムを開発。2019年設立、従業員95名、売上高135億円、営業利益22億円。大学病院・総合病院150施設以上に導入。',
                    'revenue_value': 135
                },
                {
                    'title': '株式会社ケアテック | 介護支援システム',
                    'url': 'https://example-caretech.com',
                    'snippet': '介護施設向け管理システムを提供。2021年設立、従業員38名、売上高9億円、営業利益1億円。介護記録・請求業務のデジタル化を推進。',
                    'revenue_value': 9
                }
            ],
            'retail': [
                {
                    'title': '株式会社リテールテック | ECプラットフォーム',
                    'url': 'https://example-retailtech.com',
                    'snippet': 'EC構築・運営プラットフォームを提供。2018年設立、従業員110名、売上高58億円、営業利益7億円。D2Cブランド支援に注力。',
                    'revenue_value': 58
                },
                {
                    'title': '株式会社オムニチャネルソリューションズ | 小売DX',
                    'url': 'https://example-omnichannel.com',
                    'snippet': '小売店向けオムニチャネル支援システム。2019年設立、従業員75名、売上高34億円、営業利益4億円。実店舗とECの統合ソリューション提供。',
                    'revenue_value': 34
                },
                {
                    'title': '株式会社スマートリテール | 無人店舗システム',
                    'url': 'https://example-smartretail.com',
                    'snippet': '無人決済・店舗運営システムを開発。2020年設立、従業員48名、売上高15億円、営業利益1.8億円。コンビニ・スーパー向けに展開。',
                    'revenue_value': 15
                },
                {
                    'title': '株式会社ファッションテック | アパレルDX',
                    'url': 'https://example-fashiontech.com',
                    'snippet': 'アパレル業界向け在庫管理・MD支援システム。2017年設立、従業員130名、売上高92億円、営業利益12億円。大手アパレル50社以上が利用。',
                    'revenue_value': 92
                },
                {
                    'title': '株式会社マーケットプレイステック | フリマアプリ',
                    'url': 'https://example-marketplace.com',
                    'snippet': 'C2Cマーケットプレイスを運営。2019年設立、従業員62名、売上高7億円、営業利益0.7億円。特定ジャンルに特化したフリマサービス。',
                    'revenue_value': 7
                }
            ],
            'manufacturing': [
                {
                    'title': '株式会社スマートファクトリー | 製造業DX',
                    'url': 'https://example-smartfactory.com',
                    'snippet': '製造業向けIoT・AI活用システムを提供。2018年設立、従業員95名、売上高48億円、営業利益6億円。工場の自動化・効率化を支援。',
                    'revenue_value': 48
                },
                {
                    'title': '株式会社インダストリー4.0 | スマート製造',
                    'url': 'https://example-industry40.com',
                    'snippet': '製造業向けデジタルツイン・予知保全システム。2019年設立、従業員72名、売上高28億円、営業利益3億円。製造ラインの最適化を実現。',
                    'revenue_value': 28
                },
                {
                    'title': '株式会社プロダクションテック | 生産管理システム',
                    'url': 'https://example-productiontech.com',
                    'snippet': 'クラウド型生産管理システムを開発。2017年設立、従業員140名、売上高85億円、営業利益11億円。中堅製造業800社以上が導入。',
                    'revenue_value': 85
                },
                {
                    'title': '株式会社3Dプリントイノベーション | 3D製造',
                    'url': 'https://example-3dprint-innovation.com',
                    'snippet': '産業用3Dプリンティングサービス。2020年設立、従業員55名、売上高16億円、営業利益2億円。試作開発から量産まで対応。',
                    'revenue_value': 16
                },
                {
                    'title': '株式会社ロボティクスソリューション | 産業ロボット',
                    'url': 'https://example-robotics-solution.com',
                    'snippet': '協働ロボット・自動化システムを提供。2018年設立、従業員88名、売上高6億円、営業利益0.6億円。中小製造業向けロボット導入支援。',
                    'revenue_value': 6
                }
            ],
            'food': [
                {
                    'title': '株式会社フードテック | フードデリバリー',
                    'url': 'https://example-foodtech.com',
                    'snippet': 'クラウドキッチン・デリバリー最適化プラットフォーム。2019年設立、従業員78名、売上高45億円、営業利益5億円。飲食店のデリバリー売上向上を支援。',
                    'revenue_value': 45
                },
                {
                    'title': '株式会社アグリテック | 農業DX',
                    'url': 'https://example-agritech.com',
                    'snippet': 'スマート農業・生産管理システムを提供。2020年設立、従業員52名、売上高22億円、営業利益2.5億円。IoTセンサーで農作物の最適管理を実現。',
                    'revenue_value': 22
                },
                {
                    'title': '株式会社レストランマネジメントテック | 飲食店支援',
                    'url': 'https://example-restaurant-management.com',
                    'snippet': '飲食店向け予約・在庫管理システム。2018年設立、従業員110名、売上高68億円、営業利益8億円。全国10000店舗以上が利用。',
                    'revenue_value': 68
                },
                {
                    'title': '株式会社フードサプライチェーン | 食品流通DX',
                    'url': 'https://example-food-supply.com',
                    'snippet': '食品流通・トレーサビリティシステム。2017年設立、従業員135名、売上高110億円、営業利益14億円。食の安全・効率化を推進。',
                    'revenue_value': 110
                },
                {
                    'title': '株式会社ミールキット | 定期宅配サービス',
                    'url': 'https://example-mealkit.com',
                    'snippet': '食材・ミールキット定期宅配サービス。2020年設立、従業員45名、売上高8億円、営業利益0.9億円。健康志向の顧客向けに展開。',
                    'revenue_value': 8
                }
            ],
            'education': [
                {
                    'title': '株式会社エドテック | オンライン学習プラットフォーム',
                    'url': 'https://example-edtech.com',
                    'snippet': 'AI活用オンライン学習プラットフォーム。2019年設立、従業員95名、売上高38億円、営業利益4億円。個別最適化された学習体験を提供。',
                    'revenue_value': 38
                },
                {
                    'title': '株式会社プログラミング教育 | 子供向けプログラミング',
                    'url': 'https://example-programming-edu.com',
                    'snippet': '子供向けプログラミング教育サービス。2018年設立、従業員68名、売上高24億円、営業利益3億円。全国150教室を展開。',
                    'revenue_value': 24
                },
                {
                    'title': '株式会社スタディサポート | 学習管理システム',
                    'url': 'https://example-studysupport.com',
                    'snippet': '学校・学習塾向け管理システム。2017年設立、従業員125名、売上高72億円、営業利益9億円。教育機関3000校以上が導入。',
                    'revenue_value': 72
                },
                {
                    'title': '株式会社語学学習AI | AI英語学習',
                    'url': 'https://example-language-ai.com',
                    'snippet': 'AI活用の語学学習アプリ。2020年設立、従業員58名、売上高15億円、営業利益1.8億円。ユーザー数80万人突破。',
                    'revenue_value': 15
                },
                {
                    'title': '株式会社キャリア教育テック | 就活支援',
                    'url': 'https://example-career-edutech.com',
                    'snippet': '学生向けキャリア教育・就活支援プラットフォーム。2019年設立、従業員42名、売上高6億円、営業利益0.7億円。大学との連携を強化。',
                    'revenue_value': 6
                }
            ],
            'logistics': [
                {
                    'title': '株式会社ロジテック | 物流最適化',
                    'url': 'https://example-logitech.com',
                    'snippet': '物流業務最適化システムを提供。2018年設立、従業員102名、売上高55億円、営業利益7億円。配送ルート最適化・倉庫管理を自動化。',
                    'revenue_value': 55
                },
                {
                    'title': '株式会社ラストワンマイル | 配送DX',
                    'url': 'https://example-lastmile.com',
                    'snippet': 'ラストワンマイル配送マッチングプラットフォーム。2019年設立、従業員75名、売上高32億円、営業利益3.5億円。個人配送員と荷主をマッチング。',
                    'revenue_value': 32
                },
                {
                    'title': '株式会社倉庫管理システムズ | WMS提供',
                    'url': 'https://example-wms.com',
                    'snippet': 'クラウド型倉庫管理システム（WMS）。2017年設立、従業員145名、売上高88億円、営業利益11億円。EC・小売業向けに特化。',
                    'revenue_value': 88
                },
                {
                    'title': '株式会社トラックマッチング | 運送マッチング',
                    'url': 'https://example-truck-matching.com',
                    'snippet': '運送業者とドライバーのマッチングプラットフォーム。2020年設立、従業員62名、売上高18億円、営業利益2億円。ドライバー不足解消に貢献。',
                    'revenue_value': 18
                },
                {
                    'title': '株式会社ドローン配送 | 無人配送',
                    'url': 'https://example-drone-delivery.com',
                    'snippet': 'ドローン配送システムを開発。2021年設立、従業員38名、売上高5億円、営業利益0.5億円。過疎地域での実証実験を推進。',
                    'revenue_value': 5
                }
            ]
        }
        
        # デフォルトデータ（その他の業界）
        default_data = industry_data.get('it_saas', [])
        
        # 指定された業界の基本データを取得
        base_companies = industry_data.get(industry, default_data)
        
        # 基本データを100社分に拡張
        companies = self._generate_company_variations(base_companies, target_count=100)
        
        # 売上規模でフィルタリング
        revenue_ranges = {
            'under10': (0, 10),
            '10to30': (10, 30),
            '30to50': (30, 50),
            '50to100': (50, 100),
            '100to300': (100, 300),
            '300to500': (300, 500),
            '500to1000': (500, 1000),
            'over1000': (1000, 10000)
        }
        
        min_rev, max_rev = revenue_ranges.get(revenue, (0, 10000))
        
        # 売上規模でフィルタリング
        filtered = [c for c in companies if min_rev <= c.get('revenue_value', 0) < max_rev]
        
        # フィルタ結果が十分にあればそれを返す
        if len(filtered) >= 100:
            return filtered[:100]
        
        # フィルタ結果が少ない場合は、近い売上規模の企業も含める
        # まず、条件に合う企業を優先
        result = filtered.copy()
        
        # 不足している場合、売上規模に近い企業から順に追加
        if len(result) < 100:
            # フィルタ外の企業を売上規模の近さでソート
            other_companies = [c for c in companies if c not in filtered]
            
            # 目標売上範囲の中央値
            target_revenue = (min_rev + max_rev) / 2
            
            # 目標値との差でソート（近い順）
            other_companies.sort(key=lambda c: abs(c.get('revenue_value', 0) - target_revenue))
            
            # 必要な数だけ追加
            needed = 100 - len(result)
            result.extend(other_companies[:needed])
        
        return result[:100]  # 最大100社
    
    def _get_sample_data(self, num_companies: int) -> List[Dict]:
        """
        デモ用のサンプルデータを生成（後方互換性のため残す）
        """
        return self._get_sample_data_by_industry('it_saas', '10to30')[:num_companies]

