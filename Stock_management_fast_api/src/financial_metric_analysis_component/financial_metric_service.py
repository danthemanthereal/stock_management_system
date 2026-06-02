import uuid
from typing import List
from sqlalchemy.orm import Session
from src.database.models import  FinancialMetric
from src.financial_metric_analysis_component.financial_metric_analysis import \
    ActiveFinancialMetricComponent

import os
from dotenv import load_dotenv
from src.financial_metric_analysis_component.financial_metric_evaluator import FinancialMetricEvaluator

load_dotenv()


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

    def get_evaluation_of_over_all_reference_value_development(self,
                                                               company_name: str,
                                                               current_user_id: uuid.UUID, ):
        get_active_metrics_of_template_component = ActiveFinancialMetricComponent(
            db=self.db,
            company_name=company_name,
            fmp_api_key=os.getenv("FMP_API_KEY"),
            alpha_vantage_api_key=os.getenv("ALPHA_VENTAGE_API_KEY"),
        )
        metrics_of_current_user_template = get_active_metrics_of_template_component.get_total_financial_metrics_of_current_template(current_user_id)
        metric_evaluator = FinancialMetricEvaluator(self.db)
        return metric_evaluator.get_satisfied_unsatisfied_by_category_and_summary(metrics_of_current_user_template,
                                                                                  current_user_id)