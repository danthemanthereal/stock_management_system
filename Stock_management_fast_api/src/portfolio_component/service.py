from sqlalchemy.ext.asyncio import AsyncSession

from src.bought_stock_component.service import BoughtStockService


class PortfolioService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_bought_stocks_of_current_user(self, current_user_id: str):
        bought_stock_service = BoughtStockService(db=self.db)
        return await bought_stock_service.get_bought_stocks_of_current_user(
            current_user_id=str(current_user_id))
