from uuid import UUID
from fastapi import Request
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import StockSummary
from src.kaparthies_llm_wiki_component.llm_wiki import LLMWiki
from src.configs.used_model import LLM_WIKI_MODEL
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

class WatchlistStockService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_watch_list_page(self,
                                  request: Request,
                                  current_user_id: UUID,):
        watch_list_stocks = await self.get_watchlist_stocks_of_current_user(current_user_id)
        return templates.TemplateResponse(request=request,
                                          name="watchlist/watchlist.html",
                                          context={"request": request,
                                                   "watch_list_stocks": watch_list_stocks
                                                   })


    async def get_watchlist_stocks_of_current_user(self, current_user_id: UUID):
        stmt = select(StockSummary).where(
            StockSummary.is_on_watch_list == True,
            StockSummary.user_id == str(current_user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_watchlist_stocks_of_current_user(self, current_user_id: UUID, ticker_companies: list[str]):
        stmt = delete(StockSummary).where(
            StockSummary.ticker.in_(ticker_companies),
            StockSummary.user_id == str(current_user_id)
        )
        await self.db.execute(stmt)
        await self.db.commit()
        await self.db.flush()

    async def deactivate_current_stock_on_watchlist(self, current_user_id: UUID, ticker: str):
        result = await self.db.execute(
            select(StockSummary).where(
                StockSummary.ticker == ticker,
                StockSummary.user_id == str(current_user_id)
            )
        )
        current_stock = result.scalars().first()

        current_stock.is_on_watch_list = False
        await self.db.commit()

    async def check_if_user_has_stock_already_in_watchlist(self, current_user_id: UUID, ticker: str)->bool:
        result = await self.db.execute(
            select(StockSummary).where(
                StockSummary.ticker == ticker,
                StockSummary.user_id == str(current_user_id)
            )
        )
        return result.scalars().first() is not None

    async def get_current_stock_of_user(self, current_user_id: UUID, ticker_of_stock: str) -> StockSummary:
        result = await self.db.execute(
            select(StockSummary).where(
                StockSummary.ticker == ticker_of_stock,
                StockSummary.user_id == str(current_user_id)
            )
        )
        return result.scalars().first()

    async def add_to_current_user_to__watchlist(self,
                                          name: str,
                                          ticker: str,
                                          strength: str,
                                          weakness: str,
                                          user_id: UUID,
                                          new_content: str):

        if await self.check_if_user_has_stock_already_in_watchlist(user_id, ticker):
            current_stock = await self.get_current_stock_of_user(user_id, ticker)
            llm_wiki = LLMWiki(self.db, LLM_WIKI_MODEL)


            (
                new_combined_strengths,
                new_combined_weakness,
                new_combined_wiki
            ) = await llm_wiki.ingest(
                watch_list_stock_id=None,
                bought_stock_id=current_stock.id,
                company_name=name,
                ticker=ticker,
                new_strengths=strength,
                new_weaknesses=weakness,
                new_content=new_content
            )

            await self.update_strength_weakness_wiki_page_of_watchlist_stock(
                watchlist_stock_obj=current_stock,
                new_strength=new_combined_strengths,
                new_weakness=new_combined_weakness,
                new_wiki_page=new_combined_wiki
            )

            await self.db.commit()

            return
        new_watchlist_stock = StockSummary(
            name=name,
            ticker=ticker,
            strength=strength,
            weakness=weakness,
            wiki_page="",
            user_id=str(user_id),
            is_on_watch_list=True
        )
        self.db.add(new_watchlist_stock)
        await self.db.commit()
        await self.db.refresh(new_watchlist_stock)
        llm_wiki = LLMWiki(self.db, LLM_WIKI_MODEL)
        new_strengths, new_weakness, new_wiki_page =  await llm_wiki.ingest(
            watch_list_stock_id=new_watchlist_stock.id,
            bought_stock_id=None,
            company_name=new_watchlist_stock.name,
            ticker=new_watchlist_stock.ticker,
            new_strengths=strength,
            new_weaknesses=weakness,
            new_content=new_content
        )

        await self.update_strength_weakness_wiki_page_of_watchlist_stock(
            watchlist_stock_obj=new_watchlist_stock,
            new_strength=new_strengths,
            new_weakness=new_weakness,
            new_wiki_page=new_wiki_page
        )

    async def get_watch_list_stock_with_id(self, id: int) -> StockSummary:
        result = await self.db.execute(
            select(StockSummary).where(StockSummary.id == id)
        )
        return result.scalars().first()

    async def get_of_current_watchlist_stock_strengths_weakness_wiki_page(self, user_id: UUID, ticker: str):
        current_stock = await self.get_current_stock_of_user(user_id, ticker)
        return (current_stock.strength,
                current_stock.weakness,
                current_stock.wiki_page) if current_stock else  "", "", ""


    async def get_of_current_watchlist_stock_strengths_weakness_wiki_page_with_id(self,watchlist_stock_id: int ):
        current_stock = await self.get_watch_list_stock_with_id(watchlist_stock_id)
        return (
            current_stock.strength if current_stock else "",
            current_stock.weakness if current_stock else "",
            current_stock.wiki_page if current_stock else ""
        )

    async def get_watchlist_stock_id_by_ticker(self, ticker: str) -> int:
        result = await self.db.execute(
            select(StockSummary).where(StockSummary.ticker == ticker)
        )
        stock = result.scalars().first()
        return stock.id if stock else 0

    async def update_strength_weakness_wiki_page_of_watchlist_stock(self,watchlist_stock_obj: StockSummary,new_strength: str, new_weakness: str, new_wiki_page: str):
        watchlist_stock_obj.strength = new_strength
        watchlist_stock_obj.weakness = new_weakness
        watchlist_stock_obj.wiki_page = new_wiki_page
        await self.db.commit()
        await self.db.refresh(watchlist_stock_obj)
