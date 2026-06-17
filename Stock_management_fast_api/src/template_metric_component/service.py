import uuid
from collections import defaultdict
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import and_, select, delete
from sqlalchemy.orm import  joinedload
from src.database.models import ProfileMetricConfiguration, IndustryProfile, FinancialMetric
from src.financial_metric_analysis_component.schema import FinancialMetricOverview


class TemplateMetricService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_template_metric_configuration(self, config_id, new_reference_value: int, should_rise: bool, is_active: bool):
        try:
            result = await self.db.execute(
                select(ProfileMetricConfiguration).where(ProfileMetricConfiguration.id == config_id)
            )
            current_config = result.scalars().first()

            if current_config:
                current_config.should_rise = should_rise
                current_config.is_active = is_active
                current_config.reference_value = new_reference_value
                await self.db.commit()
                await self.db.refresh(current_config)
                return True
            return False
        except Exception as e:
            print(e)
            return False


    async def get_config_by_metric_and_template_id(self, metric_id: int, template_id: int):
        result = await self.db.execute(
            select(ProfileMetricConfiguration).where(
                ProfileMetricConfiguration.metric_id == metric_id,
                ProfileMetricConfiguration.profile_id == template_id
            )
        )
        return result.scalars().first()

    async def delete_metrics_of_current_template(self, template_id: int, metric_ids:list[int]):
        try:

            config_to_delete = (
                delete(ProfileMetricConfiguration)
                .where(
                    ProfileMetricConfiguration.profile_id == template_id,
                    ProfileMetricConfiguration.metric_id.in_(metric_ids)
                )
            )
            await self.db.execute(config_to_delete)
            await self.db.commit()
            return True


        except Exception as e:
            print(e)
            return False

    async def add_metric_to_profile(self, profile_id: int, metric_id: int,
                              reference_value: int, should_rise: bool,
                              user_id: uuid.UUID):
        result = await self.db.execute(
            select(IndustryProfile).where(
                IndustryProfile.id == profile_id,
                IndustryProfile.user_id == str(user_id)
            )
        )
        profile = result.scalars().first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profil nicht gefunden")

        result = await self.db.execute(
            select(ProfileMetricConfiguration).where(
                ProfileMetricConfiguration.profile_id == profile_id,
                ProfileMetricConfiguration.metric_id == metric_id
            )
        )
        existing = result.scalars().first()
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
        await self.db.commit()
        await self.db.refresh(config)

    async def get_all_financial_metrics_of_last_selected_template_per_category(self, template_id: int) -> Dict[str,list[FinancialMetricOverview]]:
        stmt = (
            select(ProfileMetricConfiguration)
            .options(
                joinedload(ProfileMetricConfiguration.metric)
                .joinedload(FinancialMetric.category_rel)
            )
            .where(ProfileMetricConfiguration.profile_id == template_id)
        )
        result = await self.db.execute(stmt)
        configs = result.scalars().all()

        financial_metrics_overviews_per_category = defaultdict(list)
        for cfg in configs:
            print("cfg")
            print(cfg.metric)
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


    async def check_if_current_user_activated_this_metric_in_current_template(self,
                                                                        current_template_id: int,
                                                                        financial_metric_id: int) -> bool:
        result = await self.db.execute(
            select(ProfileMetricConfiguration).where(
                ProfileMetricConfiguration.profile_id == current_template_id,
                ProfileMetricConfiguration.metric_id == financial_metric_id
            )
        )
        current_user_config = result.scalars().first()
        if not current_user_config:
            return False

        return current_user_config.is_active is True

    async def get_financial_metric_config_and_financial_metric_objects(self,
                                                                 financial_metric_name: str,
                                                                 template_id: int
                                                                 ):

        stmt = (
            select(ProfileMetricConfiguration, FinancialMetric)
            .join(FinancialMetric, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
            .where(
                and_(
                    FinancialMetric.name == financial_metric_name,
                    ProfileMetricConfiguration.profile_id == template_id,
                    ProfileMetricConfiguration.is_active == True
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.first()

    async def get_active_metric_names_of_last_selected_template(self, last_selected_template_id: int)-> list[str]:
        stmt = (
            select(FinancialMetric.name)
            .join(ProfileMetricConfiguration, FinancialMetric.id == ProfileMetricConfiguration.metric_id)
            .where(
                ProfileMetricConfiguration.profile_id == last_selected_template_id,
                ProfileMetricConfiguration.is_active == True
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


