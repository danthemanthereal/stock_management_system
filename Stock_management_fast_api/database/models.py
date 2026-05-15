from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
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
    is_active = Column(Boolean, index=False, default=True)
    category_id = Column(Integer, ForeignKey("financial_metric_category.id"))
    category_rel = relationship("FinancialMetricCategory", back_populates="metrics")
    profile_configs = relationship("ProfileMetricConfiguration", back_populates="metric")

    @property
    def category_name(self) -> str:
        if self.category_id is None:
            return ""
        rel = self.category_rel
        if rel is None:
            return ""
        return (rel.name or "").strip()


class FinancialMetricCategory(Base):
    __tablename__ = "financial_metric_category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    metrics = relationship("FinancialMetric", back_populates="category_rel")


class IndustryProfile(Base):

    __tablename__ = "industry_profile"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    metric_configs = relationship("ProfileMetricConfiguration", back_populates="profile", cascade="all, delete-orphan")

class ProfileMetricConfiguration(Base):

    __tablename__ = "profile_metric_configuration"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("industry_profile.id"), nullable=False)
    metric_id = Column(Integer, ForeignKey("financial_metric.id"), nullable=False)

    should_rise = Column(Boolean)
    reference_value = Column(Integer)
    is_active = Column(Boolean, default=True)

    profile = relationship("IndustryProfile", back_populates="metric_configs")
    metric = relationship("FinancialMetric", back_populates="profile_configs")

    __table_args__ = (UniqueConstraint('profile_id', 'metric_id', name='_profile_metric_uc'),)
