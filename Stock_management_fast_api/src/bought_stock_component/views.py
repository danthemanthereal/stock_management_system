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
        bought_stock_service = BoughtStockService(db=db)
        watchlist_service = WatchlistStockService(db=db)
        bought_stock_service.add_stock_to_current_user(
            name=name,
            ticker=name,
            amount=amount,
            bought_price=bought_price,
            current_user_id=current_user_id
        )
        watchlist_service.deactivate_current_stock_on_watchlist(current_user_id, name)

        return templates.TemplateResponse(
            request=request,
            name="watchlist/watchlist.html",
            context={"request": request})
    except Exception as error:
        print(error)
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})
