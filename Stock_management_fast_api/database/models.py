from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from .db import Base

branch_profile_metric_link = Table(
    "branch_profile_metric_link",
    Base.metadata,
    Column(
        "profile_id",
        Integer,
        ForeignKey(
            "financial_metric_branch_profile.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "metric_id",
        Integer,
        ForeignKey("financial_metric.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


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
    is_active = Column(Boolean, index=False, default=True)
    category_id = Column(Integer, ForeignKey("financial_metric_category.id"))
    category_rel = relationship("FinancialMetricCategory", back_populates="metrics")
    branch_profiles = relationship(
        "FinancialMetricBranchProfile",
        secondary=branch_profile_metric_link,
        back_populates="metrics",
    )


class FinancialMetricBranchProfile(Base):
    __tablename__ = "financial_metric_branch_profile"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    metrics = relationship(
        "FinancialMetric",
        secondary=branch_profile_metric_link,
        back_populates="branch_profiles",
    )

class FinancialMetricCategory(Base):
    __tablename__ = "financial_metric_category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    metrics = relationship("FinancialMetric", back_populates="category_rel")