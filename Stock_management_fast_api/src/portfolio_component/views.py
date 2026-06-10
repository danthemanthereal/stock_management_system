import traceback
from uuid import UUID
from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from src.configs.used_model import LLM_WIKI_MODEL
from src.database.db import get_db
from src.authenticator_component.authenticator import get_current_user_id
from src.kaparthies_llm_wiki_component.llm_wiki import LLMWiki
from src.portfolio_component.schema import ChatRequest
from src.portfolio_component.service import PortfolioService
from src.utils.utils import render_localized
from src.bought_stock_component.service import BoughtStockService

from src.ticker_stock_component.ticker_stock import TickerStock

templates = Jinja2Templates(directory="templates")

portfolio_router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@portfolio_router.get("/", response_class=HTMLResponse)
async def get_portfolio_page(request: Request,
                             db: AsyncSession = Depends(get_db),
                             current_user_id: UUID = Depends(get_current_user_id)):
    try:
        portfolio_service = PortfolioService(db)

        bought_stocks = await portfolio_service.get_bought_stocks_of_current_user(str(current_user_id))

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
        db: AsyncSession = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:

        portfolio_service = PortfolioService(db)

        ticker = portfolio_service.get_ticker_of_stock(name)

        await portfolio_service.add_to_user_stock(
            name=name,
            ticker=ticker,
            bought_price=bought_price,
            amount=amount,
            current_user_id=current_user_id,
        )



        bought_stocks = await bought_stock_service.get_bought_stocks_of_current_user(current_user_id=str(current_user_id))
        return render_localized(
            template_name="portfolio/portfolio.html",
            request=request,
            context={
                "request": request,
                "bought_stocks": bought_stocks,
            }
        )

    except Exception as e:
        await db.rollback()
        traceback.print_exc()
        print(f"Fehler beim Speichern der Aktie: {e}")
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})



@portfolio_router.post("/update-multiple-bought-stock-current-user")
async def update_multiple_portfolio_entries(
        request: Request,
        delete_ids: str = Form(""),
        update_triplets: str = Form(""),
        db: AsyncSession = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:
        bought_stock_service = BoughtStockService(db=db)
        await bought_stock_service.update_bought_stocks_of_current_user(current_user_id,delete_ids, update_triplets)
        bought_stocks = await bought_stock_service.get_bought_stocks_of_current_user(current_user_id=str(current_user_id))
        return render_localized(
            template_name="portfolio/portfolio.html",
            request=request,
            context={
                "request": request,
                "bought_stocks": bought_stocks,
            }
        )

    except Exception as e:
        traceback.print_exc()
        await db.rollback()
        print(f"Fehler bei der Massenverarbeitung des Portfolios: {e}")

        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})

@portfolio_router.post("/chat-to-current-stock-wiki-page")
async def chat_endpoint(request: ChatRequest,
                        db: AsyncSession = Depends(get_db),):

    bought_stock_service = BoughtStockService(db=db)

    llm_wiki = LLMWiki(db=db,
                       groq_model_name=LLM_WIKI_MODEL)

    current_stock_wiki_page = await bought_stock_service.get_current_wiki_page_by_id(int(request.stock_id))

    answer = llm_wiki.query_on_wiki_page(
        question=request.message,
        current_wiki_page=current_stock_wiki_page
    )

    return {"response": answer}