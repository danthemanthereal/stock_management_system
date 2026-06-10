from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.bought_stock_component.service import BoughtStockService
from src.configs.used_model import LLM_WIKI_MODEL
from src.kaparthies_llm_wiki_component.llm_wiki import LLMWiki
from src.portfolio_component.schema import ChatRequest
from src.ticker_stock_component.ticker_stock import TickerStock
from src.utils.utils import render_localized
from fastapi import Request

class PortfolioService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_portfolio_main_page(self,

                                      current_user_id:UUID,
                                      request: Request):

        bought_stock_service = BoughtStockService(self.db)

        bought_stocks = await bought_stock_service.get_bought_stocks_of_current_user(
            current_user_id=str(current_user_id))
        return render_localized(
            template_name="portfolio/portfolio.html",
            request=request,
            context={
                "request": request,
                "bought_stocks": bought_stocks,
            }
        )

    async def add_to_user_stock(self,
                                name: str,
                                bought_price: float,
                                amount: float,
                                current_user_id:UUID,
                                ):
        ticker = self.get_ticker_of_stock(name)

        bought_stock_service = BoughtStockService(self.db)

        await bought_stock_service.add_stock_to_current_user(
            name=name,
            ticker=ticker,
            bought_price=bought_price,
            amount=amount,
            current_user_id=current_user_id,
            strengths="",
            weakness="",
            wiki_page=""
        )


    async def get_bought_stocks_of_current_user(self, current_user_id: str):
        bought_stock_service = BoughtStockService(db=self.db)
        return await bought_stock_service.get_bought_stocks_of_current_user(
            current_user_id=str(current_user_id))

    def get_ticker_of_stock(self, company: str):
        get_ticker_component = TickerStock()
        return get_ticker_component.get_ticker_of_a_stock(company)

    async def add_to_user_stock(self,
                                name: str,
                                ticker: str,
                                bought_price: float,
                                amount: float,
                                current_user_id: UUID):
        bought_stock_service = BoughtStockService(db=self.db)
        await bought_stock_service.add_stock_to_current_user(name=name, ticker=ticker,
                                                             bought_price=bought_price,
                                                             amount=amount,
                                                             current_user_id=current_user_id,
                                                             strengths="", weakness="", wiki_page="")

    async def update_bought_stocks(self,
                                   current_user_id:UUID,
                                   delete_ids: str,
                                   update_triplets: str):
        bought_stock_service = BoughtStockService(db=self.db)
        await bought_stock_service.update_bought_stocks_of_current_user(current_user_id, delete_ids, update_triplets)

    async def get_chat_answer(self,
                              request: ChatRequest):
        bought_stock_service = BoughtStockService(db=self.db)

        llm_wiki = LLMWiki(db=self.db,
                           groq_model_name=LLM_WIKI_MODEL)

        current_stock_wiki_page = await bought_stock_service.get_current_wiki_page_by_id(int(request.stock_id))

        return llm_wiki.query_on_wiki_page(
            question=request.message,
            current_wiki_page=current_stock_wiki_page
        )




