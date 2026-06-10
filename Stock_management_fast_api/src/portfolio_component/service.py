from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.bought_stock_component.service import BoughtStockService
from src.ticker_stock_component.ticker_stock import TickerStock


class PortfolioService:

    def __init__(self, db: AsyncSession):
        self.db = db

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