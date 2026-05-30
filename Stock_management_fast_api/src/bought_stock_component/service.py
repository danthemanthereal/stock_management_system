from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import BoughtStock
from src.bought_stock_component.schema import BoughtStockRequest
from src.watchlist_component.service import WatchlistStockService

from src.ticker_stock_component.ticker_stock import TickerStock

from src.kaparthies_llm_wiki_component.llm_wiki import LLMWiki


class BoughtStockService:
    def __init__(self, db: Session):
        self.db = db



    def get_bought_stocks_of_current_user(self, current_user_id: str) -> List[BoughtStock]:
        return self.db.query(BoughtStock).filter(BoughtStock.user_id == current_user_id).order_by(
            BoughtStock.ticker).all()

    def add_stock_to_current_user(self, name:str, ticker:str,
                                         bought_price:float, amount: float,
                                         current_user_id:UUID, strengths, weakness, wiki_page):
        get_ticker_component = TickerStock()
        ticker = get_ticker_component.get_ticker_of_a_stock(name)
        if self.user_already_bought_stock(current_user_id=current_user_id, ticker=ticker):
            llm_wiki = LLMWiki(self.db, "openai/gpt-oss-120b")

            current_stock = self.get_of_current_user_stock_by_name(current_user_id=current_user_id, ticker=ticker)
            current_stock.amount += amount

            (
                new_combined_strengths,
                new_combined_weakness,
                new_combined_wiki
            ) =  llm_wiki.ingest(
                watch_list_stock_id=None,
                bought_stock_id=current_stock.id,
                company_name=name,
                ticker=ticker,
                new_strengths=strengths,
                new_weaknesses=weakness,
                new_content=""
            )


            self.update_strength_weakness_wiki_page_of_stock(
                bought_stock_obj=current_stock,
                new_strength=new_combined_strengths,
                new_weakness=new_combined_weakness,
                new_wiki_page=new_combined_wiki
            )

        else:
            new_stock = BoughtStock(
            name=name.strip(),
            ticker=ticker,
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

        get_ticker_component = TickerStock()

        ticker = get_ticker_component.get_ticker_of_a_stock(stock_data.name)


        try:
            if self.user_already_bought_stock(current_user_id=current_user_id, ticker=ticker):

                pass

            else:
                db_bought_stock = BoughtStock(
                    name=stock_data.name,
                    ticker=ticker,
                    amount=stock_data.amount,
                    bought_price=stock_data.bought_price,
                    user_id=str(current_user_id),
                    strengths="",
                    weaknesses="",
                    wiki_page="",
                )
                self.db.add(db_bought_stock)

                self.db.commit()
                self.db.refresh(db_bought_stock)


            watchlist_service = WatchlistStockService(self.db)
            watchlist_service.deactivate_current_stock_on_watchlist(current_user_id,ticker)
            return {"status": "success", "message": "Aktie erfolgreich eingebucht", "data": db_bought_stock}
        except Exception as e:
            self.db.rollback()
            return {}

    def user_already_bought_stock(self, current_user_id:UUID, ticker)->bool:
        return self.db.query(BoughtStock).filter(BoughtStock.user_id == str(current_user_id),
                                                 BoughtStock.ticker ==ticker ).first() is not None


    def get_of_current_user_stock_by_name(self, current_user_id:UUID, ticker)->BoughtStock:
        return self.db.query(BoughtStock).filter(BoughtStock.user_id == str(current_user_id),
                                                 BoughtStock.ticker ==ticker ).first()

    def get_bought_stock_by_id(self, id: int)->BoughtStock:
        return self.db.query(BoughtStock).filter(BoughtStock.id == id).first()


    def get_bought_stock_strengths_weakness_wiki_page_with_id(self, bought_stock_id: int):
        current_bought_stock = self.get_bought_stock_by_id(bought_stock_id)
        return (
            current_bought_stock.strengths if current_bought_stock else "",
            current_bought_stock.weaknesses if current_bought_stock else "",
            current_bought_stock.wiki_page if current_bought_stock else ""
        )

    def update_strength_weakness_wiki_page_of_stock(self,bought_stock_obj: BoughtStock,
                                                    new_strength: str,
                                                    new_weakness: str,
                                                    new_wiki_page: str):
        bought_stock_obj.strengths = new_strength
        bought_stock_obj.weaknesses = new_weakness
        bought_stock_obj.wiki_page = new_wiki_page
        self.db.commit()
        self.db.refresh(bought_stock_obj)