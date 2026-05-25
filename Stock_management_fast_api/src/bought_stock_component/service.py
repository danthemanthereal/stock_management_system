from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import BoughtStock




class BoughtStockService:
    def __init__(self, db: Session):
        self.db = db



    def get_bought_stocks_of_current_user(self, current_user_id: str) -> List[BoughtStock]:
        return self.db.query(BoughtStock).filter(BoughtStock.user_id == current_user_id).order_by(
            BoughtStock.ticker).all()

    def create_new_stock_of_current_user(self, name:str, ticker:str,
                                         bought_price:float, amount: float,
                                         current_user_id:UUID):

        new_stock = BoughtStock(
            name=name.strip(),
            ticker=ticker.strip().upper(),
            bought_price=bought_price,
            amount=amount,
            user_id=str(current_user_id)
        )
        self.db.add(new_stock)
        self.db.commit()

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