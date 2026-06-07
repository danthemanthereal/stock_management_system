from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import FinancialMetricCategory


class FinancialMetricCategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_metric_categories(self):
        result = await self.db.execute(select(FinancialMetricCategory))
        return result.scalars().all()


    async def get_all
