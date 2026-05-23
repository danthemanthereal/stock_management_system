from uuid import UUID
from fastapi import APIRouter, Request, Depends, Form
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.authenticator_component.authenticator import get_current_user_id
from src.database.models import BoughtStock
from src.utils.utils import render_localized

templates = Jinja2Templates(directory="templates")

portfolio_router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@portfolio_router.get("/", response_class=HTMLResponse)
async def get_portfolio_page(request: Request,
                             db: Session = Depends(get_db),
                             current_user_id: UUID = Depends(get_current_user_id)):
    try:
        print("current user id in enty method", current_user_id)
        bought_stocks = db.query(BoughtStock).filter(BoughtStock.user_id == str(current_user_id)).order_by(
            BoughtStock.ticker).all()
        print("bought stocks", bought_stocks)
        return render_localized(
            template_name="portfolio.html",
            request=request,
            context={
                "request": request,
                "bought_stocks": bought_stocks,
            }
        )

    except Exception as e:
        print(f"Fehler beim Laden des Portfolios: {e}")
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})



@portfolio_router.post("/create")
async def create_bought_stock_of_current_user(
        name: str = Form(...),
        ticker: str = Form(...),
        bought_price: float = Form(...),
        amount: float = Form(...),
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:
        print("current user id in create:", current_user_id)
        new_stock = BoughtStock(
            name=name.strip(),
            ticker=ticker.strip().upper(),
            bought_price=bought_price,
            amount=amount,
            user_id=str(current_user_id)
        )
        db.add(new_stock)
        db.commit()

        return RedirectResponse(url="/portfolio/", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"Fehler beim Speichern der Aktie: {e}")
        return RedirectResponse(url="/portfolio/", status_code=303)



@portfolio_router.post("/update-multiple")
async def update_multiple_portfolio_entries(
        delete_ids: str = Form(""),
        update_triplets: str = Form(""),
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:
        if delete_ids:
            id_list_to_delete = [int(stock_id) for stock_id in delete_ids.split(",") if stock_id.strip()]
            if id_list_to_delete:
                db.query(BoughtStock).filter(BoughtStock.id.in_(id_list_to_delete),
                                             BoughtStock.user_id == str(current_user_id)).delete(synchronize_session=False)

        if update_triplets:
            triplet_list = [t.strip() for t in update_triplets.split(",") if t.strip()]

            for triplet in triplet_list:
                if "|" in triplet:
                    parts = triplet.split("|")
                    if len(parts) == 3:
                        stock_id = int(parts[0])
                        new_price = float(parts[1])
                        new_amount = float(parts[2])

                        stock_entry = db.query(BoughtStock).filter(BoughtStock.id == stock_id,
                                                                   str(BoughtStock.user_id == current_user_id)).first()
                        if stock_entry:
                            stock_entry.bought_price = new_price
                            stock_entry.amount = new_amount

        db.commit()

        return RedirectResponse(url="/portfolio", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"Fehler bei der Massenverarbeitung des Portfolios: {e}")
        return RedirectResponse(url="/portfolio/", status_code=303)
