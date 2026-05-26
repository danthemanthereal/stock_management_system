import uuid
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from src.database.models import IndustryProfile, ProfileMetricConfiguration, User, FinancialMetric
from src.financial_metric_analysis_component.schema import FinancialMetricOverview
from src.financial_metric_analysis_component.financial_metric_analysis import \
    FinancialMetricEvaluator
from src.financial_metric_analysis_component.financial_metric_analysis import \
    ActiveFinancialMetricComponent


class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def get_available_metrics(self) -> List[FinancialMetric]:
        return self.db.query(FinancialMetric).order_by(FinancialMetric.name).all()

    def get_financial_metric_by_id(self, financial_metric_id: int) -> FinancialMetric:
        return self.db.query(FinancialMetric).filter(FinancialMetric.id == financial_metric_id).first()



    def get_id_of_current_metric_by_name(self, metric_name: str) -> int:
        return self.db.query(FinancialMetric).filter(FinancialMetric.name == metric_name).first().id if self.db.query(FinancialMetric).filter(FinancialMetric.name == metric_name).first() else 0

    def get_name_of_current_metric_name_by_id(self, metric_id: int) -> str:
        return self.db.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first().id if self.db.query(FinancialMetric).filter(FinancialMetric.name == metric_id).first() else ""

    def get_evaluation_of_over_all_reference_value_development(self, company_name: str):
        get_active_metrics_of_template_component = ActiveFinancialMetricComponent()
        active_financial_metrics = get_active_metrics_of_template_component