import uuid
from collections import defaultdict
from typing import Dict

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from src.database.models import ProfileMetricConfiguration, IndustryProfile, FinancialMetric
from src.financial_metric_analysis_component.schema import FinancialMetricOverview


class TemplateMetricService:
    def __init__(self, db: Session):
        self.db = db


    def update_template_metric_configuration(self, config_id, new_reference_value: int, should_rise: bool, is_active: bool):
        try:
            current_config = self.db.query(ProfileMetricConfiguration).filter(ProfileMetricConfiguration.id == config_id).first()

            if current_config:
                current_config.should_rise = should_rise
                current_config.is_active = is_active
                current_config.reference_value = new_reference_value
                self.db.commit()
                self.db.refresh(current_config)
                return True
            return False
        except Exception as e:
            print(e)
            return False


    def get_config_by_metric_and_template_id(self, metric_id: int, template_id: int):
        return self.db.query(ProfileMetricConfiguration).filter(
            ProfileMetricConfiguration.metric_id == metric_id,
            ProfileMetricConfiguration.profile_id == template_id
        ).first()

    def delete_metrics_of_current_template(self, template_id: int, metric_ids:list[int]):
        try:

            (self.db.query(ProfileMetricConfiguration)
                .filter(
                    ProfileMetricConfiguration.profile_id == template_id,
                    ProfileMetricConfiguration.metric_id.in_(metric_ids)
                )
                .delete(synchronize_session='fetch')
                )
            self.db.commit()
            self.db.refresh()
            return True


        except Exception as e:
            print(e)
            return False

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


    def check_if_current_user_activated_this_metric_in_current_template(self,
                                                                        current_template_id: int,
                                                                        financial_metric_id: int) -> bool:
        current_user_config = self.db.query(ProfileMetricConfiguration).filter(
            ProfileMetricConfiguration.profile_id == current_template_id,
            ProfileMetricConfiguration.metric_id == financial_metric_id
        )
        if not current_user_config:
            return False

        return current_user_config.is_active is True

    def get_financial_metric_config_and_financial_metric_objects(self,
                                                                 financial_metric_name: str,
                                                                 template_id: int
                                                                 ):
        return (self.db.query(ProfileMetricConfiguration, FinancialMetric)
                .join(FinancialMetric, ProfileMetricConfiguration.metric_id == FinancialMetric.id)).filter(
                and_(
                    FinancialMetric.name == financial_metric_name,
                    ProfileMetricConfiguration.profile_id == template_id,
                    ProfileMetricConfiguration.is_active == True
                )
            ).first()



