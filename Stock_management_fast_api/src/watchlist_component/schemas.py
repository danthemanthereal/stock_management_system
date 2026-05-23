from typing import List

from pydantic import BaseModel

class BoughtStockRequest(BaseModel):
    name: str
    amount: float
    bought_price: float

    class Config:
        from_attributes = True


class DeleteWatchListStockRequest(BaseModel):
    companies: List[str]

class WatchlistRequest(BaseModel):
    company_name: str
    strength: str
    weakness: str