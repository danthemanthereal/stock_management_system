from sqlalchemy import Column, Integer, String, Boolean
from .db import Base

class StockSummary(Base):
    __tablename__ = "stock_summary"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,unique=True, index=True)
    strength = Column(String, index=True)
    weakness = Column(String, index=True)

class FinancialMetric(Base):
    __tablename__ = "financial_metric"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    should_rise = Column(Boolean, index=False)
    reference_value = Column(Integer, index=False)
    unit = Column(String, index=False)


