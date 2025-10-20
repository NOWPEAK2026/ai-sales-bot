"""
FastAPI Webアプリケーション
AI営業アポイント自動化BOT - Webサービス版
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime
import os

from company_search import CompanySearch
from keyman_finder import KeymanFinder

# 環境に応じてデータベースを切り替え
if os.getenv('USE_MEMORY_DB', 'false').lower() == 'true':
    import database_memory as db_module
else:
    import database as db_module

# FastAPIアプリケーション
app = FastAPI(
    title="AI営業アポイント自動化BOT",
    description="企業リストアップ、キーマン特定、SNSアカウント検索を自動化",
    version="2.0.0"
)

# テンプレート設定
import pathlib
TEMPLATE_DIR = pathlib.Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# データベース初期化
db_module.init_db()

# サービスクラスのインスタンス
company_search = CompanySearch()
keyman_finder = KeymanFinder()


# リクエスト/レスポンスモデル
class SearchRequest(BaseModel):
    industry: str
    revenue: str
    keywords: Optional[str] = ""
    num_companies: int = 5
    max_keymen: int = 5


class SearchResponse(BaseModel):
    search_id: int
    message: str


class SearchStatus(BaseModel):
    search_id: int
    status: str
    progress: Optional[int] = None
    results: Optional[List[Dict]] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


# バックグラウンドタスク
def perform_search(search_id: int, industry: str, revenue: str, keywords: str, num_companies: int, max_keymen: int = 5):
    """
    バックグラウンドで検索を実行
    """
    try:
        print(f"\n[Search {search_id}] 検索開始")
        # ステータスを処理中に更新
        db_module.update_search_status(search_id, "processing")
        
        results = []
        
        # 企業検索
        print(f"[Search {search_id}] 企業検索中...")
        companies = company_search.search_companies_by_criteria(industry, revenue, keywords, num_companies)
        print(f"[Search {search_id}] {len(companies)}社を取得")
        
        if not companies:
            error_msg = "企業が見つかりませんでした。検索条件を変更してください。"
            print(f"[Search {search_id}] エラー: {error_msg}")
            db.update_search_status(search_id, "failed", error_message=error_msg)
            return
        
        # 各企業について役員・責任者を検索
        for i, company in enumerate(companies, 1):
            print(f"[Search {search_id}] 企業 {i}/{len(companies)}: {company['企業名']}")
            # 役員・責任者を特定
            keymen = keyman_finder.find_keymen(
                company['企業名'],
                company['企業URL'],
                max_keymen
            )
            
            # 結果を統合
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
        
        # 結果を保存して完了
        print(f"[Search {search_id}] 完了: {len(results)}件の役員・責任者情報を取得")
        db.update_search_status(search_id, "completed", results=results)
    
    except Exception as e:
        # エラーが発生した場合
        import traceback
        error_message = f"{str(e)}\n{traceback.format_exc()}"
        print(f"[Search {search_id}] エラー発生:\n{error_message}")
        db.update_search_status(search_id, "failed", error_message=str(e))


# APIエンドポイント

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    トップページ
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/search", response_model=SearchResponse)
async def create_search(search_request: SearchRequest, background_tasks: BackgroundTasks):
    """
    新しい検索を開始
    """
    # 検索条件の文字列を作成
    conditions_text = f"業界: {search_request.industry}, 売上: {search_request.revenue}"
    if search_request.keywords:
        conditions_text += f", キーワード: {search_request.keywords}"
    
    # データベースに検索を作成
    search_id = db.create_search(
        conditions_text,
        search_request.num_companies
    )
    
    # バックグラウンドタスクとして検索を実行
    background_tasks.add_task(
        perform_search,
        search_id,
        search_request.industry,
        search_request.revenue,
        search_request.keywords,
        search_request.num_companies,
        search_request.max_keymen
    )
    
    return SearchResponse(
        search_id=search_id,
        message="検索を開始しました。しばらくお待ちください。"
    )


@app.get("/api/search/{search_id}", response_model=SearchStatus)
async def get_search_status(search_id: int):
    """
    検索のステータスと結果を取得
    """
    search = db.get_search(search_id)
    
    if not search:
        raise HTTPException(status_code=404, detail="検索が見つかりません")
    
    return SearchStatus(
        search_id=search.id,
        status=search.status,
        results=search.results if search.status == "completed" else None,
        error_message=search.error_message,
        created_at=search.created_at
    )


@app.get("/api/history")
async def get_search_history(limit: int = 20):
    """
    検索履歴を取得
    """
    searches = db.get_all_searches(limit)
    
    history = []
    for search in searches:
        history.append({
            "search_id": search.id,
            "conditions": search.search_conditions,
            "num_companies": search.num_companies,
            "status": search.status,
            "created_at": search.created_at.isoformat(),
            "result_count": len(search.results) if search.results else 0
        })
    
    return {"history": history}


@app.get("/api/export/{search_id}/{format}")
async def export_results(search_id: int, format: str):
    """
    結果を指定されたフォーマットでエクスポート
    format: csv, json, tsv
    """
    search = db.get_search(search_id)
    
    if not search or not search.results:
        raise HTTPException(status_code=404, detail="結果が見つかりません")
    
    results = search.results
    
    if format == "json":
        return JSONResponse(content=results)
    
    elif format == "csv" or format == "tsv":
        import csv
        import io
        
        delimiter = '\t' if format == 'tsv' else ','
        
        output = io.StringIO()
        if results:
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(results)
        
        content = output.getvalue()
        
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type="text/csv" if format == "csv" else "text/plain",
            headers={
                "Content-Disposition": f"attachment; filename=sales_leads_{search_id}.{format}"
            }
        )
    
    else:
        raise HTTPException(status_code=400, detail="サポートされていないフォーマットです")


@app.get("/health")
async def health_check():
    """
    ヘルスチェック
    """
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    print("=" * 70)
    print(" AI営業アポイント自動化BOT - Webサービス")
    print("=" * 70)
    print("\nサーバーを起動しています...")
    print("URL: http://localhost:8000")
    print("API ドキュメント: http://localhost:8000/docs")
    print("\n終了するには Ctrl+C を押してください")
    print("=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

