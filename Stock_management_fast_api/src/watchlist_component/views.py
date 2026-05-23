from uuid import UUID

from fastapi import APIRouter, Request, Depends, Form
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.authenticator_component.authenticator import get_current_user_id
from src.database.models import BoughtStock
from src.utils.utils import render_localized
from src.database import models

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