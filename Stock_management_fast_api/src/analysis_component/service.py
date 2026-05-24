from typing import List
from sqlalchemy.orm import Session
from src.database.models import FinancialMetric, User, IndustryProfile
from src.database.db import get_db



def get_available_metrics(db: Session) -> List[FinancialMetric]:
    return db.query(FinancialMetric).order_by(FinancialMetric.name).all()


