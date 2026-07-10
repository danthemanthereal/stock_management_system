import traceback
from uuid import UUID
from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse, HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates
from src.database.db import get_db
from src.authenticator_component.authenticator import get_current_user_id
from src.bought_stock_component.service import BoughtStockService


templates = Jinja2Templates(directory="templates")

bought_stock_router = APIRouter(prefix="/bought-stock", tags=["bought-stock"])


@bought_stock_router.post("/buy-stock-from-watchlist")
async def add_stock_from_watchlist(
        request: Request,
        name: str = Form(...),
        amount: float = Form(...),
        bought_price: float = Form(...),
        db: AsyncSession= Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:

        bought_stock_service = BoughtStockService(db=db)

        ticker = bought_stock_service.get_ticker_of_a_stock(name)

        current_stock_on_watchlist = await bought_stock_service.get_current_stock_on_watchlist_obj(
            ticker=ticker.strip(),
            current_user_id=current_user_id
        )

        await bought_stock_service.add_stock_to_current_user(
            name=name,
            ticker=ticker,
            amount=amount,
            bought_price=bought_price,
            current_user_id=current_user_id,
            strengths=current_stock_on_watchlist.strength,
            weakness=current_stock_on_watchlist.weakness,
            wiki_page=current_stock_on_watchlist.wiki_page
        )

        await bought_stock_service.deactivate_current_stock_on_watchlist(current_user_id, ticker)
        watch_list_stocks = await bought_stock_service.get_watchlist_stocks(current_user_id)

        return templates.TemplateResponse(
            request=request,
            name="watchlist/watchlist.html",
            context={"request": request,
                     "watch_list_stocks": watch_list_stocks})
    except Exception as error:
        print(error)
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})


@bought_stock_router.post("/analyse-financial-metrics-watchlist-stock")
def analyse_finmetrics_stock_on_bought_stock(
    name: str = Form(...),

):

    return JSONResponse({
        "name": name,
        "redirect_url": f"/analysis/get-financial-metrics?company={name}"
    })