from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import StockSummary


class WatchlistStockService:
    def __init__(self, db: Session):
        self.db = db

    def get_watchlist_stocks_of_current_user(self, current_user_id: UUID):
        return self.db.query(StockSummary).filter(StockSummary.is_on_watch_list == True,
                                                             StockSummary.user_id == str(current_user_id)).all()

    def delete_watchlist_stocks_of_current_user(self, current_user_id: UUID, watchlist_stock_names: list[str]):

        self.db.query(StockSummary) \
            .filter(
            StockSummary.name.in_(watchlist_stock_names),
            StockSummary.user_id == str(current_user_id)
        ) \
            .delete(synchronize_session=False)
        self.db.commit()
        self.db.flush()

    def deactivate_current_stock_on_watchlist(self, current_user_id: UUID, stock_name: str):
        current_stock = self.db.query(StockSummary).filter(StockSummary.name == stock_name,
                                                      StockSummary.user_id == str(current_user_id)).first()
        current_stock.is_on_watch_list = False
        self.db.commit()

    def check_if_user_has_stock_already_in_watchlist(self, current_user_id: UUID, stock_name: str):
        return self.db.query(StockSummary).filter(StockSummary.name == stock_name,StockSummary.user_id == str(current_user_id)).first() is not None

    def get_current_stock_of_user(self, current_user_id: UUID, stock_name: str)->StockSummary:
        return self.db.query(StockSummary).filter(StockSummary.name == stock_name,
                                                  StockSummary.user_id == str(current_user_id)).first()

    def add_to_current_user_to__watchlist(self, name: str, strength: str, weakness: str, user_id: UUID):
        new_watchlist_stock = StockSummary(
            name=name,
            strength=strength,
            weakness=weakness,
            user_id=str(user_id),
            is_on_watch_list=True
        )
        self.db.add(new_watchlist_stock)
        self.db.commit()
        self.db.refresh(new_watchlist_stock)