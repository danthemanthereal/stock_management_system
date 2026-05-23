import uuid

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Float, DateTime, UUID
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime, timezone
from sqlalchemy.sql import func
from pydantic import BaseModel as PydanticBase, Field
from uuid import uuid4
from datetime import datetime


class StockSummary(Base):
    __tablename__ = "stock_summary"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String,unique=True, index=True)
    strength = Column(String, index=True)
    weakness = Column(String, index=True)
    is_on_watch_list = Column(Boolean)

    user = relationship("User", back_populates="stock_summary")
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_stock_ticker"),  # sicherer
    )


class FinancialMetric(Base):
    __tablename__ = "financial_metric"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    unit = Column(String, index=False)
    category_id = Column(Integer, ForeignKey("financial_metric_category.id"))
    category_rel = relationship("FinancialMetricCategory", back_populates="metrics")
    profile_configs = relationship("ProfileMetricConfiguration", back_populates="metric")
    display_name_reference = Column(String)

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
    name = Column(String)

    metric_configs = relationship("ProfileMetricConfiguration", back_populates="profile", cascade="all, delete-orphan")
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="industry_profiles")
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_stock_ticker"),  # sicherer
    )


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


class BoughtStock(Base):
    __tablename__ = "bought_stock"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, unique=True, index=True)
    ticker = Column(String, unique=True, index=True)
    bought_price = Column(Float)
    amount = Column(Float)

    user = relationship("User", back_populates="bought_stocks")
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_stock_ticker"),  # sicherer
    )


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_name = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now())

    bought_stocks = relationship("BoughtStock", back_populates="user", cascade="all, delete-orphan")
    industry_profiles = relationship("IndustryProfile", back_populates="user", cascade="all, delete-orphan")
    stock_summary = relationship("StockSummary", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_token"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token_hash = Column(String, nullable=False, unique=True, index=True)

    expires_at = Column(DateTime(timezone=True), nullable=False)

    revoked = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("User", backref="refresh_tokens")


class BaseModel(PydanticBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)