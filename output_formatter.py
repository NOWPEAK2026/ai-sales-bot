"""
出力フォーマッターモジュール
結果を様々な形式で出力・表示・コピー
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict
from tabulate import tabulate
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("警告: pyperclipがインストールされていないため、クリップボード機能は無効です")


class OutputFormatter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def display_results(self, results: List[Dict]):
        """
        結果を見やすい表形式でターミナルに表示（簡易版）
        """
        if not results:
            print("\n結果がありません。")
            return
        
        print("\n" + "=" * 120)
        print(" 検索結果（概要）")
        print("=" * 120 + "\n")
        
        # 簡易表形式で表示
        table_data = []
        for i, row in enumerate(results, 1):
            table_data.append([
                i,
                row.get('企業名', '')[:20],
                row.get('従業員規模', '-'),
                row.get('売上', '-')[:15],
                row.get('事業領域', '-')[:25],
                row.get('キーマン氏名', ''),
                row.get('役職名', '')[:15]
            ])
        
        headers = ['#', '企業名', '従業員', '売上', '事業領域', '氏名', '役職']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        print(f"\n合計: {len(results)} 件\n")
    
    def display_detailed_results(self, results: List[Dict]):
        """
        結果を詳細形式で表示
        """
        if not results:
            print("\n結果がありません。")
            return
        
        print("\n" + "=" * 120)
        print(" 詳細な検索結果")
        print("=" * 120)
        
        current_company = None
        company_count = 0
        
        for i, row in enumerate(results, 1):
            company_name = row.get('企業名', '')
            
            # 企業が変わったら区切り線を表示
            if company_name != current_company:
                company_count += 1
                current_company = company_name
                print(f"\n{'─' * 120}")
                print(f"■ 企業 {company_count}: {company_name}")
                print(f"{'─' * 120}")
                print(f"  🌐 URL        : {row.get('企業URL', '')}")
                print(f"  📅 設立年     : {row.get('設立年', '-')}")
                print(f"  💰 売上       : {row.get('売上', '-')}")
                print(f"  📊 利益       : {row.get('利益', '-')}")
                print(f"  👥 従業員規模 : {row.get('従業員規模', '-')}")
                print(f"  🏢 事業領域   : {row.get('事業領域', '-')}")
                print(f"  🎯 注力ポイント: {row.get('注力ポイント', '-')}")
                print(f"  📝 概要       : {row.get('事業概要', '')[:150]}...")
                print(f"\n  【役員・責任者一覧】")
            
            # 役員・責任者情報を表示
            print(f"\n  {i}. {row.get('キーマン氏名', '')} ({row.get('役職名', '')})")
            print(f"     📘 Facebook : {row.get('Facebook URL', 'なし')}")
            print(f"     🐦 X/Twitter: {row.get('X（旧Twitter） URL', 'なし')}")
        
        print(f"\n{'=' * 120}\n")
        print(f"合計: {len(results)} 件の役員・責任者情報\n")
    
    def copy_to_clipboard(self, results: List[Dict], format_type: str = 'tsv') -> bool:
        """
        結果をクリップボードにコピー
        
        Args:
            results: 結果データ
            format_type: フォーマット種別 ('tsv', 'csv', 'markdown', 'json')
        
        Returns:
            成功したかどうか
        """
        if not CLIPBOARD_AVAILABLE:
            print("\n⚠️  クリップボード機能を使用するには、pyperclipをインストールしてください:")
            print("   pip install pyperclip")
            return False
        
        if not results:
            print("\nコピーする結果がありません。")
            return False
        
        try:
            if format_type == 'tsv':
                content = self._format_as_tsv(results)
            elif format_type == 'csv':
                content = self._format_as_csv_string(results)
            elif format_type == 'markdown':
                content = self._format_as_markdown(results)
            elif format_type == 'json':
                content = json.dumps(results, ensure_ascii=False, indent=2)
            else:
                content = self._format_as_tsv(results)
            
            pyperclip.copy(content)
            print(f"\n✓ {format_type.upper()}形式でクリップボードにコピーしました！")
            print(f"  Excel、Google Sheets、テキストエディタなどに貼り付けできます。")
            return True
        
        except Exception as e:
            print(f"\n✗ クリップボードへのコピーに失敗しました: {e}")
            return False
    
    def _format_as_tsv(self, results: List[Dict]) -> str:
        """
        TSV（タブ区切り）形式に変換（Excelに直接貼り付け可能）
        """
        lines = []
        # ヘッダー
        headers = [
            '企業名', '企業URL', '事業概要', '設立年', '売上', '利益', 
            '従業員規模', '事業領域', '注力ポイント',
            'キーマン氏名', '役職名', 'Facebook URL', 'X（旧Twitter） URL'
        ]
        lines.append('\t'.join(headers))
        
        # データ
        for row in results:
            line = '\t'.join([
                row.get('企業名', ''),
                row.get('企業URL', ''),
                row.get('事業概要', ''),
                row.get('設立年', ''),
                row.get('売上', ''),
                row.get('利益', ''),
                row.get('従業員規模', ''),
                row.get('事業領域', ''),
                row.get('注力ポイント', ''),
                row.get('キーマン氏名', ''),
                row.get('役職名', ''),
                row.get('Facebook URL', ''),
                row.get('X（旧Twitter） URL', '')
            ])
            lines.append(line)
        
        return '\n'.join(lines)
    
    def _format_as_csv_string(self, results: List[Dict]) -> str:
        """
        CSV形式の文字列に変換
        """
        import io
        output = io.StringIO()
        
        if results:
            fieldnames = [
                '企業名', '企業URL', '事業概要', '設立年', '売上', '利益',
                '従業員規模', '事業領域', '注力ポイント',
                'キーマン氏名', '役職名', 'Facebook URL', 'X（旧Twitter） URL'
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        return output.getvalue()
    
    def _format_as_markdown(self, results: List[Dict]) -> str:
        """
        Markdown表形式に変換
        """
        lines = []
        # ヘッダー
        lines.append("| 企業名 | 設立年 | 売上 | 従業員 | 事業領域 | 注力ポイント | 氏名 | 役職 | Facebook | X/Twitter |")
        lines.append("|--------|--------|------|--------|----------|--------------|----------|------|----------|-----------|")
        
        # データ
        for row in results:
            line = "| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                row.get('企業名', ''),
                row.get('設立年', '-'),
                row.get('売上', '-'),
                row.get('従業員規模', '-'),
                row.get('事業領域', '-'),
                row.get('注力ポイント', '')[:30] + '...' if len(row.get('注力ポイント', '')) > 30 else row.get('注力ポイント', '-'),
                row.get('キーマン氏名', ''),
                row.get('役職名', ''),
                row.get('Facebook URL', '-'),
                row.get('X（旧Twitter） URL', '-')
            )
            lines.append(line)
        
        return '\n'.join(lines)
    
    def save_as_csv(self, results: List[Dict], filename: str = None) -> str:
        """
        CSV形式で保存
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_leads_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if results:
            fieldnames = [
                '企業名', '企業URL', '事業概要', '設立年', '売上', '利益',
                '従業員規模', '事業領域', '注力ポイント',
                'キーマン氏名', '役職名', 'Facebook URL', 'X（旧Twitter） URL'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        
        return filepath
    
    def save_as_json(self, results: List[Dict], filename: str = None) -> str:
        """
        JSON形式で保存
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_leads_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(results, jsonfile, ensure_ascii=False, indent=2)
        
        return filepath
    
    def save_as_markdown(self, results: List[Dict], filename: str = None) -> str:
        """
        Markdown形式で保存
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_leads_{timestamp}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        markdown_content = self._format_as_markdown(results)
        
        with open(filepath, 'w', encoding='utf-8') as mdfile:
            mdfile.write(f"# 営業リスト - {datetime.now().strftime('%Y年%m月%d日')}\n\n")
            mdfile.write(f"合計: {len(results)} 件\n\n")
            mdfile.write(markdown_content)
        
        return filepath
    
    def show_copy_menu(self, results: List[Dict]):
        """
        コピーメニューを表示
        """
        print("\n" + "=" * 100)
        print(" コピー・保存オプション")
        print("=" * 100)
        print("\n1. TSV形式でクリップボードにコピー（Excel/Sheetsに直接貼り付け可）")
        print("2. Markdown形式でクリップボードにコピー（NotionやGitHubなどで使用）")
        print("3. JSON形式でクリップボードにコピー（プログラムで処理する場合）")
        print("4. CSV形式でファイル保存")
        print("5. JSON形式でファイル保存")
        print("6. Markdown形式でファイル保存")
        print("7. すべての形式で保存")
        print("0. スキップ")
        
        choice = input("\n選択してください (0-7): ").strip()
        
        if choice == '1':
            self.copy_to_clipboard(results, 'tsv')
        elif choice == '2':
            self.copy_to_clipboard(results, 'markdown')
        elif choice == '3':
            self.copy_to_clipboard(results, 'json')
        elif choice == '4':
            filepath = self.save_as_csv(results)
            print(f"\n✓ CSV保存完了: {filepath}")
        elif choice == '5':
            filepath = self.save_as_json(results)
            print(f"\n✓ JSON保存完了: {filepath}")
        elif choice == '6':
            filepath = self.save_as_markdown(results)
            print(f"\n✓ Markdown保存完了: {filepath}")
        elif choice == '7':
            csv_path = self.save_as_csv(results)
            json_path = self.save_as_json(results)
            md_path = self.save_as_markdown(results)
            print(f"\n✓ すべての形式で保存完了:")
            print(f"  - CSV: {csv_path}")
            print(f"  - JSON: {json_path}")
            print(f"  - Markdown: {md_path}")
        elif choice == '0':
            print("\nスキップしました。")
        else:
            print("\n無効な選択です。")

