import traceback
from uuid import UUID
from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.authenticator_component.authenticator import get_current_user_id
from src.database.models import BoughtStock, StockSummary
from src.utils.utils import render_localized
from src.watchlist_component.schemas import WatchlistRequest
from src.watchlist_component.service import WatchlistStockService
from src.watchlist_component.schemas import DeleteWatchListStockRequest
from src.evaluation_component.evaluation import Evaluator
from src.ticker_stock_component.ticker_stock import TickerStock
from src.html__text_parser_component.bs4_text_parser import BS4TextParser
from src.youtube_transcript_component.yt_transcript_component import \
    YoutubeTranscriptComponent

templates = Jinja2Templates(directory="templates")

watchlist_router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@watchlist_router.get("/")
def watch_list(request: Request, db: Session = Depends(get_db), current_user_id: UUID = Depends(get_current_user_id)):

    watchlist_service = WatchlistStockService(db)
    watch_list_stocks = watchlist_service.get_watchlist_stocks_of_current_user(current_user_id)
    return templates.TemplateResponse(request=request,
                                      name="watchlist/watchlist.html",
                                      context={"request": request,
                                               "watch_list_stocks": watch_list_stocks
                                               })

@watchlist_router.post("/add-to-watchlist-from-url-analysis")
async def add_to_watchlist_and_evaluation(
        company: WatchlistRequest,
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:



        evaluator = Evaluator(db,"llama-3.3-70b-versatile")
        trajectory, reasoning, recommendation = await evaluator.evaluate_new_information(current_user_id,
                                                                                   company.company_name,
                                                                                   company.strength,
                                                                                   company.weakness,
                                                                                   company.url,
                                                                                    company.yt_url
                                                                                   )

        watchlist_service = WatchlistStockService(db)

        ticker_component = TickerStock()
        ticker = ticker_component.get_ticker_of_a_stock(company.company_name)

        new_content = ""

        if company.url:
            html_parser = BS4TextParser()
            new_content = await html_parser.get_website_text(url)

        if company.yt_url:
            yt_transcript_component = YoutubeTranscriptComponent()
            new_content = yt_transcript_component.get_summary_of_yt_video(yt_url)

        watchlist_service.add_to_current_user_to__watchlist(
            name=company.company_name,
            ticker=ticker,
            strength=company.strength,
            weakness=company.weakness,
            user_id=current_user_id,
            new_content=new_content
        )


        return {
                "message": "Firma aktualisiert!",
                "id": 0,
                "trajectory": trajectory,
                "reasoning": reasoning,
                "recommendation": recommendation
        }


    except Exception as e:
        traceback.print_exc()
        return {"error": "fehler"}


@watchlist_router.post("/delete-stock-from-watchlist", response_class=HTMLResponse)
def delete_stock_from_watchlist(
request: Request,
    selected_companies: list[str] = Form(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    try:

        watchlist_service = WatchlistStockService(db)
        get_ticker_component = TickerStock()

        selected_tickers = [get_ticker_component.get_ticker_of_a_stock(company_name) for company_name in selected_companies]
        watchlist_service.delete_watchlist_stocks_of_current_user(current_user_id,selected_tickers)
        watch_list_stocks = watchlist_service.get_watchlist_stocks_of_current_user(current_user_id)
        return templates.TemplateResponse(request=request,
                                          name="watchlist/watchlist.html",
                                          context={"request": request,
                                                   "watch_list_stocks": watch_list_stocks
                                                   })
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request}
        )
