"""
検索API
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import parse_qs

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 環境変数を設定
os.environ['USE_MEMORY_DB'] = 'true'

from company_search import CompanySearch
from keyman_finder import KeymanFinder
import database_memory as db_module

# データベース初期化
db_module.init_db()

# サービスインスタンス
company_search = CompanySearch()
keyman_finder = KeymanFinder()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            industry = data.get('industry', '')
            revenue = data.get('revenue', '')
            keywords = data.get('keywords', '')
            num_companies = data.get('num_companies', 5)
            max_keymen = data.get('max_keymen', 5)
            
            # 検索条件の文字列を作成
            conditions_text = f"業界: {industry}, 売上: {revenue}"
            if keywords:
                conditions_text += f", キーワード: {keywords}"
            
            # データベースに検索を作成
            search_id = db_module.create_search(conditions_text, num_companies)
            
            # すぐに検索を実行（バックグラウンドタスクは使えないため）
            try:
                db_module.update_search_status(search_id, "processing")
                
                results = []
                companies = company_search.search_companies_by_criteria(industry, revenue, keywords, num_companies)
                
                if not companies:
                    db_module.update_search_status(search_id, "failed", error_message="企業が見つかりませんでした")
                else:
                    for company in companies:
                        keymen = keyman_finder.find_keymen(company['企業名'], max_keymen)
                        
                        for keyman in keymen:
                            result_row = {
                                '企業名': company['企業名'],
                                '企業URL': company['企業URL'],
                                '事業概要': company['事業概要'],
                                '設立年': company.get('設立年', ''),
                                '売上': company.get('売上', ''),
                                '利益': company.get('利益', ''),
                                '従業員規模': company.get('従業員規模', ''),
                                '事業領域': company.get('事業領域', ''),
                                '注力ポイント': company.get('注力ポイント', ''),
                                'キーマン氏名': keyman['氏名'],
                                '役職名': keyman['役職']
                            }
                            results.append(result_row)
                    
                    db_module.update_search_status(search_id, "completed", results=results)
            
            except Exception as e:
                db_module.update_search_status(search_id, "failed", error_message=str(e))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'search_id': search_id,
                'message': '検索を開始しました'
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                'error': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

