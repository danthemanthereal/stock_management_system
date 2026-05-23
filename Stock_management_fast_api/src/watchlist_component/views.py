from uuid import UUID
from fastapi import APIRouter, Request, Depends, HTTPException,status
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.authenticator_component.authenticator import get_current_user_id
from src.database.models import BoughtStock
from src.utils.utils import render_localized
from src.database import models
from src.database.models import StockSummary
from src.watchlist_component.schemas import BoughtStockRequest,DeleteWatchListStockRequest
from src.combining_stock_infos_llm.combine_stock import get_combination
from src.evaluation_component.evaluation import evaluate_new_information
from src.watchlist_component.schemas import WatchlistRequest

templates = Jinja2Templates(directory="templates")

watchlist_router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@watchlist_router.get("/")
def watch_list(request: Request, db: Session = Depends(get_db), current_user_id: UUID = Depends(get_current_user_id)):
    watch_list_stocks = db.query(models.StockSummary).filter(models.StockSummary.is_on_watch_list == True,
                                                             models.StockSummary.user_id == str(current_user_id)).all()
    return templates.TemplateResponse(request=request,
                                      name="watchlist.html",
                                      context={"request": request,
                                               "watch_list_stocks": watch_list_stocks
                                               })

@watchlist_router.post("/add-to-watchlist-from-url-analysis")
async def add_to_watchlist(
        company: WatchlistRequest,
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    db_company = db.query(models.StockSummary).filter_by(
        name=company.company_name,
        user_id=str(current_user_id)
    ).first()

    if db_company:
        current_strengths = db_company.strength
        current_weakness = db_company.weakness
        strengths, weaknesses = get_combination(current_strengths, current_weakness, company.strength, company.weakness)
        db_company.strength = "\n".join(f"• {s}" for s in strengths)
        db_company.weakness = "\n".join(f"• {w}" for w in weaknesses)
        db.commit()
        db.refresh(db_company)
        trajectory, reasoning, recommendation = evaluate_new_information(current_strengths, company.strength,
                                                                         current_weakness, company.weakness)

        return {
            "message": "Firma aktualisiert!",
            "id": db_company.id,
            "trajectory": trajectory,
            "reasoning": reasoning,
            "recommendation": recommendation
        }

    else:
        db_company = models.StockSummary(
            name=company.company_name,
            strength=company.strength,
            weakness=company.weakness,
            is_on_watch_list=True,
            user_id=str(current_user_id)
        )
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return {"message": "Firma gespeichert!", "id": db_company.id}

## TODO bei gekaufte aktien comp machen
@watchlist_router.post("/buy-stock-from-watchlist", status_code=status.HTTP_201_CREATED)
def create_bought_stock(stock_data: BoughtStockRequest, db: Session = Depends(get_db),
                        current_user_id: UUID = Depends(get_current_user_id)):
    existing_stock = db.query(BoughtStock).filter(BoughtStock.name == stock_data.name,
                                                  BoughtStock.user_id == str(current_user_id)).first()

    if existing_stock:
        raise HTTPException(
            status_code=400,
            detail=f"Die Aktie '{stock_data.name}' wurde bereits eingebucht!"
        )

    generated_ticker = stock_data.name.replace(" ", "").upper()[:5]

    db_bought_stock = BoughtStock(
        name=stock_data.name,
        ticker=generated_ticker,
        amount=stock_data.amount,
        bought_price=stock_data.bought_price,
        user_id=current_user_id
    )

    try:
        db.add(db_bought_stock)
        current_stock = db.query(StockSummary).filter(StockSummary.name == stock_data.name,
                                                      StockSummary.user_id == str(current_user_id)).first()
        current_stock.is_on_watch_list = False
        db.commit()
        db.refresh(db_bought_stock)
        return {"status": "success", "message": "Aktie erfolgreich eingebucht", "data": db_bought_stock}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@watchlist_router.post("/delete-stock-from-watchlist", response_class=HTMLResponse)
def delete_stock_from_watchlist(
        request: Request,
        data: DeleteWatchListStockRequest,
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:
        if not data.companies:
            return {"message": "Keine Companies übergeben", "deleted": 0}

        db.query(models.StockSummary) \
            .filter(models.StockSummary.name.in_(data.companies), models.StockSummary.user_id == str(current_user_id)) \
            .delete(synchronize_session=False)

        db.commit()

        watch_list_stocks = db.query(models.StockSummary).filter(models.StockSummary.is_on_watch_list == True,
                                                                 models.StockSummary.user_id == str(current_user_id)).all()
        return templates.TemplateResponse(request=request,
                                          name="watchlist.html",
                                          context={"request": request,
                                                   "watch_list_stocks": watch_list_stocks
                                                   })
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request}
        )
