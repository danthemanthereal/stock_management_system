from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.kaparthies_llm_wiki_component.llm_wiki import LLMWiki

STOCK_MARKET_WIKI_PAGE_ID=1

from src.database.models import StockMarket


class StockMarketComponentService:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_current_wiki_page(self):
        return (await self.db.execute(
            select(StockMarket.wiki_page).where(StockMarket.id == STOCK_MARKET_WIKI_PAGE_ID)
        )).scalar_one_or_none()

    async def update_stock_market_wiki_page(self, new_content):

        llm_wiki = LLMWiki(

        )