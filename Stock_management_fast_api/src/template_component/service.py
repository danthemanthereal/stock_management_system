import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import IndustryProfile, ProfileMetricConfiguration, User




class TemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_template_from_active_metrics(
        self,
        user_id: uuid.UUID,
        new_profile_name: str,
        triplets_str: Optional[str]
    ) -> int:

        new_template = IndustryProfile(
            name=new_profile_name,
            user_id=str(user_id)
        )
        self.db.add(new_template)
        await self.db.commit()
        await self.db.refresh(new_template)

        if triplets_str:
            for item in triplets_str.split(","):
                parts = item.strip().split("|")
                if len(parts) < 4:
                    continue
                metric_id = int(parts[0])
                reference_value = float(parts[1])

                should_rise = parts[3].lower() == "true"

                new_cfg = ProfileMetricConfiguration(
                    profile_id=new_template.id,
                    metric_id=metric_id,
                    reference_value=reference_value,
                    should_rise=should_rise,
                    is_active=True
                )
                self.db.add(new_cfg)
                await self.db.commit()
                await self.db.refresh(new_cfg)

        await self.update_last_selected_template_id(new_template.id,user_id)
        return new_template.id

    async def get_last_selected_template_id_of_user(self, current_user_id: uuid.UUID) -> int:
        if not await self.check_if_user_already_has_template(current_user_id):
            over_all_user_template = IndustryProfile(
                name="Allgemein",
                user_id=str(current_user_id)
            )
            self.db.add(over_all_user_template)
            await self.db.commit()
            await self.db.refresh(over_all_user_template)
            return await self.set_to_current_user_his_first_template(current_user_id, over_all_user_template.id)

        return await self.get_last_selected_template_id_if_user(current_user_id)

    async def check_if_user_already_has_template(self, user_id: uuid.UUID) -> bool:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        return user is not None and user.last_selected_template_id is not None

    async def set_to_current_user_his_first_template(self, user_id: uuid.UUID, template_id: int) -> int:
        result = await self.db.execute(select(User).where(User.id == user_id))
        current_user = result.scalars().first()
        current_user.last_selected_template_id = template_id
        await self.db.commit()
        await self.db.refresh(current_user)
        return current_user.last_selected_template_id

    async def get_last_selected_template_id_if_user(self, current_user_id: uuid.UUID) -> int:
        result = await self.db.execute(select(User).where(User.id == current_user_id))
        user = result.scalars().first()
        return user.last_selected_template_id

    async def get_current_user_created_templates(
            self,
            user_id: uuid.UUID
    ) -> list[IndustryProfile]:
        stmt = select(IndustryProfile).where(
            IndustryProfile.user_id == str(user_id)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_last_selected_template_id(
            self,
            template_id: int,
            user_id: uuid.UUID
        ):
        stmt = select(User).where(User.id == user_id)

        result = await self.db.execute(stmt)
        current_user = result.scalar_one_or_none()

        current_user.last_selected_template_id = template_id

        await self.db.commit()
        await self.db.refresh(current_user)

    async def get_template_by_id(self, template_id: int) -> IndustryProfile:
        stmt = select(IndustryProfile).where(IndustryProfile.id == template_id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()