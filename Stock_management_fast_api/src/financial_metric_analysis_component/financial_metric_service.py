import uuid
from collections import defaultdict
from typing import  Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from src.database.models import IndustryProfile, ProfileMetricConfiguration, User, FinancialMetric
from src.financial_metric_analysis_component.schema import FinancialMetricOverview




class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def add_metric_to_profile(self, profile_id: int, metric_id: int,
                              reference_value: int, should_rise: bool,
                              user_id: uuid.UUID):
        profile = self.db.query(IndustryProfile).filter(
            IndustryProfile.id == profile_id,
            IndustryProfile.user_id == str(user_id)
        ).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profil nicht gefunden")

        existing = self.db.query(ProfileMetricConfiguration).filter(
            ProfileMetricConfiguration.profile_id == profile_id,
            ProfileMetricConfiguration.metric_id == metric_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Kennzahl bereits im Profil vorhanden")

        config = ProfileMetricConfiguration(
            profile_id=profile_id,
            metric_id=metric_id,
            reference_value=reference_value,
            should_rise=should_rise,
            is_active=True
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)

    def get_all_financial_metrics_of_last_selected_template_per_category(self, template_id: int) -> Dict[str,list[FinancialMetricOverview]]:
        configs = (
            self.db.query(ProfileMetricConfiguration)
            .options(
                joinedload(ProfileMetricConfiguration.metric)
                .joinedload(FinancialMetric.category_rel)
            )
            .filter(ProfileMetricConfiguration.profile_id == template_id)
            .all()
        )

        financial_metrics_overviews_per_category = defaultdict(list)
        for cfg in configs:
            metric = cfg.metric
            overview = FinancialMetricOverview(
                config_id=cfg.id,
                metric_id=metric.id,
                display_name=metric.display_name_reference,
                category=metric.category_rel.name,
                reference_value=cfg.reference_value,
                unit=metric.unit,
                should_rise=cfg.should_rise,
                is_active=cfg.is_active,
            )
            financial_metrics_overviews_per_category[metric.category_rel.name].append(overview)

        return financial_metrics_overviews_per_category

    
