from typing import List

from pydantic import BaseModel


class DeleteWatchListStockRequest(BaseModel):
    companies: List[str]

class WatchlistRequest(BaseModel):
    company_name: str
    strength: str
    weakness: str
    url: str
    yt_url: str