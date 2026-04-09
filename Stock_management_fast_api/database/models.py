from sqlalchemy import Column, Integer, String
from .db import Base

class StockSummary(Base):
    __tablename__ = "stock_summary"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,unique=True, index=True)
    strength = Column(String, index=True)
    weakness = Column(String, index=True)
