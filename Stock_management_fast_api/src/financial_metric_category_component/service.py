from typing import List

from sqlalchemy.orm import Session

from src.database.models import FinancialMetricCategory


class FinancialMetricCategoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_metric_categories(self):
        return self.db.query(FinancialMetricCategory).all()

