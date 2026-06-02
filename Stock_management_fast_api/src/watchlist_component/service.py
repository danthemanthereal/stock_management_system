from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import StockSummary
from src.kaparthies_llm_wiki_component.llm_wiki import LLMWiki
from src.configs.used_model import LLM_WIKI_MODEL


class WatchlistStockService:
    def __init__(self, db: Session):
        self.db = db

    def get_watchlist_stocks_of_current_user(self, current_user_id: UUID):
        return self.db.query(StockSummary).filter(StockSummary.is_on_watch_list == True,
                                                             StockSummary.user_id == str(current_user_id)).all()

    def delete_watchlist_stocks_of_current_user(self, current_user_id: UUID, ticker_companies: list[str]):

        self.db.query(StockSummary) \
            .filter(
            StockSummary.ticker.in_(ticker_companies),
            StockSummary.user_id == str(current_user_id)
        ) \
            .delete(synchronize_session=False)
        self.db.commit()
        self.db.flush()

    def deactivate_current_stock_on_watchlist(self, current_user_id: UUID, ticker: str):
        current_stock = self.db.query(StockSummary).filter(StockSummary.ticker == ticker,
                                                      StockSummary.user_id == str(current_user_id)).first()
        current_stock.is_on_watch_list = False
        self.db.commit()

    def check_if_user_has_stock_already_in_watchlist(self, current_user_id: UUID, ticker: str):
        return self.db.query(StockSummary).filter(StockSummary.ticker ==ticker,StockSummary.user_id == str(current_user_id)).first() is not None

    def get_current_stock_of_user(self, current_user_id: UUID, ticker_of_stock: str)->StockSummary:
        return self.db.query(StockSummary).filter(StockSummary.ticker == ticker_of_stock,
                                                  StockSummary.user_id == str(current_user_id)).first()

    def add_to_current_user_to__watchlist(self,
                                          name: str,
                                          ticker: str,
                                          strength: str,
                                          weakness: str,
                                          user_id: UUID,
                                          new_content: str):

        if self.check_if_user_has_stock_already_in_watchlist(user_id, ticker):
            current_stock = self.get_current_stock_of_user(user_id, ticker)
            llm_wiki = LLMWiki(self.db, LLM_WIKI_MODEL)


            (
                new_combined_strengths,
                new_combined_weakness,
                new_combined_wiki
            ) = llm_wiki.ingest(
                watch_list_stock_id=None,
                bought_stock_id=current_stock.id,
                company_name=name,
                ticker=ticker,
                new_strengths=strength,
                new_weaknesses=weakness,
                new_content=new_content
            )

            self.update_strength_weakness_wiki_page_of_watchlist_stock(
                watchlist_stock_obj=current_stock,
                new_strength=new_combined_strengths,
                new_weakness=new_combined_weakness,
                new_wiki_page=new_combined_wiki
            )

            self.db.commit()

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
        self.db.commit()
        self.db.refresh(new_watchlist_stock)
        llm_wiki = LLMWiki(self.db, LLM_WIKI_MODEL)
        new_strengths, new_weakness, new_wiki_page =  llm_wiki.ingest(
            watch_list_stock_id=new_watchlist_stock.id,
            bought_stock_id=None,
            company_name=new_watchlist_stock.name,
            ticker=new_watchlist_stock.ticker,
            new_strengths=strength,
            new_weaknesses=weakness,
            new_content=new_content
        )

        self.update_strength_weakness_wiki_page_of_watchlist_stock(
            watchlist_stock_obj=new_watchlist_stock,
            new_strength=new_strengths,
            new_weakness=new_weakness,
            new_wiki_page=new_wiki_page
        )




    def get_watch_list_stock_with_id(self, id:int) -> StockSummary:
        return self.db.query(StockSummary).filter(StockSummary.id == id).first()

    def get_of_current_watchlist_stock_strengths_weakness_wiki_page(self, user_id: UUID, ticker: str):
        current_stock = self.get_current_stock_of_user(user_id, ticker)
        return (current_stock.strength,
                current_stock.weakness,
                current_stock.wiki_page) if current_stock else  "", "", ""


    def get_of_current_watchlist_stock_strengths_weakness_wiki_page_with_id(self,watchlist_stock_id: int ):
        current_stock = self.get_watch_list_stock_with_id(watchlist_stock_id)
        return (
            current_stock.strength if current_stock else "",
            current_stock.weakness if current_stock else "",
            current_stock.wiki_page if current_stock else ""
        )

    def get_watchlist_stock_id_by_ticker(self, ticker: str) -> int:
        return (self.db.query(StockSummary).filter(StockSummary.ticker == ticker).first().id
            if self.db.query(StockSummary).filter(StockSummary.ticker == ticker).first() else 0)

    def update_strength_weakness_wiki_page_of_watchlist_stock(self,watchlist_stock_obj: StockSummary,new_strength: str, new_weakness: str, new_wiki_page: str):
        watchlist_stock_obj.strength = new_strength
        watchlist_stock_obj.weakness = new_weakness
        watchlist_stock_obj.wiki_page = new_wiki_page
        self.db.commit()
        self.db.refresh(watchlist_stock_obj)