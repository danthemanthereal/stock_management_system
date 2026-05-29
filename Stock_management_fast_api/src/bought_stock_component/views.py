import traceback
from uuid import UUID

from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates
from src.bought_stock_component.schema import BoughtStockRequest
from src.database.db import get_db
from src.authenticator_component.authenticator import get_current_user_id
from src.bought_stock_component.service import BoughtStockService
from src.watchlist_component.service import WatchlistStockService

from src.ticker_stock_component.ticker_stock import TickerStock

templates = Jinja2Templates(directory="templates")

bought_stock_router = APIRouter(prefix="/bought-stock", tags=["bought-stock"])


@bought_stock_router.post("/buy-stock-from-watchlist")
def add_stock_from_watchlist(
        request: Request,
        name: str = Form(...),
        amount: float = Form(...),
        bought_price: float = Form(...),
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:

        get_ticker_component = TickerStock()
        ticker = get_ticker_component.get_ticker_of_a_stock(name)

        bought_stock_service = BoughtStockService(db=db)

        watchlist_service = WatchlistStockService(db=db)

        current_stock_on_watchlist = watchlist_service.get_current_stock_of_user(current_user_id=current_user_id, ticker_of_stock=ticker)

        bought_stock_service.add_stock_to_current_user(
            name=name,
            ticker=ticker,
            amount=amount,
            bought_price=bought_price,
            current_user_id=current_user_id,
            strengths=current_stock_on_watchlist.strength,
            weakness=current_stock_on_watchlist.weakness,
            wiki_page=current_stock_on_watchlist.wiki_page
        )

        watchlist_service.deactivate_current_stock_on_watchlist(current_user_id, ticker)
        watch_list_stocks = watchlist_service.get_watchlist_stocks_of_current_user(current_user_id)

        return templates.TemplateResponse(
            request=request,
            name="watchlist/watchlist.html",
            context={"request": request,
                     "watch_list_stocks": watch_list_stocks})
    except Exception as error:
        print(error)
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})
