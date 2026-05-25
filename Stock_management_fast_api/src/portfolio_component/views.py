import traceback
from uuid import UUID
from fastapi import APIRouter, Request, Depends, Form
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.authenticator_component.authenticator import get_current_user_id
from src.database.models import BoughtStock
from src.utils.utils import render_localized
from src.bought_stock_component.service import BoughtStockService

templates = Jinja2Templates(directory="templates")

portfolio_router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@portfolio_router.get("/", response_class=HTMLResponse)
async def get_portfolio_page(request: Request,
                             db: Session = Depends(get_db),
                             current_user_id: UUID = Depends(get_current_user_id)):
    try:
        bought_stock_service = BoughtStockService(db=db)
        bought_stocks = bought_stock_service.get_bought_stocks_of_current_user(current_user_id=str(current_user_id))
        return render_localized(
            template_name="portfolio/portfolio.html",
            request=request,
            context={
                "request": request,
                "bought_stocks": bought_stocks,
            }
        )

    except Exception as e:
        print(f"Fehler beim Laden des Portfolios: {e}")
        traceback.print_exc()

        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})



@portfolio_router.post("/create-new-bought-stock-current-user")
async def create_bought_stock_of_current_user(
        request: Request,
        name: str = Form(...),
        ticker: str = Form(...),
        bought_price: float = Form(...),
        amount: float = Form(...),
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:
        bought_stock_service = BoughtStockService(db=db)
        bought_stock_service.create_new_stock_of_current_user(name=name, ticker=ticker,
                                                              bought_price=bought_price,
                                                              amount=amount, current_user_id=current_user_id)


        bought_stocks = bought_stock_service.get_bought_stocks_of_current_user(current_user_id=str(current_user_id))
        return render_localized(
            template_name="portfolio/portfolio.html",
            request=request,
            context={
                "request": request,
                "bought_stocks": bought_stocks,
            }
        )

    except Exception as e:
        db.rollback()
        traceback.print_exc()
        print(f"Fehler beim Speichern der Aktie: {e}")
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})



@portfolio_router.post("/update-multiple-bought-stock-current-user")
async def update_multiple_portfolio_entries(
        request: Request,
        delete_ids: str = Form(""),
        update_triplets: str = Form(""),
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:
        bought_stock_service = BoughtStockService(db=db)
        bought_stock_service.update_bought_stocks_of_current_user(current_user_id,delete_ids, update_triplets)
        bought_stocks = bought_stock_service.get_bought_stocks_of_current_user(current_user_id=str(current_user_id))
        return render_localized(
            template_name="portfolio/portfolio.html",
            request=request,
            context={
                "request": request,
                "bought_stocks": bought_stocks,
            }
        )

    except Exception as e:
        db.rollback()
        print(f"Fehler bei der Massenverarbeitung des Portfolios: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})
