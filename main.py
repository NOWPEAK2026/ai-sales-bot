"""
AI営業アポイント自動化BOT - メインスクリプト
企業リストアップ、キーマン特定、SNSアカウント検索を自動実行
"""

import os
from typing import List, Dict
from company_search import CompanySearch
from keyman_finder import KeymanFinder
from sns_finder import SNSFinder
from output_formatter import OutputFormatter
from config import OUTPUT_DIR


class AISalesBot:
    def __init__(self):
        self.company_search = CompanySearch()
        self.keyman_finder = KeymanFinder()
        self.sns_finder = SNSFinder()
        self.formatter = OutputFormatter(OUTPUT_DIR)
    
    def run(self, conditions: str, num_companies: int, max_keymen: int = 5):
        """
        営業リストアップフローを実行
        
        Args:
            conditions: 企業リストアップ条件
            num_companies: リストアップする企業数
            max_keymen: 各企業のキーマン最大数
        """
        print("=" * 70)
        print("AI営業アポイント自動化BOT 開始")
        print("=" * 70)
        print(f"\n【検索条件】")
        print(f"企業条件: {conditions}")
        print(f"企業数: {num_companies}")
        print(f"キーマン数/企業: 最大{max_keymen}名")
        print("\n" + "=" * 70)
        
        # ステップ1: 企業検索
        print("\n[ステップ1] 企業検索を実行中...")
        companies = self.company_search.search_companies(conditions, num_companies)
        print(f"✓ {len(companies)}社の企業を取得しました\n")
        
        # ステップ2: キーマン特定とSNS検索
        print("[ステップ2] キーマン特定とSNS検索を実行中...")
        results = []
        
        for i, company in enumerate(companies, 1):
            print(f"\n企業 {i}/{len(companies)}: {company['企業名']}")
            
            # キーマン特定
            keymen = self.keyman_finder.find_keymen(
                company['企業名'],
                company['企業URL'],
                max_keymen
            )
            
            print(f"  ✓ {len(keymen)}名のキーマンを特定しました")
            
            # 各キーマンのSNSアカウント検索
            for keyman in keymen:
                sns_accounts = self.sns_finder.find_sns_accounts(
                    keyman['氏名'],
                    company['企業名'],
                    keyman['役職']
                )
                
                # 結果を統合
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
                    '役職名': keyman['役職'],
                    'Facebook URL': sns_accounts['Facebook'],
                    'X（旧Twitter） URL': sns_accounts['X（旧Twitter）']
                }
                
                results.append(result_row)
        
        print("\n✓ キーマン特定とSNS検索が完了しました")
        
        # ステップ3: 結果表示
        print("\n[ステップ3] 結果を表示しています...")
        print("\n" + "=" * 70)
        
        # 簡易表示
        self.formatter.display_results(results)
        
        # 詳細表示の確認
        show_detail = input("\n詳細な結果を表示しますか？ (y/n): ").strip().lower()
        if show_detail == 'y':
            self.formatter.display_detailed_results(results)
        
        # ステップ4: コピー・保存オプション
        print("\n[ステップ4] 結果のコピー・保存")
        self.formatter.show_copy_menu(results)
        
        print("\n" + "=" * 70)
        print(f"\n✓ すべての処理が完了しました！")
        print(f"✓ 合計 {len(results)} 件のキーマン情報を取得しました")
        print("\n" + "=" * 70)
        
        return results
    


def main():
    """
    メイン関数
    """
    print("\n" + "=" * 70)
    print(" AI営業アポイント自動化BOT")
    print(" - 企業リストアップ & SNSアカウント特定 -")
    print("=" * 70 + "\n")
    
    # ユーザー入力
    print("【企業リストアップ条件を入力してください】")
    print("例: SaaS スタートアップ シリーズA 従業員50名以上")
    conditions = input("条件: ").strip()
    
    if not conditions:
        conditions = "SaaS スタートアップ 東京"
        print(f"（デフォルト条件を使用: {conditions}）")
    
    print("\n【リストアップする企業数を入力してください】")
    num_companies_input = input("企業数 (デフォルト: 5): ").strip()
    
    try:
        num_companies = int(num_companies_input) if num_companies_input else 5
    except ValueError:
        num_companies = 5
        print(f"（デフォルト値を使用: {num_companies}）")
    
    # BOT実行
    bot = AISalesBot()
    bot.run(conditions, num_companies)


if __name__ == "__main__":
    main()

