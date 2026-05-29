from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import StockSummary


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

    def add_to_current_user_to__watchlist(self, name: str, ticker: str,  strength: str, weakness: str, user_id: UUID):

        if self.check_if_user_has_stock_already_in_watchlist(user_id, ticker):
            current_stock = self.get_current_stock_of_user(user_id, ticker)
            # TODO with karpaty summ up
            self.db.commit()

            return
        new_watchlist_stock = StockSummary(
            name=name,
            ticker=ticker,
            strength=strength,
            weakness=weakness,
            user_id=str(user_id),
            is_on_watch_list=True
        )
        self.db.add(new_watchlist_stock)
        self.db.commit()
        self.db.refresh(new_watchlist_stock)


    def get_watch_list_stock_with_id(self, id:int) -> StockSummary:
        return self.db.query(StockSummary).filter(StockSummary.id == id).first()