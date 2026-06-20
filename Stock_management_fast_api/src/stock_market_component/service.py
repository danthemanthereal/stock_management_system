from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.used_model import LLM_WIKI_MODEL
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


    async def update_wiki_page(self, new_wiki_page):
        await self.db.execute(
            update(StockMarket)
            .where(StockMarket.id == STOCK_MARKET_WIKI_PAGE_ID)
            .values(wiki_page=new_wiki_page)
        )
        await self.db.commit()

    async def update_stock_market_wiki_page(self, new_content):

        llm_wiki = LLMWiki(
            self.db,
            LLM_WIKI_MODEL
        )

        current_page = await self.get_current_wiki_page()

        new_wiki_page = await llm_wiki.ingest_stock_market_wiki_page(
            new_content,
            current_page
        )

        await self.update_wiki_page(new_wiki_page)

