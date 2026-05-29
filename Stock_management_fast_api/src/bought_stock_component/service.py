from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import BoughtStock
from src.bought_stock_component.schema import BoughtStockRequest
from src.watchlist_component.service import WatchlistStockService


class BoughtStockService:
    def __init__(self, db: Session):
        self.db = db



    def get_bought_stocks_of_current_user(self, current_user_id: str) -> List[BoughtStock]:
        return self.db.query(BoughtStock).filter(BoughtStock.user_id == current_user_id).order_by(
            BoughtStock.ticker).all()

    def add_stock_to_current_user(self, name:str, ticker:str,
                                         bought_price:float, amount: float,
                                         current_user_id:UUID, strengths, weakness, wiki_page):

        if self.user_already_bought_stock(current_user_id=current_user_id, stock_name=name):
            current_stock = self.get_of_current_user_stock_by_name(current_user_id=current_user_id, stock_name=name)
            current_stock.amount += amount
            # TODO hier noch die zusammenfügen machen
            self.db.commit()

        else:
            new_stock = BoughtStock(
            name=name.strip(),
            ticker=ticker.strip().upper(),
            bought_price=bought_price,
            amount=amount,
            user_id=str(current_user_id),
            strengths=strengths,
            weaknesses=weakness,
            wiki_page=wiki_page,
            )
            self.db.add(new_stock)
            self.db.commit()
            self.db.refresh(new_stock)

    def update_bought_stocks_of_current_user(self, current_user_id:UUID,
                                             delete_ids: str,
                                             update_triplets: str):
        try:
            if delete_ids:
                id_list_to_delete = [int(stock_id) for stock_id in delete_ids.split(",") if stock_id.strip()]
                if id_list_to_delete:
                    self.db.query(BoughtStock).filter(BoughtStock.id.in_(id_list_to_delete),
                                                 BoughtStock.user_id == str(current_user_id)).delete(
                        synchronize_session=False)

            if update_triplets:
                triplet_list = [t.strip() for t in update_triplets.split(",") if t.strip()]

                for triplet in triplet_list:
                    if "|" in triplet:
                        parts = triplet.split("|")
                        if len(parts) == 3:
                            stock_id = int(parts[0])
                            new_price = float(parts[1])
                            new_amount = float(parts[2])

                            stock_entry = self.db.query(BoughtStock).filter(BoughtStock.id == stock_id,
                                                                       BoughtStock.user_id == str(current_user_id)).first()
                            if stock_entry:
                                stock_entry.bought_price = new_price
                                stock_entry.amount = new_amount

            self.db.commit()
            self.db.flush()
        except Exception:
            self.db.rollback()


    def create_bought_stock(self,stock_data: BoughtStockRequest,
                            current_user_id: UUID):


        generated_ticker = stock_data.name.replace(" ", "").upper()[:5]

        db_bought_stock = BoughtStock(
            name=stock_data.name,
            ticker=generated_ticker,
            amount=stock_data.amount,
            bought_price=stock_data.bought_price,
            user_id=str(current_user_id)
        )

        try:
            self.db.add(db_bought_stock)

            self.db.commit()
            self.db.refresh(db_bought_stock)
            watchlist_service = WatchlistStockService(self.db)
            watchlist_service.deactivate_current_stock_on_watchlist(current_user_id,stock_data.name)
            return {"status": "success", "message": "Aktie erfolgreich eingebucht", "data": db_bought_stock}
        except Exception as e:
            self.db.rollback()
            return {}

    def user_already_bought_stock(self, current_user_id:UUID, stock_name)->bool:
        return self.db.query(BoughtStock).filter(BoughtStock.user_id == str(current_user_id),
                                                 BoughtStock.name ==stock_name ).first() is not None


    def get_of_current_user_stock_by_name(self, current_user_id:UUID, stock_name)->BoughtStock:
        return self.db.query(BoughtStock).filter(BoughtStock.user_id == str(current_user_id),
                                                 BoughtStock.name ==stock_name ).first()

    def get_bought_stock_by_id(self, id: int)->BoughtStock:
        return self.db.query(BoughtStock).filter(BoughtStock.id == id).first()